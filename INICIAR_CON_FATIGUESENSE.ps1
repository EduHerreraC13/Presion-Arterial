$ErrorActionPreference = 'Stop'
$env:TF_USE_LEGACY_KERAS = '1'
if (-not (Test-Path '.\.venv\Scripts\python.exe')) { Write-Error 'Falta .venv; lee README_INICIO.md'; exit 1 }
if (-not (Test-Path '.\terceros\fatigue-sense\fatigue_pipeline')) { Write-Error 'Clona el repositorio FatigueSense primero; consulta README_INICIO.md'; exit 1 }
& '.\.venv\Scripts\python.exe' '.\servidor_camara.py' --fabian-model '.\modelos\lstm_ppg_nonmixed.h5' --fatiguesense-root '.\terceros\fatigue-sense'
