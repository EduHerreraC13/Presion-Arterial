"""Research-only rPPG heart-rate estimator using VitaSense-style spectral tracking.

The camera-derived optical signal is not a clinical heart-rate measurement.
"""
from __future__ import annotations

from dataclasses import dataclass
import numpy as np


@dataclass(frozen=True)
class SpectralEstimate:
    bpm: float | None
    peak_fraction: float
    snr_db: float
    agreement_bpm: float | None
    reason: str


def _peak(signal: np.ndarray, fs: float) -> tuple[float, float, float] | None:
    """Return interpolated BPM, peak power fraction, spectral SNR in the HR band."""
    y = np.asarray(signal, dtype=float)
    if len(y) < round(8 * fs) or not np.isfinite(y).all() or np.std(y) < 1e-7:
        return None
    y = (y - y.mean()) * np.hanning(len(y))
    nfft = max(4096, 1 << int(np.ceil(np.log2(len(y) * 4))))
    power = np.abs(np.fft.rfft(y, n=nfft)) ** 2
    freq = np.fft.rfftfreq(nfft, 1 / fs)
    band = (freq >= 0.75) & (freq <= 3.0)
    ids = np.flatnonzero(band)
    if len(ids) < 3:
        return None
    i = int(ids[np.argmax(power[band])])
    log_power = np.log(power + 1e-20)
    den = log_power[i - 1] - 2 * log_power[i] + log_power[i + 1]
    delta = float(np.clip(0.5 * (log_power[i - 1] - log_power[i + 1]) / den, -1, 1)) if abs(den) > 1e-12 else 0.
    f0 = float(freq[i] + delta * (freq[1] - freq[0]))
    # Fixed-width frequency neighborhoods: zero padding must not inflate quality.
    # A 0.12 Hz half-width is approximately the main lobe for an ~18 s window.
    halfwidth = max(0.12, 1.0 / (len(y) / fs))
    signal_bins = band & (np.abs(freq - f0) <= halfwidth)
    noise_bins = band & ~signal_bins
    sig = float(power[signal_bins].sum())
    noise = float(power[noise_bins].sum())
    total = sig + noise
    fraction = sig / (total + 1e-20)
    snr = float(10 * np.log10((sig + 1e-20) / (noise + 1e-20)))
    return f0 * 60, fraction, snr


def estimate_hr(pulse: np.ndarray, fs: float) -> SpectralEstimate:
    """Require agreement between overlapping windows; reject ambiguous BPM changes.

    Run on the latest 18 s only. Two 12 s estimates share six seconds; this is
    an internal consistency check, NOT independent validation of physiological HR.
    """
    signal = np.asarray(pulse, dtype=float)
    if not np.isfinite(fs) or fs <= 6 or len(signal) < round(18 * fs):
        return SpectralEstimate(None, 0., float("-inf"), None, "Need 18 seconds of continuous signal")
    signal = signal[-round(18 * fs):]
    whole = _peak(signal, fs)
    half = round(12 * fs)
    first, last = _peak(signal[:half], fs), _peak(signal[-half:], fs)
    if whole is None or first is None or last is None:
        return SpectralEstimate(None, 0., float("-inf"), None, "Insufficient pulse signal")
    bpm, fraction, snr = whole
    disagreement = abs(first[0] - last[0])
    if disagreement > 15.:
        return SpectralEstimate(None, fraction, snr, disagreement, "Inconsistent pulse peaks across windows")
    # Spectral concentration is a heuristic; never report it as accuracy.
    if fraction < 0.25 or snr < -4.:
        return SpectralEstimate(None, fraction, snr, disagreement, "Weak or ambiguous pulse peak")
    return SpectralEstimate(float(bpm), fraction, snr, disagreement, "Experimental HR estimate")
