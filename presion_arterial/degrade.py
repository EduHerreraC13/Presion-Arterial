"""Degradación de PPG de contacto para que se parezca a una señal rPPG de webcam.

Los datasets grandes con PA (MIMIC, VitalDB, PulseDB...) tienen PPG a ~125 Hz con morfología fina.
Una webcam entrega ~30 fps, pasa-banda 0,7-3 Hz, con ruido, movimiento y modulación respiratoria.
Entrenar sin degradar hace que el modelo aprenda detalles que la cámara nunca verá.

Esto SIMULA el dominio de la webcam; no lo reemplaza. La validación final debe hacerse con video real.
"""
from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from typing import Optional

import numpy as np
from scipy.signal import butter, resample_poly, sosfiltfilt

from .config import BAND_HZ, FS_MODEL, WIN_N

EPS = 1e-8


@dataclass
class DegradeConfig:
    snr_db: tuple = (4.0, 25.0)          # relación señal/ruido (ruido en banda, como en rPPG)
    motion_prob: float = 0.3             # prob. de que haya artefactos de movimiento
    motion_amp: tuple = (0.3, 1.5)       # amplitud del artefacto relativa a la señal
    resp_am_max: float = 0.3             # modulación de amplitud por respiración (máx.)


def zscore(x: np.ndarray) -> np.ndarray:
    return (x - x.mean(-1, keepdims=True)) / (x.std(-1, keepdims=True) + EPS)


def bandpass(x: np.ndarray, fs: float, lo: float = BAND_HZ[0], hi: float = BAND_HZ[1], order: int = 4) -> np.ndarray:
    sos = butter(order, [lo, hi], btype="bandpass", fs=fs, output="sos")
    return sosfiltfilt(sos, x, axis=-1)


def resample_to(x: np.ndarray, fs_in: float, fs_out: float) -> np.ndarray:
    """Remuestreo polifásico con filtro anti-alias."""
    x = np.asarray(x, float)
    if abs(fs_in - fs_out) < 1e-9:
        return x
    frac = Fraction(fs_out / fs_in).limit_denominator(1000)
    return resample_poly(x, frac.numerator, frac.denominator, axis=-1, padtype="line")


def degrade_ppg(ppg: np.ndarray, fs_in: float, rng: Optional[np.random.Generator] = None,
                cfg: Optional[DegradeConfig] = None, fs_out: float = FS_MODEL) -> np.ndarray:
    """PPG de contacto (fs_in) -> señal tipo rPPG de webcam (fs_out, pasa-banda, z-score)."""
    rng = rng or np.random.default_rng()
    cfg = cfg or DegradeConfig()
    x = zscore(np.asarray(ppg, float))
    x = resample_to(x, fs_in, fs_out)
    x = bandpass(x, fs_out)
    t = np.arange(len(x)) / fs_out

    # Modulación de amplitud respiratoria
    a = rng.uniform(0.0, cfg.resp_am_max)
    x = x * (1.0 + a * np.sin(2 * np.pi * rng.uniform(0.1, 0.4) * t + rng.uniform(0, 2 * np.pi)))

    # Artefactos de movimiento (ráfagas con envolvente gaussiana)
    if rng.random() < cfg.motion_prob:
        for _ in range(int(rng.integers(1, 3))):
            dur = rng.uniform(0.3, 1.5)
            t0 = rng.uniform(0.0, max(t[-1] - dur, 1e-3))
            env = np.exp(-0.5 * ((t - (t0 + dur / 2)) / (dur / 4)) ** 2)
            x = x + rng.uniform(*cfg.motion_amp) * env * np.sin(2 * np.pi * rng.uniform(0.5, 4.0) * t + rng.uniform(0, 2 * np.pi))

    # Ruido en banda a un SNR aleatorio
    snr = rng.uniform(*cfg.snr_db)
    noise = bandpass(rng.standard_normal(len(x)), fs_out, 0.5, 8.0)
    noise *= np.sqrt(np.mean(x ** 2) / (10 ** (snr / 10) * (np.mean(noise ** 2) + EPS)))
    x = bandpass(x + noise, fs_out)
    return zscore(x)


def make_channels(x: np.ndarray) -> np.ndarray:
    """(L,) -> (3, L): pulso, 1ª derivada, 2ª derivada; cada canal estandarizado."""
    p = zscore(np.asarray(x, float))
    v = np.gradient(p)
    a = np.gradient(v)
    return np.stack([p, zscore(v), zscore(a)]).astype(np.float32)


def crop_window(x: np.ndarray, n: int = WIN_N, rng: Optional[np.random.Generator] = None) -> np.ndarray:
    """Ventana de n muestras: aleatoria si hay rng, centrada si no."""
    if len(x) < n:
        raise ValueError(f"Segmento demasiado corto: {len(x)} < {n} muestras a {FS_MODEL} Hz")
    free = len(x) - n
    off = int(rng.integers(0, free + 1)) if rng is not None else free // 2
    return x[off:off + n]
