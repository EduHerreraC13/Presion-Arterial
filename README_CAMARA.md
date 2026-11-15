# Dashboard alimentado por webcam (sin entradas manuales)

**Este es un experimento rPPG, no un dispositivo médico.** El ZIP original incluye un simulador y un dashboard de evaluación de modelos, pero **no incluye un checkpoint de presión arterial entrenado con personas reales**. No se inventan valores de sistólica ni diastólica.

## Ejecutar en Windows (PowerShell)

```powershell
cd "RUTA\Presion-Arterial"
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python servidor_camara.py
```

Abre `http://127.0.0.1:8765/camara_dashboard.html` en Chrome o Edge. La detección MediaPipe requiere internet al menos durante la carga inicial del CDN y modelo.

La pantalla abre la cámara y registra únicamente datos de cámara; no hay inputs manuales de FC/PA. El navegador detecta la frente y extrae medias RGB. Envía **solo las medias RGB y tiempos** al servidor Python local, que filtra una señal pulsátil, calcula un espectro e informa FC experimental si hay una señal con pico suficiente. **No transmite el video**. El umbral espectral es heurístico y no equivale a exactitud médica.

### PA (solo para investigación)

Si posteriormente entrenas un modelo en **datos reales con sujetos separados** y verificas su comportamiento, puedes probar un checkpoint:

```powershell
python servidor_camara.py --ckpt runs/exp1/best.pt
```

El resultado SBP/DBP sigue siendo **inferencia experimental no calibrada ni validada en webcam**, no lectura médica. El modelo puede fallar por diferencia entre PPG de contacto y rPPG. No usar para alertas ni decisiones operativas. **No utilices checkpoints entrenados en datos sintéticos para mostrar PA como resultado real.**

### Qué NO produce la webcam

El dashboard original muestra MAE, comparaciones contra un predictor trivial y otros indicadores de *evaluación*. Esos outputs necesitan presiones de referencia de un tensiómetro o dataset anotado, por lo que **no pueden obtenerse exclusivamente de cámara**. Mantuvimos todos los scripts originales, y la plantilla `presion_arterial/web/dashboard.html` sigue disponible por separado.

### Limitaciones técnicas

- FaceLandmarker de MediaPipe se descarga de CDN; requiere acceso inicial y `localhost` para permisos de cámara.
- El ejemplo usa **CHROM simplificado**, no un pipeline rPPG validado; estimaciones ruidosas son posibles.
- La intensidad depende de luz y movimiento; la calidad espectral no confirma que la FC sea correcta.
- Antes de integrar con aplicaciones reales se requieren prueba con referencia, evaluación de latencia, privacidad y validación de diferentes condiciones de captura.
