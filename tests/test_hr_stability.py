"""Synthetic regression tests for the research-only heart-rate estimator.

These tests verify spectral behavior, not accuracy on human volunteers.
"""
import numpy as np
from presion_arterial.hr_stability import estimate_hr


def _signal(bpm: float, seconds: float = 24., fs: int = 30):
    t = np.arange(0, seconds, 1 / fs)
    return np.sin(2 * np.pi * bpm / 60 * t), fs


def test_clean_72_bpm():
    pulse, fs = _signal(72)
    result = estimate_hr(pulse, fs)
    assert result.bpm is not None, result
    assert abs(result.bpm - 72) <= 2, result


def test_clean_120_bpm():
    pulse, fs = _signal(120)
    result = estimate_hr(pulse, fs)
    assert result.bpm is not None, result
    assert abs(result.bpm - 120) <= 2, result


def test_insufficient_window_is_unavailable():
    pulse, fs = _signal(72, seconds=11.)
    assert estimate_hr(pulse, fs).bpm is None


def test_disagreement_rejects_unstable_window():
    fs = 30
    t = np.arange(0, 24, 1 / fs)
    pulse = np.where(t < 12, np.sin(2 * np.pi * 70 / 60 * t),
                     np.sin(2 * np.pi * 140 / 60 * t))
    assert estimate_hr(pulse, fs).bpm is None


def test_flat_signal_is_unavailable():
    assert estimate_hr(np.ones(24 * 30), 30).bpm is None
