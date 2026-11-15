"""Adaptador de inferencia experimental de un checkpoint genuino .h5 de Schrumpf et al. (2021).
ATENCION: esos modelos se entrenaron con PPG de contacto, NO con esta webcam.
Remuestrear 30 FPS a 125 Hz no recupera detalles fisiológicos faltantes.
Solo demostración / investigación; NUNCA uso clínico ni decisión de seguridad.
"""
from pathlib import Path
import numpy as np

class FabianBPModel:
    def __init__(self, checkpoint):
        ck = Path(checkpoint)
        if not ck.is_file():
            raise FileNotFoundError(f"Checkpoint no encontrado: {ck}")
        try:
            import tensorflow as tf
        except ImportError as e:
            raise RuntimeError("TensorFlow no está instalado en este entorno: use requirements_dl.txt y un Python compatible") from e
        objs = {"ReLU": tf.keras.layers.ReLU}
        try:
            from kapre import STFT, Magnitude, MagnitudeToDecibel
            objs.update(STFT=STFT, Magnitude=Magnitude, MagnitudeToDecibel=MagnitudeToDecibel)
        except ImportError:
            # Modelo LSTM puede no requerir Kapre; las otras arquitecturas sí.
            pass
        try:
            self.model = tf.keras.models.load_model(str(ck), custom_objects=objs, compile=False)
        except Exception as e:
            raise RuntimeError("No se pudo cargar el archivo Keras legado de 2021. "
                               "Puede necesitar Python 3.8 + TensorFlow 2.4.1, o convertirlo con un entorno compatible. "
                               f"Detalle: {e}") from e
        self.name = ck.name
        self.input_shape = self.model.input_shape
        self.output_shape = self.model.output_shape
        self.self_test()

    def _input(self, wave):
        # Formato original: 7 s x 125 Hz = 875 puntos.
        a = np.asarray(wave, dtype=np.float32)
        if a.shape != (875,) or not np.isfinite(a).all():
            raise ValueError(f"Se requieren 875 muestras finitas (recibidas {a.shape})")
        # Entrada de una señal rPPG estandarizada. No equivale al preprocesamiento PPG original.
        dims = len(self.input_shape) if isinstance(self.input_shape, tuple) else 0
        if dims == 3:
            return a.reshape(1,875,1)
        if dims == 2:
            return a.reshape(1,875)
        raise ValueError(f"Forma de entrada del modelo no soportada: {self.input_shape}")

    def self_test(self):
        if isinstance(self.input_shape, list):
            raise ValueError('Checkpoint con varias entradas: revisar arquitectura')
        shape = tuple(self.input_shape)
        if len(shape)==3 and shape[1:] != (875,1):
            raise ValueError(f'El modelo espera {shape}, no (None,875,1)')
        if len(shape)==2 and shape[1] != 875:
            raise ValueError(f'El modelo espera {shape}, no (None,875)')

    def predict_pulse(self, pulse, fs):
        # Únicamente después de verificar un mínimo de 7 s de señal observada.
        x = np.asarray(pulse, dtype=np.float64)
        if len(x) < 2 or (len(x)-1)/fs < 6.9:
            raise ValueError('Insuficiente señal observada: se requieren al menos 7 s')
        duration = len(x)/fs
        if duration < 7:
            raise ValueError(f'El modelo requiere 7 s, recibió {duration:.2f} s')
        xx=np.interp(np.linspace(duration-7, duration, 875, endpoint=False),
                     np.arange(len(x))/fs,x)
        xin=self._input(xx)
        pred=self.model.predict(xin, verbose=0)
        # El script original utiliza dos cabezales [SBP, DBP].
        if isinstance(pred,(tuple,list)) and len(pred)==2:
            sbp,dbp=float(np.asarray(pred[0]).reshape(-1)[0]),float(np.asarray(pred[1]).reshape(-1)[0])
        else:
            pp=np.asarray(pred).reshape(-1)
            if pp.size != 2: raise ValueError(f'Salida inesperada del modelo: {np.asarray(pred).shape}')
            sbp,dbp=map(float,pp)
        if not np.isfinite([sbp,dbp]).all(): raise ValueError('La red produjo valores no finitos')
        return sbp,dbp
