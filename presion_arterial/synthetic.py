"""Datos SINTÉTICOS de juguete, solo para probar que el pipeline funciona.

Los resultados sobre estos datos NO dicen nada sobre PA real. La morfología del pulso se hace
depender de la PA de forma inventada (`signal_strength`); con 0 la señal no contiene información
de PA, y un buen pipeline NO debe superar al predictor trivial.
"""
from __future__ import annotations

import numpy as np


def _beat_shape(p, sbp, dbp, strength, shift):
    s = (sbp - 120.0) / 20.0 * strength
    d = (dbp - 75.0) / 12.0 * strength
    ps = 0.20 - 0.025 * s + shift
    ws = max(0.07 - 0.008 * s, 0.03)
    pr = ps + 0.28 - 0.06 * s
    ar = float(np.clip(0.45 - 0.10 * s - 0.05 * d, 0.05, 0.9))
    return np.exp(-0.5 * ((p - ps) / ws) ** 2) + ar * np.exp(-0.5 * ((p - pr) / 0.10) ** 2)


def synth_dataset(n_subjects: int = 40, windows_per_subject: int = 60, fs: float = 125.0,
                  seg_s: float = 8.0, seed: int = 0, signal_strength: float = 1.0):
    """Devuelve dict con ppg (N, L) float32, sbp, dbp, subject (str), fs."""
    rng = np.random.default_rng(seed)
    n = int(seg_s * fs)
    ppg, sbp_l, dbp_l, subj = [], [], [], []
    for s in range(n_subjects):
        sb, db = rng.normal(122, 14), rng.normal(76, 9)
        hr0, shift = rng.uniform(55, 100), rng.normal(0.0, 0.015)   # rasgos del sujeto no ligados a la PA
        for _ in range(windows_per_subject):
            sbp = sb + rng.normal(0, 8)
            dbp = db + 0.45 * (sbp - sb) + rng.normal(0, 3)
            hr = hr0 + rng.normal(0, 5)
            wiggle = np.convolve(rng.standard_normal(n), np.ones(int(fs)) / fs, mode="same") * np.sqrt(fs)
            phase = np.cumsum(hr / 60.0 * (1 + 0.04 * wiggle)) / fs + rng.uniform()
            x = _beat_shape(phase % 1.0, sbp, dbp, signal_strength, shift) + 0.02 * rng.standard_normal(n)
            ppg.append(x.astype(np.float32)); sbp_l.append(sbp); dbp_l.append(dbp); subj.append(f"S{s:03d}")
    return {"ppg": np.stack(ppg), "sbp": np.array(sbp_l, np.float32), "dbp": np.array(dbp_l, np.float32),
            "subject": np.array(subj), "fs": float(fs)}
