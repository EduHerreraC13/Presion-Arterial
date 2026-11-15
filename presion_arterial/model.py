"""ResNet 1D para regresión de PA (SBP, DBP) desde una ventana de pulso de 6 s a 30 Hz."""
from __future__ import annotations

import torch
from torch import nn

from .config import IN_CH


class ResBlock1D(nn.Module):
    def __init__(self, cin: int, cout: int, stride: int = 1, k: int = 5, p_drop: float = 0.0):
        super().__init__()
        self.c1 = nn.Conv1d(cin, cout, k, stride, k // 2, bias=False)
        self.b1 = nn.BatchNorm1d(cout)
        self.c2 = nn.Conv1d(cout, cout, k, 1, k // 2, bias=False)
        self.b2 = nn.BatchNorm1d(cout)
        self.drop = nn.Dropout(p_drop)
        self.act = nn.ReLU(inplace=True)
        self.skip = None if (cin == cout and stride == 1) else nn.Sequential(
            nn.Conv1d(cin, cout, 1, stride, bias=False), nn.BatchNorm1d(cout))

    def forward(self, x):
        y = self.drop(self.act(self.b1(self.c1(x))))
        y = self.b2(self.c2(y))
        return self.act(y + (x if self.skip is None else self.skip(x)))


class BPNet(nn.Module):
    """Entrada (B, in_ch, 180) -> salida (B, 2) = [SBP, DBP] normalizados (ver checkpoint: mu, sd)."""

    def __init__(self, in_ch: int = IN_CH, base: int = 32, n_blocks=(2, 2, 2), dropout: float = 0.2, out_dim: int = 2):
        super().__init__()
        self.stem = nn.Sequential(nn.Conv1d(in_ch, base, 7, 1, 3, bias=False), nn.BatchNorm1d(base), nn.ReLU(inplace=True))
        blocks, cin = [], base
        for i, nb in enumerate(n_blocks):
            cout = base * 2 ** i
            for j in range(nb):
                blocks.append(ResBlock1D(cin, cout, stride=2 if (j == 0 and i > 0) else 1, p_drop=dropout / 2))
                cin = cout
        self.body = nn.Sequential(*blocks)
        self.head = nn.Sequential(nn.Dropout(dropout), nn.Linear(2 * cin, 64), nn.ReLU(inplace=True), nn.Linear(64, out_dim))

    def forward(self, x):
        h = self.body(self.stem(x))
        return self.head(torch.cat([h.mean(-1), h.amax(-1)], dim=1))
