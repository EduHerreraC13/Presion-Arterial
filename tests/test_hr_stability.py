"""Synthetic tests: fast provisional updates and strict confirmation.

These tests use idealized sine waves, not camera recordings or human reference data.
"""
import numpy as np
from presion_arterial.hr_stability import estimate_hr


def _signal(bpm: float, seconds: float = 24., fs: int = 30):
    t = np.arange(0, seconds, 1 / fs)
    return np.sin(2 * np.pi * bpm / 60 * t), fs


def test_clean_72_bpm_confirmed():
    pulse, fs = _signal(72)
    result = estimate_hr(pulse, fs)
    assert result.state == "confirmed", result
    assert abs(result.bpm - 72) <= 2, result


def test_clean_120_bpm_confirmed():
    pulse, fs = _signal(120)
    result = estimate_hr(pulse, fs)
    assert result.state == "confirmed", result
    assert abs(result.bpm - 120) <= 2, result


def test_quick_provisional_72_bpm():
    pulse, fs = _signal(72, seconds=10)
    result = estimate_hr(pulse, fs)
    assert result.state == "provisional", result
    assert abs(result.bpm - 72) <= 5, result


def test_not_ready_at_six_seconds():
    pulse, fs = _signal(72, seconds=6)
    result = estimate_hr(pulse, fs)
    assert result.state == "unavailable"
    assert result.bpm is None


def test_nine_second_low_fps_provisional():
    pulse, fs = _signal(72, seconds=10, fs=8)
    result = estimate_hr(pulse, fs)
    assert result.state == "provisional", result
    assert abs(result.bpm - 72) <= 6, result


def test_disagreement_cannot_be_confirmed():
    fs = 30
    t = np.arange(0, 24, 1 / fs)
    pulse = np.where(t < 12, np.sin(2 * np.pi * 70 / 60 * t),
                     np.sin(2 * np.pi * 140 / 60 * t))
    result = estimate_hr(pulse, fs)
    assert result.state != "confirmed", result


def test_flat_signal_is_unavailable():
    result = estimate_hr(np.ones(24 * 30), 30)
    assert result.state == "unavailable"
    assert result.bpm is None
