# HEAMON — ampliar regiones faciales, partiendo de `web-deployment`

## Alcance estricto

Este parche modifica **solo `camara_dashboard.html`**, partiendo de la versión `web-deployment` preparada anteriormente; no se incorporan algoritmos, filtros, modos de calibración ni ciclos de resultados de `precision-v1`, `precision-v2`, `precision-v3` o `precision-v4`.

- Frente: 6 sectores poligonales distribuidos en tres columnas y dos filas dentro de la región delimitada por landmarks MediaPipe.
- Mejilla/pómulo izquierdo: 2 polígonos.
- Mejilla/pómulo derecho: 2 polígonos.
- Total: hasta 10 sectores. Se dibujan en verde los sectores con muestras válidas y en naranja los descartados.
- Se extraen promedios RGB por polígono de una copia de la imagen de cámara reducida (320 x 180) para limitar el costo del muestreo. Se combinan con medianas espaciales dentro de cada grupo y pesos de 50 % frente y 25 % cada pómulo, cuando los tres grupos están disponibles. Se renormalizan los pesos para los grupos disponibles.
- El servidor recibe **el mismo formato** anterior: `timestamps: []` y `rgb: [[R,G,B],...]`. No cambia `servidor_camara.py`, el algoritmo CHROM/FFT, los umbrales, los tiempos, el LSTM ni sus datos de entrada previstos.
- Muestra el número de polígonos útiles en el estado de captura. Se requieren por lo menos 3 polígonos muestreables en el fotograma para generar un promedio.

## Limitaciones y precauciones

**Más polígonos no garantizan por sí mismos mayor precisión**. Pueden empeorar la señal si se incluyen sombras, gafas, pelo, maquillaje o movimiento. Este cambio necesita una comparación controlada frente a oxímetro (varias sesiones, misma iluminación y cámara) para evaluar la variabilidad de BPM. No significa que el LSTM pueda determinar presión arterial con exactitud clínica.

Esta versión conserva los resultados y la lógica de calibración que ya estaban en `web-deployment`, sin asegurar una nueva frecuencia de salida. Es posible que el muestreo real siga limitado por MediaPipe o el hardware.

## Instalación segura (Git Bash)

```bash
cd '/c/Users/User/Downloads/NASA 2026/Presion-Arterial'
git status --short
git fetch origin
git switch web-deployment
git pull --ff-only origin web-deployment
git switch -c web-roi-ampliado
```

Antes de reemplazar, guardar una copia del dashboard actual, por ejemplo desde el explorador de Windows. Copiar `camara_dashboard.html` del parche en la raíz del repositorio. Si ya existía la rama `web-roi-ampliado`, usar `git switch web-roi-ampliado` en vez de crearla.

```bash
git diff -- camara_dashboard.html
git add camara_dashboard.html
git commit -m 'Expand forehead and cheek sampling on web baseline'
git push -u origin web-roi-ampliado
```

**No cambiar la rama de Render antes de probar el dashboard con cámara.** La página pública sigue usando la rama configurada en Render; integrar después de las pruebas mediante un merge/PR hacia `web-deployment` mantiene la URL pública sin necesidad de crear un nuevo servicio.

## Validación sugerida

1. Confirma 6 polígonos en la frente, 2 en cada mejilla y cuántos se muestran como útiles.
2. Confirma que `/api/estimate` recibe señales y que la webcam continúa funcionando.
3. Compara la versión anterior y esta con el mismo oxímetro (60–120 s por sesión) y registra BPM, FPS y estabilidad, **sin concluir que la precisión aumentó solo por verse más regiones**.
4. Confirma que las estimaciones de presión arterial siguen marcadas como experimentales.

## Fuente de trabajo

Se tomó como base el paquete anterior `HEAMON_Despliegue_Web_Docker_Render.zip`. Si `web-deployment` tuvo cambios posteriores en GitHub, **revisar el diff antes de reemplazar** para no sobrescribir trabajo reciente.
