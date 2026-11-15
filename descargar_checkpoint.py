"""Descarga un checkpoint PUBLICADO, sin generar pesos sintéticos. Ejecute voluntariamente."""
import hashlib, urllib.request
from pathlib import Path
URL='https://zenodo.org/records/5590603/files/lstm_ppg_nonmixed.h5?download=1'
DEST=Path(__file__).resolve().parent/'modelos'/'lstm_ppg_nonmixed.h5'
MD5='189bc9c1e6b946a0b91f936a07848801'
DEST.parent.mkdir(parents=True,exist_ok=True)
print('Descargando modelo real desde Zenodo:', URL)
try:
    urllib.request.urlretrieve(URL,DEST)
    h=hashlib.md5(DEST.read_bytes()).hexdigest()
    if h != MD5:
        DEST.unlink(missing_ok=True)
        raise RuntimeError('No coincide el checksum publicado: archivo rechazado')
    print('Descarga verificada:',DEST)
except Exception as e:
    print('No fue posible descargar automáticamente:',e)
    print('Descarga manual:', 'https://zenodo.org/records/5590603')
    raise SystemExit(1)
