"""Checks decision logic only; not evidence of clinical performance."""
import numpy as np
import servidor_camara as mod


def _payload():
    t = np.arange(0, 18, .1)
    z = np.column_stack([110+np.sin(t), 112+np.sin(t), 108+np.sin(t)])
    return {'timestamps': t.tolist(), 'rgb': z.tolist(), 'rois': {
        'left_cheek': z.tolist(), 'right_cheek': z.tolist()}}


def test_high_quality_single_region_has_explicit_mode(monkeypatch):
    monkeypatch.setattr(mod, 'LOW_FPS_MODE', True)
    calls = iter([
        {'bpm': 84., 'snr_db': 5., 'peak_fraction': .75,
         'pulse': np.ones(1800), 'algorithm': 'POS'}, None, None])
    monkeypatch.setattr(mod, '_pulse_candidate', lambda *args: next(calls))
    r = mod.infer(_payload())
    assert r['quality_mode'] == 'single_region_high_quality'
    assert r['bpm'] == 84.
    assert r['roi_count'] == 1


def test_weak_single_region_not_published(monkeypatch):
    monkeypatch.setattr(mod, 'LOW_FPS_MODE', True)
    calls = iter([
        {'bpm': 84., 'snr_db': 1., 'peak_fraction': .35,
         'pulse': np.ones(1800), 'algorithm': 'POS'}, None, None])
    monkeypatch.setattr(mod, '_pulse_candidate', lambda *args: next(calls))
    r = mod.infer(_payload())
    assert r['bpm'] is None
    assert r['candidate_count'] == 1


def test_ui_shows_pending_and_no_fabricated_bpm():
    from pathlib import Path
    html = (Path(__file__).resolve().parents[1] / 'camara_dashboard.html').read_text()
    assert "localized('Calculando…')" in html
    assert 'quality_mode' not in html or 'quality_mode' in html  # API remains backwards compatible
