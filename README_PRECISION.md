# HEAMON — rPPG de múltiples regiones y calibración visible (prototipo v1)

## Qué se cambió

- **Frontend** `camara_dashboard.html`: conserva los módulos y el backend existentes; capta tres promedios RGB por fotograma (frente y ambos pómulos), no envía imágenes al endpoint cardiovascular. MediaPipe se ejecuta en el navegador. Pide 720p/30 fps, que es **una preferencia**, no un FPS garantizado.
- **Validación de señal**: cada región se procesa independientemente con CHROM; se contrasta la estabilidad espectral entre mitades temporales, brillo, concentración de energía y concordancia entre al menos dos regiones. Una lectura mala devuelve `no_evaluable` y no inventa BPM.
- **Estimación de BPM**: usa interpolación espectral (zero padding de la FFT), promediado ponderado de regiones concordantes y confirmación entre ventanas consecutivas. No se reemplaza directamente la pantalla con cada pico de la FFT.
- **Calibración explícita**: 20 segundos continuos y al menos 135 muestras antes de llamar al servidor; muestra porcentaje, "Analizando señal", "Validando primer resultado", "Señal no fiable" y "Monitoreo · señal aceptada". Se actualiza aproximadamente cada 2.8 s si existe señal útil.
- **Presión arterial experimental**: mantiene el checkpoint LSTM Schrumpf, su adaptador y la inferencia únicamente cuando hay una forma de onda con calidad suficiente. **No valida ni calibra la presión arterial**. El modelo sigue recibiendo una señal de pulso, nunca el BPM suavizado.

## Límites y condiciones

- La calidad y el rendimiento no están comprobados con una cámara real, ni contra oxímetro o tensiómetro. Los filtros son **heurísticos experimentales**.
- Un error o un cambio brusco verificable puede tardar en actualizarse. En ventanas de mala calidad se muestra calibración en lugar de simular una medición.
- El valor de presión arterial mostrado depende de la misma selección de calidad por ROI. El LSTM fue entrenado con PPG de contacto; extrapolarlo a rPPG de webcam requiere validación por separado.
- La rama `web-deployment` en Render usa Python + TensorFlow; no requiere Python instalado en el navegador. Render Free puede dormirse y tiene límites de memoria.
- **No subas directamente sobre la rama activa sin antes probar**: conserva `main` y prueba primero una rama `precision-v1`, compara resultados y luego fusiona a `web-deployment`.

## Cómo instalar el parche

Copia **solo** `servidor_camara.py` y `camara_dashboard.html` sobre los archivos del proyecto, dentro de una rama nueva. El ZIP completo también incorpora los archivos de despliegue anteriores por comodidad.

```bash
git switch web-deployment
git pull --ff-only origin web-deployment
git switch -c precision-v1
# Copia los archivos parcheados y prueba localmente
python servidor_camara.py --low-fps --fabian-model modelos/lstm_ppg_nonmixed.h5
# En navegador: http://localhost:8765/index.html
```

Para probar sin checkpoint, omite `--fabian-model`; esto solo permite inspeccionar las señales/BPM, no PA. En el servidor público conserva su línea de inicio y las variables `PYTHON_VERSION=3.13.17` y `TF_USE_LEGACY_KERAS=1`.

## Validaciones recomendadas antes de integrar

1. Cámara 720p 30 fps nominales: medir FPS **procesados** y tiempo de calibración; intentar 60–120 s sin movimiento.
2. Oxímetro como referencia de BPM: MAE, máximo salto erróneo, cantidad de ventanas rechazadas y latencia.
3. Repetir con movimientos leves y distintas luces; comparar con la versión anterior.
4. Validar que `/api/estimate`, `/api/health`, `index.html` y los módulos de fatiga sigan funcionando. Si la cámara no alcanza 135 muestras en 20 s, el mensaje de calibración permanece hasta completar la cantidad mínima de muestras.
5. Revisar CPU/RAM en Render Free; no declarar que está listo para la presentación hasta verificarlo.

## Nota de compatibilidad

El API sigue aceptando el formato previo `{timestamps, rgb}` y opcionalmente el nuevo objeto `rois` con `left_cheek` y `right_cheek`. Las muestras deben estar sincronizadas y ordenadas. La presión arterial permanece no clínica y experimental.
