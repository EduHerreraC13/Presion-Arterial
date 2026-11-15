"""Conecta un checkpoint entrenado con VitaSense (https://github.com/braytwing/VitaSense).

`DeepBPModel` cumple la interfaz `BPModel` de `rppg/bp.py` (predict(feats, window) -> (sbp, dbp)),
así que se pasa directamente a `BloodPressureEstimator`:

    from presion_arterial.vitasense_adapter import DeepBPModel
    from rppg import BloodPressureEstimator, BPCalibration

    model = DeepBPModel("runs/exp1/best.pt")
    est = BloodPressureEstimator(model, BPCalibration(sbp_offset=..., dbp_offset=...))
    # y agrega `est` a la lista de estimadores de RPPGPipeline

VitaSense solo muestra un número si hay modelo Y calibración por sujeto; eso se mantiene.
Sin validación externa con video real, la salida NO debe interpretarse como una medición.
"""
from __future__ import annotations

import numpy as np
import torch

from .config import FS_MODEL, WIN_N
from .degrade import make_channels, resample_to
from .model import BPNet


class DeepBPModel:
    def __init__(self, ckpt_path: str, device: str = "cpu"):
        ck = torch.load(ckpt_path, map_location=device, weights_only=True)
        self.device = device
        self.net = BPNet(**ck["cfg"]).to(device)
        self.net.load_state_dict(ck["state_dict"])
        self.net.eval()
        self.mu, self.sd = np.array(ck["mu"], float), np.array(ck["sd"], float)

    @torch.no_grad()
    def predict_pulse(self, pulse: np.ndarray, fs: float) -> tuple[float, float]:
        """Señal de pulso rPPG filtrada (p. ej. `ctx.pulse`) a `fs` Hz -> (sbp, dbp) en mmHg SIN calibrar."""
        x = resample_to(np.asarray(pulse, float), fs, FS_MODEL)
        if len(x) < WIN_N:
            raise ValueError(f"Se necesitan >= {WIN_N / FS_MODEL:.0f} s de pulso; hay {len(pulse) / fs:.1f} s")
        t = torch.from_numpy(make_channels(x[-WIN_N:]))[None].to(self.device)
        out = self.net(t).cpu().numpy()[0] * self.sd + self.mu
        return float(out[0]), float(out[1])

    def predict(self, feats, window):
        """Contrato de VitaSense: `window` = 750 muestras (6 s a 125 Hz), normalizadas min-max."""
        return self.predict_pulse(np.asarray(window, float), 125.0)
