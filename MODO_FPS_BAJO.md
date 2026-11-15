# HEAMON — experimental low-FPS acquisition mode / Modo FPS bajo

**Warning / Advertencia:** This mode is for technical demos and research only. Estimates are NOT clinically validated. Blood-pressure inference from 8 FPS rPPG has unknown accuracy and must not guide health decisions.

## Problem / Problema
Browser track settings can report 30 FPS while HEAMON records ~8 samples per second. These are different measurements. The backend previously rejected all signals below 12 FPS; the frontend also required 140 samples within a 17-second rolling window.

## Run on PowerShell / Ejecutar
From `C:\Users\User\Downloads\Presion-Arterial`:

```powershell
$env:TF_USE_LEGACY_KERAS="1"
.\.venv\Scripts\python.exe servidor_camara.py --fabian-model modelos\lstm_ppg_nonmixed.h5 --low-fps
```

Open `http://127.0.0.1:8765/index.html` and acquire a stable signal for at least 12 seconds.

## Changes / Cambios
- Opt-in server flag `--low-fps`: minimum effective sampling lowered **only in this mode** from 12 to 7 FPS.
- Rejects long discontinuities in timestamps; does not bypass weak spectral peak or implausible BP checks.
- Browser now holds up to 24 seconds of RGB averages, sends a minimum of 90 samples after 12 seconds.
- Low-FPS results warn about their experimental status; resampling to the model input does **not** recover missing pulse information.
- Default server start without `--low-fps` retains the original 12 FPS threshold.

## Verify / Verificar
1. Confirm browser `getSettings().frameRate` (configured FPS), but remember this does not prove actual delivered/processed FPS.
2. Observe the dashboard *effective sampling* number. If it stays below 7, optimize the capture pipeline instead of lowering the threshold further.
3. Watch signal quality and read any rejection reason. Never use SBP/DBP as clinical readings.
4. For reproducible clinical/scientific performance claims, compare with reference instruments on independent subjects.
