# HEAMON — Precisión cardiovascular v2 (adaptación de VitaSense)

## Objetivo
Reducir saltos artificiales de BPM y comunicar al evaluador que HEAMON está **calibrando**, **procesando** o **esperando una señal aceptable**. Se mantiene la API `/api/estimate` y el modelo experimental de presión arterial (LSTM) **sin alterar sus pesos ni su adaptador**.

## Cambios frente a `precision-v1`

- **ROI de frente ampliada**: polígono de 18 puntos anatómicos inspirado en `rppg/roi.py` de VitaSense (no el círculo anterior), más dos regiones de pómulos. Las regiones se dibujan sobre la imagen y cada una tiene su propia traza RGB. Se descartan píxeles quemados u oscuros en los polígonos. La máscara no garantiza excluir pelo/anteojos ni se ha validado en todos los tonos de piel.
- **Captura más eficiente en el navegador**: FaceLandmarker se ejecuta aproximadamente cada 170 ms, pero se reutilizan landmarks suavizados para extraer muestras RGB de fotogramas intermedios (~36 ms como intervalo mínimo). Esto evita ejecutar MediaPipe en cada muestra; **no garantiza FPS reales** en un hardware concreto. Ante movimiento brusco, se reinicia la calibración.
- **Estimador inspirado en VitaSense**: `presion_arterial/vitasense_hr.py` evalúa CHROM y POS, calcula la FFT con interpolación parabólica del máximo, estima SNR/concentración, revisa estabilidad entre mitades, usa comprobaciones de armónicos y exige consenso entre al menos dos regiones. Es una adaptación propia, no un port 1:1 del pipeline Python de VitaSense.
- **Duración de calibración inicial**: 14 s con >=120 muestras. El backend acepta >=12 s. Analiza cada ~2.5 s y acumula hasta 25 s de trazas. Si no hay señal aceptable, no fuerza un BPM.
- **Interfaz de estados**: se ve la preparación inicial, progreso, procesamiento y el motivo de rechazo. Una barra al 100% significa **ventana reunida**, no que el BPM esté necesariamente validado. Dos ventanas concordantes son necesarias para el primer valor visualizado.
- **El LSTM no se reemplaza**: recibe la forma de onda CHROM filtrada; no el BPM suavizado por la UI. La presión arterial sigue siendo una hipótesis experimental con transferencia PPG contacto a rPPG sin validación clínica.

## Integración segura en GitHub

Conservar `main` y `web-deployment`. Copiar estos archivos a `precision-v1` (o mejor, otra rama basada en `precision-v1`):

- `camara_dashboard.html`
- `servidor_camara.py`
- `presion_arterial/vitasense_hr.py` **(nuevo y obligatorio)**
- `tests/test_vitasense_hr.py` (opcional, recomendado)

**No sustituir** `requirements_web.txt`, `descargar_checkpoint.py`, `Dockerfile`, el checkpoint ni `presion_arterial/fabian_adapter.py`. La API sigue en el mismo origen; Render seguirá funcionando con la URL existente cuando se publique la rama correcta. En Render, verificar que **Branch** sea la rama actualizada y que **Auto-Deploy** esté habilitado.

## Cómo probar antes de compartirlo

1. `python -m pytest tests/test_precision.py tests/test_vitasense_hr.py -q`
2. Iniciar localmente con el comando habitual de `servidor_camara.py` y el modelo de presión arterial, si está disponible.
3. Frente visible, sin mano sobre nariz/pómulos, con luz uniforme, a una distancia estable. La ROI de frente aparece como un **polígono delineado**, no como un círculo pequeño.
4. Comprobar FPS efectivos y `Regiones concordantes`, comparando durante 60-120 s contra pulsioxímetro sincronizado. Anotar **MAE en BPM**, porcentaje de ventanas rechazadas y tiempo hasta primer resultado válido.
5. Probar con 720p/30 FPS nominales. Si Render o el navegador no alcanzan FPS suficientes, optimizar JS/carga y no bajar sin más los umbrales para inventar resultados.

## Advertencias

- Pruebas unitarias con señales sintéticas no equivalen a validación biomédica, precisión real ni mejoría demostrada frente al oxímetro.
- VitaSense implementa además un filtro de Kalman escalar; esta versión **conserva el seguimiento temporal existente de HEAMON** por compatibilidad con la interfaz y el backend sin sesión. Se puede evaluar un Kalman en otra iteración usando mediciones reales.
- No publicar la versión hasta comparar contra un instrumento de referencia. Evitar comunicar valores clínicos de presión arterial.
