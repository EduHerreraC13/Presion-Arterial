# HEAMON — Monitoring Health

**Prototipo multimodal de monitoreo experimental de señales fisiológicas y conductuales mediante webcam.** Diseñado como proyecto de exploración para el desafío de monitoreo de salud de astronautas de NASA Space Apps Challenge 2026.

> **Investigación / demostración — no es un dispositivo médico.** Los resultados de presión arterial, frecuencia cardíaca, respiración y somnolencia obtenidos por webcam no están clínicamente validados. No utilizar para diagnóstico, decisiones de tratamiento ni decisiones operativas de seguridad.

## ¿Qué incluye?

| Módulo | Salidas | Tecnología / límite |
|---|---|---|
| Cardiovascular | BPM, concentración espectral, señal rPPG, PAS y PAD experimentales | Webcam RGB + análisis espectral + LSTM PPG preentrenada de Schrumpf; aplicar PPG de contacto a rPPG facial **no está validado** |
| Fatiga visual | EAR, PERCLOS estimado, parpadeos, duración de cierres, movimiento de cabeza, índice heurístico | MediaPipe Face Landmarker + cálculos temporales; los pesos y los umbrales del índice **no son escala clínica** |
| Respiración | Respiraciones/min, ciclos observados y calidad | Seguimiento de movimiento vertical del torso (flujo óptico) con luminancia de respaldo; sensible a encuadre, ropa, iluminación y movimientos |
| FatigueSense (opcional) | Probabilidades oculares/bucales y *focus score* temporal | Código y checkpoints publicados por FatigueSense; se descargan por separado y requieren verificar compatibilidad de dependencias y FPS |

La frecuencia respiratoria contribuye con un **15 % heurístico** al índice original de HEAMON únicamente cuando su señal supera los controles de calidad. El BiGRU de FatigueSense **no** utiliza directamente la respiración. Los resultados aparecen diferenciados para evitar atribuir al modelo neuronal una fusión que no ha sido entrenada.

## Interfaz y arquitectura

- `index.html`: inicio y navegación entre las pestañas con captura de cámara compartida en el navegador.
- `camara_dashboard.html`: módulo cardiovascular.
- `fatiga_respiracion.html`: módulo ocular + respiración de HEAMON.
- `servidor_camara.py`: servidor HTTP local y endpoints de estimación.
- `presion_arterial/fabian_adapter.py`: integración experimental con checkpoint LSTM `.h5` de Schrumpf.
- `fatiguesense_bridge.py`: adaptador opcional para los modelos **originales** de FatigueSense.
- `descargar_checkpoint.py`: descarga y verificación del checkpoint de presión arterial desde Zenodo.
- `tests/`: pruebas del pipeline cardiovascular.
- `README_INICIO.md`: instrucciones detalladas, incluido FatigueSense.

**Una webcam:** el navegador es el propietario del video; los módulos comparten el mismo recurso. La solicitud de 1920 × 1080 / 30 FPS no garantiza que cada pipeline alcance esos FPS (el puente FatigueSense limita solicitudes y puede procesar bastante menos).

## Instalación (Windows PowerShell, Python 3.13)

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m pip install "tensorflow==2.20.0" "tf-keras==2.20.1"
.\.venv\Scripts\python.exe descargar_checkpoint.py
$env:TF_USE_LEGACY_KERAS = '1'
.\.venv\Scripts\python.exe servidor_camara.py --fabian-model modelos\lstm_ppg_nonmixed.h5
```

Abrir **http://127.0.0.1:8765/index.html** y autorizar la webcam. Los archivos `.h5` se descargan localmente y están excluidos de Git. Si falla la carga del checkpoint legado, revisar `README_MODELO_FABIAN.md` y la versión de Keras.

### FatigueSense opcional

```powershell
New-Item -ItemType Directory -Force terceros | Out-Null
git clone https://github.com/Fatigue-Sense/fatigue-sense.git terceros\fatigue-sense
.\.venv\Scripts\python.exe -m pip install -r terceros\fatigue-sense\requirements.txt
$env:TF_USE_LEGACY_KERAS = '1'
.\.venv\Scripts\python.exe servidor_camara.py --fabian-model modelos\lstm_ppg_nonmixed.h5 --fatiguesense-root terceros\fatigue-sense
```

**Atención:** las dependencias del proyecto de terceros pueden requerir resolución adicional. La activación de FatigueSense no ha sido verificada con webcam en esta distribución. Si no está activo, los indicadores oculares y respiratorios de HEAMON permanecen disponibles.

## Investigación y fuentes principales

**Código/modelos reutilizados y atribuciones:**

- Schrumpf et al. (2021), *Assessment of Non-Invasive Blood Pressure Prediction from PPG and rPPG Signals Using Deep Learning*: https://doi.org/10.3390/s21186022 — código https://github.com/Fabian-Sc85/non-invasive-bp-estimation-using-deep-learning y modelos https://zenodo.org/records/5590603
- FatigueSense: https://github.com/Fatigue-Sense/fatigue-sense — repositorio original, arquitectura temporal, dependencias y checkpoints distribuidos por sus autores.
- MediaPipe: https://github.com/google-ai-edge/mediapipe — seguimiento de rasgos faciales.
- J0R0W/Breathing: https://github.com/J0R0W/Breathing — **solo referencia conceptual**, su código no se distribuye en este proyecto.
- rPPG-Toolbox: https://github.com/ubicomplab/rPPG-Toolbox — **referencia** para futuras evaluaciones de rPPG.

**Datos para evaluación futura (no incluidos ni utilizados para validar esta webcam):** UBFC-rPPG, COHFACE, UTA-RLDD y datos de presión arterial de referencia sincronizados. Consulta `docs/DATASETS.md`.

### Licencias y publicación

Los repositorios, modelos y datos de terceros conservan sus propias condiciones de licencia; compruébalas **por separado** antes de redistribuir checkpoints, materiales o derivados. El repositorio de Schrumpf declara GPL-3.0. Este paquete **no incluye** los pesos externos ni una copia del código de FatigueSense. **La licencia del código original de HEAMON aún debe ser acordada por sus autores y participantes**; no se ha creado un archivo LICENSE para evitar atribuir permisos sin autorización.

## Limitaciones y validación pendiente

1. Evaluar BPM con PPG de referencia (por ejemplo UBFC-rPPG).
2. Comparar PAS/PAD con un tensiómetro; el modelo LSTM fue entrenado con **PPG de contacto**, no con nuestro rPPG de webcam.
3. Validar EAR/PERCLOS, cierres y somnolencia con anotaciones y sujetos independientes.
4. Validar respiración mediante conteo o sensor de referencia y medir error en respiraciones/min.
5. Probar FatigueSense con sus checkpoints originales, documentar FPS efectivos, latencias y resultados.
6. Evaluar la combinación de señales y la aportación real de la respiración al índice de fatiga.

**Privacidad:** procesamiento local por defecto. No subir videos de participantes, archivos biométricos, datos sensibles, secretos, `.venv`, modelos ni salidas de entrenamiento. Cualquier estudio con personas requiere su consentimiento y una política de tratamiento de datos.

## Estado de las pruebas

Se han comprobado pruebas estáticas/automatizadas del pipeline y endpoints de desarrollo. No se ha completado una validación clínica ni una prueba reproducible de todos los modelos simultáneamente con cámara real.
