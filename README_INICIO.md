# HEAMON multimodal — proyecto completo de integración

## Contenido funcional

- **Cardiovascular:** `camara_dashboard.html` conserva extracción RGB/rPPG, BPM, calidad espectral, señal y PAS/PAD estimadas mediante `lstm_ppg_nonmixed.h5` del trabajo de Schrumpf et al. (si se habilita el checkpoint original). No hay datos manuales.
- **Fatiga y respiración:** `fatiga_respiracion.html` conserva el HEAMON que aportaste: EAR, PERCLOS, duración/frecuencia de parpadeos, movimiento de cabeza, respiraciones/mín, flujo óptico vertical del torso, luminancia como respaldo, calidad, índice experimental y comparación entre ventanas de 30 s.
- **FatigueSense opcional:** `fatiguesense_bridge.py` invoca el **repositorio original** y sus pesos de CNN de ojos/boca, YOLO de postura y BiGRU; muestra probabilidades y puntaje de enfoque cuando se dispone de suficientes características. No suplanta sus redes por fórmulas ficticias.
- **Cámara única:** `index.html` abre una única MediaStream con la webcam (preferencia 1920×1080 / 30 FPS); las dos vistas HTML acceden a ese mismo stream. Con pestañas ocultas, algunos navegadores limitan el procesamiento: prioriza la pestaña visible.

## Arranque rápido en Windows, reutilizando tu .venv de Python 3.13

Extrae el ZIP en una carpeta NUEVA. No sobrescribas ni borres la carpeta `.venv` de tu versión que sí está funcionando. La forma más fácil de usar sus dependencias es ejecutar el Python del entorno **ya instalado** mediante ruta absoluta, o crear un entorno nuevo en el proyecto.

```powershell
cd "C:\Users\User\Downloads\NASA 2026\prueba_2\HEAMON_Multimodal_Integrado"
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m pip install "tensorflow==2.20.0" "tf-keras==2.20.1"
$env:TF_USE_LEGACY_KERAS="1"
.\.venv\Scripts\python.exe descargar_checkpoint.py
.\.venv\Scripts\python.exe servidor_camara.py --fabian-model modelos\lstm_ppg_nonmixed.h5
```

> Si `tf-keras==2.20.1` no está disponible para tu plataforma, usa la versión 2.20.x compatible ofrecida por pip. En tu instalación previa ya conseguiste cargar el `.h5`: puedes reutilizar esa `.venv` directamente en lugar de reinstalar paquetes.

Abre **http://127.0.0.1:8765/index.html**, pulsa **Activar cámara compartida** y cambia de pestaña.

## Habilitar *realmente* FatigueSense (requiere internet una vez, Git y dependencias pesadas)

La integración opcional no incluye pesos ajenos: los obtiene del repositorio de los autores. Desde la raíz de ESTE proyecto:

```powershell
mkdir terceros -ErrorAction SilentlyContinue
git clone https://github.com/Fatigue-Sense/fatigue-sense.git terceros\fatigue-sense
.\.venv\Scripts\python.exe -m pip install -r terceros\fatigue-sense\requirements.txt
```

Después inicia el servidor con **ambos modelos**:

```powershell
$env:TF_USE_LEGACY_KERAS="1"
.\.venv\Scripts\python.exe servidor_camara.py --fabian-model modelos\lstm_ppg_nonmixed.h5 --fatiguesense-root terceros\fatigue-sense
```

Si no se instala o no se carga FatigueSense, el servidor sigue mostrando el motivo en el panel «FatigueSense»; la fatiga heurística y respiración original siguen funcionando. Si la descarga de Hugging Face falla por red o licencias, consulta el README original de los autores.

**Nota importante sobre ritmo de fotogramas:** este puente envía JPEG de 480px con un límite de ~10 solicitudes/segundo para evitar saturación de CPU; una webcam de 30 FPS no implica que el servidor procese 30 FPS. El BiGRU del repositorio se entrenó para un pipeline específico; aun cuando arroje una cifra, en nuestro puente se considera experimental **sin equivalencia validada con el comportamiento original**. Puede tardar en aparecer o permanecer indisponible si el FPS procesado es bajo. Se deben confirmar rendimiento y compatibilidad de preprocesamiento localmente.

## ¿Cómo influye la respiración en la fatiga?

El índice original HEAMON ya incorpora un **15 % heurístico** de la frecuencia respiratoria cuando hay señal considerada suficiente. Conservamos **exactamente esa regla original** para no alterar un prototipo que ya conoces. **La red FatigueSense no recibe directamente la respiración**: su score de enfoque permanece separado; no afirmamos haber reentrenado un modelo multimodal.

J0R0W/Breathing y sus ejemplos de flujo óptico / seguimiento de pose se utilizaron como **referencia técnica**, no se copió ni se incorporó su código porque su repositorio todavía indica una licencia pendiente. La implementación respiratoria que corre es la original de tu HEAMON (seguimiento vertical del torso con flujo óptico Lucas–Kanade + respaldo de luminancia).

## Privacidad y limitaciones

- Para **cardiovascular**: se envían valores medios RGB/tiempos al servidor `127.0.0.1`.
- Para **FatigueSense**: solo si se habilitó `--fatiguesense-root`, se envían fotogramas JPEG reducidos al **mismo servidor local**, para sus clasificadores. No se cargan a Hugging Face para inferencia; la primera instalación sí descarga pesos.
- La cámara puede dejar de funcionar al recargar solo uno de los iframes; si ocurre, actualiza `index.html` y vuelve a activar la cámara central.
- Sin validación clínica: BPM es rPPG experimental; PAS/PAD son predicciones de un modelo PPG de contacto aplicado a rPPG facial (cambio de dominio importante); el índice HEAMON y score FatigueSense no diagnostican fatiga. No utilices el sistema para decisiones de seguridad o tratamiento.
- **Pruebas realizadas en la preparación de este ZIP:** validación estática de JavaScript, compilación Python, 9 tests del paquete cardiovascular y endpoints HTTP; no se ha ejecutado MediaPipe/YOLO/TensorFlow con tu cámara en este entorno.

## Fuentes y atribución

- FatigueSense (código original y documentación): https://github.com/Fatigue-Sense/fatigue-sense ; modelos en https://huggingface.co/FatigueSense — revisar **cada licencia de pesos** antes de distribuirlos.
- J0R0W/Breathing, enfoque de respiración: https://github.com/J0R0W/Breathing — no se distribuye su código por licencia por determinar.
- Schrumpf et al., modelos LSTM PPG: https://github.com/Fabian-Sc85/non-invasive-bp-estimation-using-deep-learning y https://zenodo.org/records/5590603 — atención a GPL-3.0 y condiciones de redistribución.
- MediaPipe FaceLandmarker: modelo y paquete obtenidos en navegador desde servidores oficiales / CDN.
