"""Fast provisional rPPG followed by a quality-gated, longer-window estimate.

Spectral concentration/SNR and window agreement are *heuristics*, not validation.
No remote-camera method guarantees a 6–8 BPM error bound without ground truth.
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
    state: str = "unavailable"  # provisional | confirmed | unavailable


def _peak(signal: np.ndarray, fs: float) -> tuple[float, float, float] | None:
    """Interpolated spectral peak, fixed-width peak concentration, and SNR."""
    y = np.asarray(signal, dtype=float)
    if len(y) < round(7.5 * fs) or not np.isfinite(y).all() or np.std(y) < 1e-7:
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
    # Limit integration bandwidth so zero-padding does not increase the score by itself.
    halfwidth = max(0.12, 1.0 / (len(y) / fs))
    peak_bins = band & (np.abs(freq - f0) <= halfwidth)
    sig = float(power[peak_bins].sum())
    noise = float(power[band & ~peak_bins].sum())
    concentration = sig / (sig + noise + 1e-20)
    snr = float(10 * np.log10((sig + 1e-20) / (noise + 1e-20)))
    return f0 * 60.0, concentration, snr


def estimate_hr(pulse: np.ndarray, fs: float) -> SpectralEstimate:
    """Return a provisional update from ~9s or confirmed result from >=18s.

    Never turn a low-quality spectral peak into a numeric reading. Confirmation
    requires consensus of overlapping subwindows and their full-window estimate.
    Overlap is a consistency check, NOT an independent physiological validation.
    """
    signal = np.asarray(pulse, dtype=float)
    if not np.isfinite(fs) or fs <= 6 or not np.isfinite(signal).all():
        return SpectralEstimate(None, 0., float("-inf"), None, "Invalid pulse signal")
    if len(signal) < round(8.5 * fs):
        return SpectralEstimate(None, 0., float("-inf"), None, "Collecting pulse signal")
    quick = _peak(signal[-round(9 * fs):], fs)
    if quick is None:
        return SpectralEstimate(None, 0., float("-inf"), None, "No discernible pulse peak")

    # Early reading is deliberately labeled as provisional and uses stricter
    # minimum peak concentration than the old unconstrained raw FFT.
    provisional_ok = quick[1] >= 0.28 and quick[2] >= -3.0
    if len(signal) < round(18 * fs):
        return SpectralEstimate(quick[0] if provisional_ok else None, quick[1], quick[2],
                                None, "Early estimate; awaiting confirmation" if provisional_ok
                                else "Weak pulse peak", "provisional" if provisional_ok else "unavailable")

    recent = signal[-round(18 * fs):]
    whole = _peak(recent, fs)
    segment_n = round(12 * fs)
    first = _peak(recent[:segment_n], fs)
    last = _peak(recent[-segment_n:], fs)
    if whole is not None and first is not None and last is not None:
        disagreement = max(abs(first[0] - last[0]), abs(whole[0] - last[0]))
        if disagreement <= 12.0 and whole[1] >= 0.30 and whole[2] >= -2.5:
            return SpectralEstimate(whole[0], whole[1], whole[2], disagreement,
                                    "Consistent spectral estimate", "confirmed")
    else:
        disagreement = None

    # When long-window quality drops, keep *new* provisional values separate
    # from confirmed ones. The client will never label a hold as freshly confirmed.
    if provisional_ok:
        return SpectralEstimate(quick[0], quick[1], quick[2], disagreement,
                                "Confirmation pending; displaying provisional signal", "provisional")
    return SpectralEstimate(None, quick[1], quick[2], disagreement,
                            "Insufficient signal quality", "unavailable")
