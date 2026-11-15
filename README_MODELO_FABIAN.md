# Modelo preentrenado de presión arterial — integración experimental

Esta variante PRESERVA el dashboard de webcam (BPM, concentración espectral, sistólica y diastólica). Añade un adaptador real para el modelo **LSTM PPG** de Schrumpf et al., *Sensors* 2021. **No incluye pesos falsos ni genera presión ficticia.**

## Limitación principal

El modelo publicado fue entrenado con PPG de CONTACTO a 125 Hz, 875 muestras (7 s), no directamente con rPPG de esta webcam. Nuestra cámara puede adquirir hasta 1920×1080 a 30 FPS, pero el procesamiento consume recursos y el muestreo real puede ser menor. Remuestrear 30→125 Hz **no reconstruye** detalles perdidos. Estos números, si se obtienen, solo demuestran que corrió inferencia de DL, **no que se midió presión arterial**. No utilizar para decisiones médicas, clasificación de riesgos, ni actividades de astronautas.

## Windows — instalación

Usa preferentemente Python 3.10/3.11 (el entorno del autor usaba Python 3.8 + TensorFlow 2.4.1; los checkpoints HDF5 pueden necesitar versión legado). Python 3.13 y TensorFlow legado no son una combinación equivalente.

```powershell
cd "RUTA\Presion-Arterial"
py -3.11 -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m pip install -r requirements_dl.txt
.\.venv\Scripts\python.exe descargar_checkpoint.py
.\.venv\Scripts\python.exe servidor_camara.py --fabian-model modelos\lstm_ppg_nonmixed.h5
```

Si `py -3.11` no está instalado, instala Python 3.11 o usa un entorno compatible. No instales dependencias DL a ciegas en Python 3.13. El navegador sigue en http://127.0.0.1:8765/camara_dashboard.html.

**IMPORTANTE:** los modelos Keras de 2021 pueden NO abrir con TensorFlow 2.15: en ese caso se debe replicar el entorno Python 3.8/TF 2.4.1 o convertir el checkpoint. El servidor falla explícitamente si no puede cargarlo, sin inventar números. No se verificó esa conversión en este entorno.

Modelo Zenodo: https://zenodo.org/records/5590603 (LSTM de 2.5 MB con MD5 `189bc9c1e6b946a0b91f936a07848801`). Código original: https://github.com/Fabian-Sc85/non-invasive-bp-estimation-using-deep-learning (GPL-3.0). Se debe citar a Schrumpf et al. y revisar la licencia del modelo descargado para redistribución.

## Qué se añadió

- `presion_arterial/fabian_adapter.py`: carga del modelo REAL con `tf.keras`, chequeo de entradas y salidas, inferencia con ventanas de siete segundos.
- `descargar_checkpoint.py`: descarga desde Zenodo y comprueba checksum.
- `--fabian-model`: sustituye el adaptador de PyTorch del proyecto previo por el de Keras .h5.
- Conserva frecuencias cardíacas, calidad, waveform, FPS, avisos y PAS/PAD (si existe inferencia).
- Solicita 1080p/30 FPS a la cámara; comprueba el muestreo real de RGB y no infiere PA sin modelo.

## Lo que NO se probó

No se descargó ni ejecutó el `.h5` en esta sesión, ni se dispuso de una webcam real o TensorFlow. Por tanto NO se ha demostrado que el checkpoint antiguo cargue en TF moderno o que prediga correctamente desde webcam. El modelo podría producir números plausibles pero fisiológicamente erróneos. Verificación obligatoria con tensiómetro y pruebas de sujetos independientes para estudiar errores.
