"""Convierte un dataset de PPG+PA (HDF5 / MAT v7.3 / npz) al formato .npz de este proyecto.

NO se probó contra los archivos reales de PulseDB/VitalDB (no estaban disponibles al escribirlo).
Primero inspecciona el archivo para ver sus claves y formas, luego indica cuáles usar:

    python scripts/prepare_dataset.py inspect archivo.mat
    python scripts/prepare_dataset.py convert archivo.mat --ppg-key Subset/Signals --channel 1 \
        --sbp-key Subset/SBP --dbp-key Subset/DBP --subject-key Subset/Subject --fs 125 \
        --out data/pulsedb.npz [--transpose] [--max-segments 200000]

Notas: los .mat v7.3 guardan las matrices transpuestas al leerlas con h5py (usa --transpose si
ppg queda como (L, N)). `--subject-key` es obligatorio: sin identificar a la persona no se puede
particionar sin fuga de datos.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from presion_arterial.data import save_npz  # noqa: E402


def _open(path: str):
    if path.endswith(".npz"):
        return np.load(path, allow_pickle=False)
    try:
        import h5py
    except ImportError:
        raise SystemExit("Instala h5py: pip install h5py")
    return h5py.File(path, "r")


def _arr(f, key):
    return np.asarray(f[key][()])


def cmd_inspect(a):
    f = _open(a.file)
    if a.file.endswith(".npz"):
        for k in f.files:
            print(f"{k:30s} {f[k].shape} {f[k].dtype}")
        return

    def visit(name, obj):
        if hasattr(obj, "shape"):
            print(f"{name:40s} {obj.shape} {obj.dtype}")
    f.visititems(visit)


def cmd_convert(a):
    f = _open(a.file)
    ppg = _arr(f, a.ppg_key)
    if a.transpose:
        ppg = ppg.T
    if ppg.ndim == 3:
        ppg = ppg[:, a.channel, :]
    sbp, dbp = _arr(f, a.sbp_key).ravel(), _arr(f, a.dbp_key).ravel()
    subj = _arr(f, a.subject_key).ravel()
    n = len(sbp)
    if not (ppg.ndim == 2 and len(ppg) == n == len(dbp) == len(subj)):
        raise SystemExit(f"Formas incompatibles: ppg {ppg.shape}, sbp {sbp.shape}, dbp {dbp.shape}, subject {subj.shape}. "
                         "Prueba --transpose o --channel.")
    ok = np.isfinite(ppg).all(1) & np.isfinite(sbp) & np.isfinite(dbp)
    # filtros fisiológicos básicos para quitar etiquetas imposibles
    ok &= (sbp > 60) & (sbp < 260) & (dbp > 30) & (dbp < 160) & (sbp > dbp)
    print(f"Segmentos válidos: {ok.sum()}/{n}")
    idx = np.flatnonzero(ok)
    if a.max_segments and len(idx) > a.max_segments:
        idx = np.sort(np.random.default_rng(0).choice(idx, a.max_segments, replace=False))
    Path(a.out).parent.mkdir(parents=True, exist_ok=True)
    save_npz(a.out, ppg[idx], sbp[idx], dbp[idx], subj[idx], a.fs)
    print(f"Guardado {len(idx)} segmentos de {ppg.shape[1] / a.fs:.1f} s, {len(set(subj[idx].tolist()))} sujetos -> {a.out}")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    i = sub.add_parser("inspect"); i.add_argument("file"); i.set_defaults(fn=cmd_inspect)
    c = sub.add_parser("convert"); c.add_argument("file")
    c.add_argument("--ppg-key", required=True); c.add_argument("--sbp-key", required=True)
    c.add_argument("--dbp-key", required=True); c.add_argument("--subject-key", required=True)
    c.add_argument("--fs", type=float, required=True); c.add_argument("--out", required=True)
    c.add_argument("--channel", type=int, default=0, help="si ppg es (N, C, L), canal a usar")
    c.add_argument("--transpose", action="store_true"); c.add_argument("--max-segments", type=int, default=0)
    c.set_defaults(fn=cmd_convert)
    a = ap.parse_args(); a.fn(a)


if __name__ == "__main__":
    main()
