$ErrorActionPreference = 'Stop'
$env:TF_USE_LEGACY_KERAS = '1'
if (-not (Test-Path '.\.venv\Scripts\python.exe')) { Write-Error 'Falta .venv; lee README_INICIO.md'; exit 1 }
if (-not (Test-Path '.\modelos\lstm_ppg_nonmixed.h5')) { Write-Error 'Falta .h5: ejecuta descargar_checkpoint.py'; exit 1 }
& '.\.venv\Scripts\python.exe' '.\servidor_camara.py' --fabian-model '.\modelos\lstm_ppg_nonmixed.h5'
