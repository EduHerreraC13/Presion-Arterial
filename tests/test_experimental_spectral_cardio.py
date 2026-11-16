"""Non-clinical regressions for the isolated spectral experiment branch.

These checks exercise synthetic pulse data and source-level UI contracts.
They do not establish BPM accuracy on real faces or robustness under motion.
"""
from pathlib import Path
import numpy as np
from presion_arterial.hr_stability import estimate_hr

ROOT = Path(__file__).resolve().parents[1]


def _tone(bpm=76, duration=24, fps=30, noise=0):
    t = np.arange(0, duration, 1 / fps)
    rng = np.random.default_rng(104)
    pulse = np.sin(2 * np.pi * bpm * t / 60)
    return pulse + noise * rng.standard_normal(len(t)), fps


def test_stable_76_bpm_confirms():
    signal, fs = _tone()
    r = estimate_hr(signal, fs)
    assert r.state == "confirmed", r
    assert abs(r.bpm - 76) <= 3, r


def test_spectral_signal_is_unavailable_too_early():
    signal, fs = _tone(duration=5)
    r = estimate_hr(signal, fs)
    assert r.state == "unavailable" and r.bpm is None


def test_flat_signal_cannot_become_valid():
    signal = np.ones(24 * 30)
    r = estimate_hr(signal, 30)
    assert r.state == "unavailable" and r.bpm is None


def test_large_frequency_switch_cannot_be_confirmed():
    fs = 30
    t = np.arange(0, 24, 1 / fs)
    signal = np.where(t < 12, np.sin(2 * np.pi * 70 / 60 * t),
                      np.sin(2 * np.pi * 140 / 60 * t))
    assert estimate_hr(signal, fs).state != "confirmed"


def test_face_rois_preserved_and_quality_gates_are_separate():
    ui = (ROOT / "camara_dashboard.html").read_text(encoding="utf-8")
    assert "const rows=3,cols=5" in ui
    assert "const cheeks=[" in ui
    assert "const weights={forehead:0.6,left:0.2,right:0.2}" in ui
    assert "MAX_MOTION_FACE_WIDTH" in ui
    assert "relativeMove>MAX_MOTION_FACE_WIDTH" in ui
    assert "mode:'spectral_experimental'" in ui
    assert "function chooseSpectralValue(" in ui
    assert "Two nearby quality-gated estimates" in ui
    assert "MEDIAN_PERIOD_MS=15000" in ui
    assert "if(isNew)addLiveReading" in ui


def test_server_maintains_old_live_and_new_experimental_paths():
    api = (ROOT / "servidor_camara.py").read_text(encoding="utf-8")
    assert "data.get('mode') == 'live'" in api
    assert "hr = estimate_hr(pulse, fs)" in api
    assert "if (confirmed or live_mode) and MODEL is not None" in api


def test_bilingual_experimental_labels():
    js = (ROOT / "heamon_i18n.js").read_text(encoding="utf-8")
    assert "Experimental Spectral Monitoring" in js
    assert "Held or rejected values are excluded" in js
