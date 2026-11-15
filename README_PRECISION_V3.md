# HEAMON precision v3 — ventana de resultado y fallback controlado

## Qué corrige
- Mostrar **Calculando…** en BPM, calidad y presión arterial mientras no hay una medición validada. Es un estado; no inventa valores.
- Barra animada durante procesamiento/espera: 100 % de fotogramas recopilados no implica éxito del cálculo.
- Mantener consenso de dos regiones como ruta preferida. Si no se logra, se admite **una región con señal espectral excepcional** (SNR >= 4 dB y fracción pico >= 0.65), sujeto además a dos ventanas consistentes en la interfaz.
- El modo de una región queda identificado como `quality_mode: single_region_high_quality` en la API. No es validación clínica.
- Si no existe ninguna señal válida, HEAMON continúa mostrando Calculando y una explicación tras 45 s, no una cifra fabricada.

## Limitaciones
La captura mostrada por el usuario tiene ~12 FPS efectivos y 0 regiones concordantes. **Este cambio no garantiza extraer pulso si no hay señal válida en ninguna región**. Las gafas, sombras, luz artificial y pequeñas zonas de piel pueden causar el fallo.
El fallback debe validarse contra oxímetro y la presión arterial contra tensiómetro antes de alegar exactitud. Mantiene el checkpoint y la forma de onda CHROM.

## Integración
Copiar `servidor_camara.py` y `camara_dashboard.html` sobre la rama `precision-v1`. No modificar `requirements_web.txt` ni el script de checkpoint.
Probar `python -m pytest tests/test_vitasense_hr.py tests/test_precision.py -q`.
