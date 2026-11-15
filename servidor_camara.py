"""Servidor local para panel rPPG por webcam; PA solo con checkpoint externo experimental.
No diagnostica ni estima PA sin un modelo entrenado por separado.
"""
from __future__ import annotations
import argparse
import json
import math
import os
import threading
from urllib.parse import urlsplit, unquote
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import numpy as np
from scipy.signal import butter, sosfiltfilt
from presion_arterial.config import FS_MODEL
from presion_arterial.degrade import resample_to

ROOT = Path(__file__).resolve().parent
MODEL = None
MODEL_STATUS = 'Sin checkpoint real: PA no disponible'
FATIGUE = None
FATIGUE_STATUS = 'No se inició con --fatiguesense-root'
LOW_FPS_MODE = False
# Cap concurrent inference to prevent one public deployment from being overloaded.
INFERENCE_SLOTS = threading.BoundedSemaphore(value=2)
PUBLIC_ASSETS = frozenset({
    '/index.html', '/camara_dashboard.html', '/fatiga_respiracion.html',
    '/heamon_i18n.js', '/favicon.ico',
})

def _pulse_candidate(ts, rgb, fs):
    """Extrae BPM y calidad con el estimador adaptado de las ideas de VitaSense.

    Calcula CHROM (onda para el LSTM) y POS (candidato alternativo de BPM).
    El consenso entre regiones sigue siendo obligatorio: NO infiere valores sin señal.
    """
    from presion_arterial.vitasense_hr import estimate_region
    return estimate_region(ts, rgb, fs)


def infer(data):
    ts = np.asarray(data.get('timestamps', []), float)
    rgb = np.asarray(data.get('rgb', []), float)
    if ts.ndim != 1 or rgb.ndim != 2 or rgb.shape[1:] != (3,) or len(ts) != len(rgb) or not 90 <= len(ts) <= 1500:
        raise ValueError('Se necesitan 90–1500 muestras RGB con marcas temporales')
    if not np.isfinite(ts).all() or not np.isfinite(rgb).all() or np.any(np.diff(ts) <= 0):
        raise ValueError('Señales o tiempos no válidos')
    elapsed = float(ts[-1] - ts[0])
    if not 12.0 <= elapsed <= 100:
        return {'status':'calibrating','reason':'Calibrando: se requieren al menos 12 segundos continuos de señal útil','bpm':None,'sbp':None,'dbp':None}
    fps = (len(ts) - 1) / elapsed
    minimum = 7 if LOW_FPS_MODE else 12
    if fps < minimum or fps > 90:
        return {'status':'no_evaluable','reason':f'FPS insuficientes o anómalos: {fps:.1f}','bpm':None,'sbp':None,'dbp':None,'fps':round(fps,1)}
    intervals = np.diff(ts)
    if np.max(intervals) > max(0.5, 4 * float(np.median(intervals))):
        return {'status':'no_evaluable','reason':'Fotogramas discontinuos: recalibrando','bpm':None,'sbp':None,'dbp':None,'fps':round(fps,1)}
    # Opcionalmente tres señales independientes, conservando compatibilidad API.
    rois = data.get('rois') or {}
    if rois and (not isinstance(rois, dict) or len(rois)>3):
        raise ValueError('Regiones inválidas')
    traces = {'forehead': rgb}
    for name in ('left_cheek', 'right_cheek'):
        if name in rois:
            a=np.asarray(rois[name],float)
            if a.shape != rgb.shape or not np.isfinite(a).all():
                raise ValueError('Señal RGB por región inválida')
            traces[name]=a
    fs=float(FS_MODEL)
    candidates=[]
    for name, trace in traces.items():
        result=_pulse_candidate(ts,trace,fs)
        if result is not None:
            result['name']=name
            candidates.append(result)
    if len(traces) > 1:
        # Consenso: no basta con un pico espurio fuerte de una sola región.
        groups = [[c for c in candidates if abs(c['bpm']-anchor['bpm'])<=10] for anchor in candidates]
        agreed=max(groups,key=len) if groups else []
        if len(agreed) < 2:
            return {'status':'no_evaluable','reason':'Calibrando: frente y pómulos no concuerdan; revisa luz y movimiento','bpm':None,'sbp':None,'dbp':None,'fps':round(fps,1),'roi_count':len(candidates)}
    else:
        agreed=candidates
    if not agreed:
        return {'status':'no_evaluable','reason':'Señal pulsátil no fiable; mantente quieto e ilumina el rostro','bpm':None,'sbp':None,'dbp':None,'fps':round(fps,1)}
    weights=np.array([max(c['snr_db'],1.0) for c in agreed])
    candidate_bpm=float(np.average([c['bpm'] for c in agreed],weights=weights))
    # Preferimos la región con mejor señal para el LSTM; NO pasamos BPM suavizado.
    chosen=max(agreed,key=lambda c:c['snr_db']+10*c['peak_fraction'])
    pulse=chosen['pulse']
    low=fps<12
    result={'status':'experimental_low_fps' if low else 'experimental',
            'reason':'Consenso entre regiones; medición experimental no validada',
            'bpm':round(candidate_bpm,1),'peak_fraction':round(float(np.mean([c['peak_fraction'] for c in agreed])),3),
            'fps':round(fps,1),'seconds':round(elapsed,1),'roi_count':len(agreed),
            'snr_db':round(float(np.mean([c['snr_db'] for c in agreed])),1),
            'algorithm':chosen.get('algorithm','CHROM'),
            'low_fps':low,'sbp':None,'dbp':None,'bp_status':MODEL_STATUS,
            'waveform':np.round(pulse[-min(len(pulse),240):],3).tolist(), 'model_loaded':MODEL is not None}
    if MODEL is not None:
        try:
            sbp, dbp=MODEL.predict_pulse(pulse[-int(7*fs):], fs)
            if all(map(math.isfinite,(sbp,dbp))) and 30<dbp<180 and 50<sbp<280 and sbp>dbp:
                result.update(sbp=round(sbp,1),dbp=round(dbp,1),bp_status='DL experimental PPG→rPPG, SIN VALIDACIÓN CLÍNICA')
            else:
                result['bp_status']='Inferencia DL implausible: se oculta'
        except Exception as exc:
            result['bp_status']=f'Inferencia DL no disponible: {exc}'
    return result

