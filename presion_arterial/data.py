"""Carga de datos, partición POR SUJETO y Dataset de PyTorch con degradación a estilo webcam.

Formato de datos (.npz):
    ppg      (N, L)  float   segmentos de PPG de contacto (L >= 6 s * fs)
    sbp      (N,)    float   PA sistólica de referencia (mmHg)
    dbp      (N,)    float   PA diastólica de referencia (mmHg)
    subject  (N,)    str/int identificador de persona (obligatorio: evita fuga de datos)
    fs       ()      float   frecuencia de muestreo de `ppg` (Hz), p. ej. 125
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

import numpy as np
import torch
from torch.utils.data import Dataset

from .config import FS_MODEL, WIN_N
from .degrade import DegradeConfig, crop_window, degrade_ppg, make_channels


@dataclass
class RawData:
    ppg: np.ndarray
    sbp: np.ndarray
    dbp: np.ndarray
    subject: np.ndarray
    fs: float

    def __len__(self):
        return len(self.sbp)


def load_npz(path: str) -> RawData:
    d = np.load(path, allow_pickle=False)
    for k in ("ppg", "sbp", "dbp", "subject", "fs"):
        if k not in d:
            raise KeyError(f"Falta '{k}' en {path}. Ver el formato en presion_arterial/data.py")
    raw = RawData(d["ppg"].astype(np.float32), d["sbp"].astype(np.float32), d["dbp"].astype(np.float32),
                  d["subject"].astype(str), float(d["fs"]))
    _validate(raw)
    return raw


def save_npz(path: str, ppg, sbp, dbp, subject, fs: float) -> None:
    np.savez_compressed(path, ppg=np.asarray(ppg, np.float32), sbp=np.asarray(sbp, np.float32),
                        dbp=np.asarray(dbp, np.float32), subject=np.asarray(subject).astype(str), fs=float(fs))


def from_dict(d: dict) -> RawData:
    raw = RawData(np.asarray(d["ppg"], np.float32), np.asarray(d["sbp"], np.float32),
                  np.asarray(d["dbp"], np.float32), np.asarray(d["subject"]).astype(str), float(d["fs"]))
    _validate(raw)
    return raw


def _validate(raw: RawData) -> None:
    n = len(raw.sbp)
    if not (raw.ppg.ndim == 2 and len(raw.ppg) == n == len(raw.dbp) == len(raw.subject)):
        raise ValueError("ppg debe ser (N, L) y coincidir en N con sbp, dbp y subject")
    if raw.ppg.shape[1] / raw.fs < 6.0:
        raise ValueError(f"Los segmentos duran {raw.ppg.shape[1] / raw.fs:.1f} s; se necesitan >= 6 s")
    ok = np.isfinite(raw.ppg).all(1) & np.isfinite(raw.sbp) & np.isfinite(raw.dbp)
    if not ok.all():
        raise ValueError(f"{(~ok).sum()} segmentos con NaN/inf: límpialos antes de entrenar")


def split_by_subject(subjects, val_frac: float = 0.15, test_frac: float = 0.15, seed: int = 0) -> dict:
    """Partición train/val/test donde ninguna persona aparece en dos conjuntos."""
    subjects = np.asarray(subjects).astype(str)
    uniq = np.unique(subjects)
    if len(uniq) < 3:
        raise ValueError("Se necesitan al menos 3 sujetos distintos para separar train/val/test")
    perm = np.random.default_rng(seed).permutation(uniq)
    n_test = max(1, int(round(len(uniq) * test_frac)))
    n_val = max(1, int(round(len(uniq) * val_frac)))
    groups = {"test": perm[:n_test], "val": perm[n_test:n_test + n_val], "train": perm[n_test + n_val:]}
    if len(groups["train"]) == 0:
        raise ValueError("Muy pocos sujetos para esas fracciones")
    out = {k: np.sort(np.flatnonzero(np.isin(subjects, v))) for k, v in groups.items()}
    for a in out:
        for b in out:
            if a < b:
                assert not set(subjects[out[a]]) & set(subjects[out[b]]), "fuga de sujetos entre conjuntos"
    return out


class BPWindowDataset(Dataset):
    """Cada item: (canales (3, 180) float32, objetivo normalizado (2,), índice).

    train=True : degradación y recorte aleatorios en cada acceso (aumento de datos).
    train=False: determinista (semilla por índice) y cacheado, para comparar épocas y modelos.
    """

    def __init__(self, raw: RawData, idx: np.ndarray, mu: np.ndarray, sd: np.ndarray, train: bool,
                 cfg: Optional[DegradeConfig] = None, seed: int = 0):
        self.raw, self.idx, self.mu, self.sd = raw, np.asarray(idx), np.asarray(mu, np.float32), np.asarray(sd, np.float32)
        self.train, self.cfg, self.seed = train, cfg or DegradeConfig(), seed
        self._cache: dict = {}

    def __len__(self):
        return len(self.idx)

    def targets_mmhg(self) -> np.ndarray:
        return np.stack([self.raw.sbp[self.idx], self.raw.dbp[self.idx]], 1).astype(np.float64)

    def subjects(self) -> np.ndarray:
        return self.raw.subject[self.idx]

    def _make(self, i: int) -> np.ndarray:
        rng = np.random.default_rng() if self.train else np.random.default_rng(self.seed * 1_000_003 + int(self.idx[i]))
        deg = degrade_ppg(self.raw.ppg[self.idx[i]], self.raw.fs, rng, self.cfg, FS_MODEL)
        return make_channels(crop_window(deg, WIN_N, rng if self.train else None))

    def __getitem__(self, i):
        if self.train:
            x = self._make(i)
        else:
            if i not in self._cache:
                self._cache[i] = self._make(i)
            x = self._cache[i]
        t = (np.array([self.raw.sbp[self.idx[i]], self.raw.dbp[self.idx[i]]], np.float32) - self.mu) / self.sd
        return torch.from_numpy(x), torch.from_numpy(t), i
