"""Regression checks: live cardio API, median UI, and preserved facial ROIs."""
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parents[1]


def test_live_api_supports_continuous_spectral_estimates():
    from servidor_camara import infer
    t = np.arange(0, 12, 1 / 30.0)
    phase = 2 * np.pi * 1.2 * t
    rgb = np.column_stack((
        125 + 1.2 * np.sin(phase),
        105 + 0.7 * np.sin(phase + 0.6),
        115 + 0.5 * np.cos(phase),
    ))
    result = infer({"mode": "live", "timestamps": t.tolist(), "rgb": rgb.tolist()})
    assert result["hr_state"] == "live"
    assert 45 <= result["bpm"] <= 180
    assert 0 <= result["peak_fraction"] <= 1
    assert result["sbp"] is None and result["dbp"] is None


def test_live_and_median_readouts_are_separate_and_labeled():
    html = (ROOT / "camara_dashboard.html").read_text(encoding="utf-8")
    assert "mode:'live'" in html
    assert "MEDIAN_PERIOD_MS=15000" in html
    assert "samples.slice(-800)" in html
    for element in ("bpm", "quality", "sbp", "dbp",
                    "medianBpm", "medianQuality", "medianSbp", "medianDbp"):
        assert f'id="{element}"' in html
    for message in ("Monitoreo en tiempo real",
                    "mediana cada 15 segundos",
                    "no indica exactitud"):
        assert message in html


def test_forehead_and_cheek_rois_are_preserved():
    html = (ROOT / "camara_dashboard.html").read_text(encoding="utf-8")
    assert "const rows=3,cols=5" in html
    assert "const cheeks=[" in html
    assert "const weights={forehead:0.6,left:0.2,right:0.2}" in html


def test_second_tab_heading_has_valid_span():
    html = (ROOT / "fatiga_respiracion.html").read_text(encoding="utf-8")
    assert '<h1>YanqhayCare <span style="color:var(--muted);font-weight:400">' in html
    assert 'YanqhayCare span style=' not in html