class Handler(SimpleHTTPRequestHandler):
    """Serve only browser assets; do not expose Python, model files or datasets."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(ROOT), **kwargs)

    def end_headers(self):
        self.send_header('X-Content-Type-Options', 'nosniff')
        self.send_header('Referrer-Policy', 'no-referrer')
        self.send_header('Permissions-Policy', 'camera=(self), microphone=()')
        self.send_header('X-Frame-Options', 'SAMEORIGIN')
        super().end_headers()

    def do_GET(self):
        route = unquote(urlsplit(self.path).path)
        if route == '/api/health':
            self.reply({'status': 'ok'}, 200)
            return
        if route == '/api/fatigue-status':
            self.reply({'enabled': FATIGUE is not None, 'reason': FATIGUE_STATUS})
            return
        if route == '/':
            self.send_response(302)
            self.send_header('Location', '/index.html')
            self.end_headers()
            return
        if route not in PUBLIC_ASSETS:
            self.send_error(404, 'Not found')
            return
        return super().do_GET()

    def do_HEAD(self):
        route = unquote(urlsplit(self.path).path)
        if route not in PUBLIC_ASSETS:
            self.send_error(404, 'Not found')
            return
        return super().do_HEAD()

    def reply(self, answer, code=200):
        blob=json.dumps(answer,ensure_ascii=False).encode('utf-8')
        self.send_response(code)
        self.send_header('Content-Type','application/json; charset=utf-8')
        self.send_header('Cache-Control','no-store')
        self.send_header('Content-Length',str(len(blob)))
        self.end_headers()
        self.wfile.write(blob)

    def do_POST(self):
        # Prevent cross-origin form/API requests from other websites.
        origin = self.headers.get('Origin')
        if origin:
            origin_url = urlsplit(origin)
            host = self.headers.get('Host', '')
            if origin_url.scheme not in ('http', 'https') or origin_url.netloc.lower() != host.lower():
                return self.reply({'status': 'error', 'reason': 'Cross-origin request rejected'}, 403)
        route = urlsplit(self.path).path
        if route not in ('/api/estimate', '/api/fatigue-frame'):
            self.send_error(404)
            return
        if not INFERENCE_SLOTS.acquire(blocking=False):
            return self.reply({'status': 'busy', 'reason': 'Server busy; retry shortly'}, 503)
        try:
            if route == '/api/fatigue-frame':
                if FATIGUE is None:
                    return self.reply({'reason': FATIGUE_STATUS}, 503)
                try:
                    n=int(self.headers.get('Content-Length','0'))
                    if n<=100 or n>350000: raise ValueError('Fotograma JPEG demasiado grande o vacío')
                    if self.headers.get('Content-Type','').split(';')[0]!='image/jpeg':
                        raise ValueError('Se esperaba image/jpeg')
                    response=FATIGUE.process_jpeg(self.rfile.read(n))
                    return self.reply(response)
                except Exception as exc:
                    return self.reply({'reason':str(exc)},400)
            try:
                n=int(self.headers.get('Content-Length','0'))
                if n <= 0 or n > 200000:
                    raise ValueError('Solicitud demasiado grande o vacía')
                if self.headers.get('Content-Type','').split(';')[0].strip() != 'application/json':
                    raise ValueError('Se esperaba application/json')
                payload=json.loads(self.rfile.read(n))
                answer=infer(payload)
                code=200
            except Exception as exc:
                answer={'status':'error','reason':str(exc),'sbp':None,'dbp':None,'bpm':None}
                code=400
            return self.reply(answer,code)
        finally:
            INFERENCE_SLOTS.release()

def main():
    global MODEL, MODEL_STATUS, FATIGUE, FATIGUE_STATUS, LOW_FPS_MODE
    ap=argparse.ArgumentParser()
    ap.add_argument('--ckpt',help='Checkpoint PyTorch propio (formato .pt, NO compatible con .h5)')
    ap.add_argument('--fabian-model',help='Modelo real Keras .h5 de Schrumpf et al. (2021), investigación EXCLUSIVAMENTE')
    ap.add_argument('--host', default='127.0.0.1', help='Bind address; use 0.0.0.0 behind an HTTPS reverse proxy')
    ap.add_argument('--port',type=int,default=int(os.environ.get('PORT', '8765')))
    ap.add_argument('--low-fps',action='store_true',help='Permite ~7–12 FPS de forma experimental; NO valida BPM ni presión arterial')
    ap.add_argument('--fatiguesense-root',help='Ruta al repositorio original FatigueSense clonado (pesos reales se descargan)')
    ap.add_argument('--fatigue-fps',type=float,default=10.0,help='FPS objetivo del puente FatigueSense; predeterminado 10')
    args=ap.parse_args()
    LOW_FPS_MODE = args.low_fps
    if LOW_FPS_MODE:
        print('AVISO: modo 7–12 FPS experimental activado; no utilizar resultados para decisiones de salud.')
    if args.ckpt and args.fabian_model:
        ap.error('Elige uno: --ckpt o --fabian-model')
    if args.fabian_model:
        from presion_arterial.fabian_adapter import FabianBPModel
        MODEL=FabianBPModel(args.fabian_model)
        MODEL_STATUS='Schrumpf 2021: PPG de contacto sobre señal rPPG NO VALIDADA, SIN calibración'
        print(f'Checkpoint real cargado: {MODEL.name}; input={MODEL.input_shape}; output={MODEL.output_shape}')
    if args.ckpt:
        from presion_arterial.vitasense_adapter import DeepBPModel
        MODEL=DeepBPModel(args.ckpt)
        MODEL_STATUS='Checkpoint cargado; salida experimental SIN validación con webcam'
    if args.fatiguesense_root:
        try:
            from fatiguesense_bridge import FatigueSenseBridge
            FATIGUE=FatigueSenseBridge(args.fatiguesense_root,args.fatigue_fps)
            FATIGUE_STATUS='Modelos CNN, YOLO y BiGRU cargados'
            print('FatigueSense: modelos CNN, YOLO y BiGRU reales cargados.')
        except Exception as e:
            FATIGUE_STATUS='No se pudo cargar FatigueSense: '+str(e)
            print('ADVERTENCIA:',FATIGUE_STATUS)
    print(f'HEAMON listening on {args.host}:{args.port}; locally open http://127.0.0.1:{args.port}/index.html')
    print('PA: se transmiten RGB/tiempos. FatigueSense opcional: JPEG local de fotogramas reducidos.')
    ThreadingHTTPServer((args.host,args.port),Handler).serve_forever()

if __name__=='__main__': main()
