# Datasets

> Descritos de memoria. **Verifica disponibilidad, licencia, formato y términos de acceso antes de planificar**;
> pueden haber cambiado. Varios exigen solicitud o acuerdo de uso (PhysioNet requiere credenciales).

## A. PPG de contacto + PA (para entrenar la relación pulso → PA)

| Dataset | Notas |
|---|---|
| **PulseDB** | Benchmark curado a partir de MIMIC-III y VitalDB: segmentos de 10 s con PPG, ECG y PA, con partición por sujeto. **Punto de partida recomendado.** |
| MIMIC-III / IV Waveform (PhysioNet) | Pacientes de UCI, PA invasiva + PPG. Requiere cuenta acreditada. |
| VitalDB | Pacientes quirúrgicos, línea arterial + PPG. |
| UCI Cuff-Less BP | Versión reducida de MIMIC-II; útil para pruebas rápidas. |
| PPG-BP (Liang et al.), Aurora-BP | PPG de dedo/portátil con PA por cuff; tamaños menores. |

**Sesgo a tener presente:** son pacientes hospitalizados (UCI/quirófano), no personas sanas frente a una webcam.

## B. Video facial + PA (el más escaso; necesario para validar de verdad)

| Dataset | Notas |
|---|---|
| **BP4D+** | Video multimodal de ~140 personas con señales fisiológicas incluida PA. Acceso por licencia. |
| **V4V (Vision-for-Vitals)** | Derivado de BP4D+ con anotaciones de FC y PA (reto ICCV 2021). |
| Datos propios | Casi inevitables. Ver abajo. |

## C. Video facial + pulso de referencia (sin PA; para la etapa video → pulso)

UBFC-rPPG, PURE, VIPL-HR, MMPD, MAHNOB-HCI, COHFACE, MMSE-HR; **SCAMPS** (sintético). Se usan con rPPG-Toolbox.

## Datos propios: diseño mínimo razonable

- 100+ participantes, variedad de edad, sexo, tono de piel (Fitzpatrick) y **rango de PA** (sin variación, el modelo solo aprende la media).
- Varias sesiones por persona: reposo, tras ejercicio leve, distintos momentos del día.
- Referencia validada: tensiómetro clínico como mínimo; ideal, PA continua y pulsioxímetro para sincronizar.
- Condiciones variadas de luz, cámara y distancia; metadatos (edad, sexo, medicación, tono de piel).
- Consentimiento informado y aprobación ética antes de grabar.

## Formato `.npz` que espera este proyecto

| Clave | Forma | Descripción |
|---|---|---|
| `ppg` | (N, L) | Segmentos de PPG de contacto, L ≥ 6 s × fs (ideal 8–10 s) |
| `sbp`, `dbp` | (N,) | PA de referencia en mmHg |
| `subject` | (N,) | Identificador de persona (**obligatorio**) |
| `fs` | escalar | Frecuencia de muestreo de `ppg`, p. ej. 125 |

`scripts/prepare_dataset.py inspect|convert` ayuda a generarlo desde HDF5 / MAT v7.3 (sin probar contra los archivos reales).
