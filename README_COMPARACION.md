# Comparativa de referencias AHA — Dashboard webcam

Esta edición conserva la captura de webcam, señal rPPG, concentración espectral y las predicciones de presión arterial sistólica/diastólica del modelo preentrenado, y añade una sección de comparación **automática** (sin entradas manuales).

## Uso

Con Python y dependencias ya instaladas en `.venv`:

```powershell
$env:TF_USE_LEGACY_KERAS="1"
.\.venv\Scripts\python.exe servidor_camara.py --fabian-model modelos\lstm_ppg_nonmixed.h5
```

Abrir http://127.0.0.1:8765/camara_dashboard.html y pulsar **Activar cámara**.

## Criterios poblacionales (AHA), solamente educativos

- FC en reposo de adultos: habitualmente 60–100 lpm. Entrenamiento físico, medicamentos y contexto pueden alterar este intervalo.
- PA convencional: normal sistólica <120 **y** diastólica <80; elevada sistólica 120–129 **y** diastólica <80; etapa 1 sistólica 130–139 **o** diastólica 80–89; etapa 2 sistólica >=140 **o** diastólica >=90. Cifras de más de 180 sistólica y/o 120 diastólica pertenecen a una categoría muy elevada y precisan interpretación clínica de una medición validada, no de rPPG.

- https://www.heart.org/en/healthy-living/exercise-and-physical-activity/fitness-basics/target-heart-rates/
- https://www.heart.org/en/health-topics/high-blood-pressure/understanding-blood-pressure-readings

## Limitaciones esenciales

La presión arterial mostrada procede de la inferencia de un modelo PPG de contacto aplicado a rPPG facial de webcam **sin validación clínica**. Los umbrales de AHA se desarrollaron para mediciones reales de presión arterial y **no validan** las salidas de esta red neuronal. No se debe usar el panel para diagnosticar, prescribir, emitir alarmas clínicas o determinar aptitud para una misión. El indicador 'concentración del pico' NO es exactitud ni probabilidad de certeza.

El panel evita fabricar cifras cuando una entrada no existe. Al perder la cara o detenerse la cámara se eliminan comparaciones anteriores. Estas reglas son descriptivas y NO se retroalimentan al modelo ni a la toma de decisiones médicas.
