# HEAMON — frente ampliada y estabilidad de BPM (`web-roi-ampliado`)

## Origen

Modificación aplicada **sobre el ZIP recibido** `Presion-Arterial-web-roi-ampliado.zip`. No se han incorporado componentes de `precision-v1`, `precision-v3` ni `precision-v4`.

## Cambios

- **Frente**: 15 sectores (5 columnas × 3 filas) que abarcan una banda más ancha de piel frontal, delimitada por los puntos de MediaPipe 10, 70, 300, 105, 334, 234, 454 y 152. No se considera válido el pelo ni una zona fuera del rostro. La cobertura depende del peinado, los movimientos, la calidad de la detección facial y la iluminación.
- **Pómulos**: exactamente los mismos cuatro polígonos del ZIP original (dos a cada lado).
- **RGB**: mediana espacial por grupo y fusión frente/pómulos con pesos iniciales de 60/20/20, renormalizados si falta algún grupo. Se mantiene el formato de API (`timestamps`, `rgb`).
- **BPM**: filtro temporal *solo de visualización* con mediana de hasta cinco candidatos recientes; exige confirmación de dos estimaciones compatibles ante cambios superiores a `max(18 BPM, 18 % de BPM anterior)`. Con calidad espectral menor de 0.22 no publica lectura nueva. No prohíbe cambios fisiológicos reales: los acepta cuando se confirman.
- **Estado**: si la estimación se rechaza o verifica, indica que muestra temporalmente un valor anterior; a los 8 segundos sin datos aceptados lo reemplaza por `Calculating…`/`Calculando…`. La pantalla no debe interpretarse como un monitor clínico continuo.
- **Presión arterial**: no se modificó el modelo de Schrumpf ni `servidor_camara.py`. Cuando el BPM nuevo está en revisión, **no** se publica la presión de ese ciclo para evitar asociar una presión a un BPM anterior retenido.
- **Idiomas**: inglés por defecto en una sesión nueva, español disponible con el selector existente; los nuevos mensajes de la captura tienen versión en ambos idiomas.

## Archivos modificados

Solo `camara_dashboard.html`. Se agregó esta guía y una prueba de la lógica. No cambies `fabian_adapter.py`, `requirements_web.txt` ni `heamon_i18n.js` para este parche.

## Pruebas automatizadas

Se validó la sintaxis JS y se probaron 15 polígonos frontales, cuatro pómulos, expansión lateral y la gestión de candidatos BPM aislados o confirmados con un rostro sintético. **No es una prueba de precisión fisiológica.**

## Validación con cámara y oxímetro

1. Ejecutar el servidor local como antes y abrir `http://127.0.0.1:8765/index.html` en Chrome o Edge.
2. Comprobar que se dibujan hasta 15 sectores sobre la frente y cuatro en pómulos; puede haber menos sectores *útiles* cuando hay cabello, sombra o ruido.
3. Comprobar el texto `Forehead X/15 · cheeks Y/4 (Z/19)` o su versión española.
4. Mantener postura e iluminación estables y comparar contra el oxímetro durante 2 minutos. Anotar BPM, FPS real, concentración espectral y cuándo se muestra un valor anterior o se rechaza.
5. Evaluar error absoluto, número de lecturas no evaluables y saltos >20 BPM que no correspondan al oxímetro. Una curva aparentemente estable **no implica precisión**.
6. Si sigue habiendo desviaciones grandes, el siguiente paso debe ser evaluar la **calidad de las señales por región en el backend**, no incrementar sin límite los polígonos ni ajustar arbitrariamente el BPM.

## Cómo integrarlo en tu PC

```bash
cd "/c/Users/User/Downloads/NASA 2026/Presion-Arterial"
git switch web-roi-ampliado
git status --short
```

Reemplaza `camara_dashboard.html` con el del parche y agrega esta guía. Evita ejecutar `git restore` si tienes cambios sin respaldar. Comprueba el código:

```bash
# Node.js opcional: verificación de sintaxis del script JS integrado
# Prueba manual con webcam: obligatoria antes de hacer push
TF_USE_LEGACY_KERAS=1 ./.venv/Scripts/python.exe servidor_camara.py --low-fps --fabian-model modelos/lstm_ppg_nonmixed.h5
```

Cuando la prueba local sea satisfactoria:

```bash
git add camara_dashboard.html README_ROI_ESTABILIDAD.md
git commit -m "Expand forehead sampling and guard unstable BPM readings"
git push origin web-roi-ampliado
```

Esto **no cambia Render**, salvo que Render esté configurado para desplegar esta rama. No cambies la rama pública hasta completar la prueba con cámara.
