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
from presion_arterial.hr_stability import estimate_hr

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

def infer(data):
    ts = np.asarray(data.get('timestamps', []), float)
    rgb = np.asarray(data.get('rgb', []), float)
    if ts.ndim != 1 or rgb.ndim != 2 or rgb.shape[1:] != (3,) or len(ts) != len(rgb) or len(ts) < 90 or len(ts) > 1500:
        raise ValueError('Se necesitan entre 90 y 1500 muestras RGB con marcas temporales')
    if not np.isfinite(ts).all() or not np.isfinite(rgb).all() or np.any(np.diff(ts) <= 0):
        raise ValueError('Tiempos y señales deben ser finitos y ordenados')
    elapsed = float(ts[-1] - ts[0])
    if elapsed < 7 or elapsed > 100:
        raise ValueError('Ventana temporal fuera de 7–100 segundos')
    fs_real = (len(ts)-1)/elapsed
    minimum_fps = 7.0 if LOW_FPS_MODE else 12.0
    if fs_real < minimum_fps or fs_real > 90:
        return {'status': 'no_evaluable', 'reason': f'Muestreo insuficiente/inusual ({fs_real:.1f} fps; mínimo {minimum_fps:.0f})', 'bpm': None, 'sbp': None, 'dbp': None, 'fps': round(fs_real,1)}
    # Resampling alone cannot recover dropped frames: reject severe time gaps.
    intervals = np.diff(ts)
    if np.max(intervals) > max(0.5, 4.0 * float(np.median(intervals))):
        return {'status': 'no_evaluable', 'reason': 'Captura interrumpida o irregular: hay saltos temporales grandes', 'bpm': None, 'sbp': None, 'dbp': None, 'fps': round(fs_real,1)}
    low_fps = fs_real < 12
    if low_fps and elapsed < 12:
        return {'status': 'no_evaluable', 'reason': 'Modo FPS bajo: se requieren al menos 12 segundos de señal', 'bpm': None, 'sbp': None, 'dbp': None, 'fps': round(fs_real,1)}
    fs = float(FS_MODEL)
    tgrid = np.arange(ts[0], ts[-1], 1/fs)
    # CHROM utiliza combinaciones de canales normalizados para reducir artefactos comunes.
    interp = np.column_stack([np.interp(tgrid, ts, rgb[:,j]) for j in range(3)])
    base = np.mean(interp, axis=0)
    if np.min(base) < 8 or np.max(base) > 248:
        return {'status':'no_evaluable','reason':'Iluminación insuficiente o saturación RGB','bpm':None,'sbp':None,'dbp':None}
    norm = interp/(base + 1e-9)-1
    X = 3*norm[:,0]-2*norm[:,1]
    Y = 1.5*norm[:,0]+norm[:,1]-1.5*norm[:,2]
    pulse = X - (np.std(X)/(np.std(Y)+1e-9))*Y
    sos = butter(3, [0.7,3.0], btype='bandpass', fs=fs, output='sos')
    pulse = sosfiltfilt(sos,pulse)
    pulse = (pulse - np.mean(pulse))/(np.std(pulse)+1e-9)
    # VitaSense-inspired approach: interpolated spectral peak and temporal agreement.
    # Requiring 18 s reduces harmonic switches but increases warm-up latency.
    hr = estimate_hr(pulse, fs)
    peak_frac = hr.peak_fraction
    if hr.bpm is None:
        return {'status':'no_evaluable', 'reason':hr.reason, 'bpm':None,
                'sbp':None, 'dbp':None, 'peak_fraction':round(peak_frac,3),
                'snr_db':round(hr.snr_db,2) if math.isfinite(hr.snr_db) else None,
                'agreement_bpm':round(hr.agreement_bpm,1) if hr.agreement_bpm is not None else None,
                'fps':round(fs_real,1)}
    bpm = hr.bpm
    caution = ('LOW FPS MODE (experimental): ~8 FPS; BP inference is NOT validated and can be unreliable. ' if low_fps else '')
    result={'status':'experimental_low_fps' if low_fps else 'experimental','reason':caution+'Estimación rPPG no validada; no utilizar clínicamente',
        'bpm':round(bpm,1),'peak_fraction':round(peak_frac,3),'fps':round(fs_real,1),
        'seconds':round(elapsed,1),'snr_db':round(hr.snr_db,2),
        'agreement_bpm':round(hr.agreement_bpm,1), 'low_fps':low_fps,'sbp':None,'dbp':None,'bp_status':MODEL_STATUS,
        'waveform':np.round(pulse[-min(len(pulse),240):],3).tolist(), 'model_loaded':MODEL is not None}
    if MODEL is not None:
        try:
            sbp,dbp=MODEL.predict_pulse(pulse[-int(7*fs):], fs)
            # Nunca etiquetar como lectura real o usar reglas clínicas.
            if all(map(math.isfinite,(sbp,dbp))) and 30 < dbp < 180 and 50 < sbp < 280 and sbp > dbp:
                result.update(sbp=round(sbp,1),dbp=round(dbp,1),bp_status=('LOW FPS ~8: NO VALIDADO, ALTA INCERTIDUMBRE · ' if low_fps else '')+'DL experimental PPG→rPPG · NO ES UNA MEDICIÓN')
            else:
                result['bp_status']='La inferencia DL devolvió valores implausibles: se ocultaron'
        except Exception as e:
            result['bp_status']=f'Fallo de inferencia experimental: {e}'
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
