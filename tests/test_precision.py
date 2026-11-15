import numpy as np
import servidor_camara as mod


def payload(bpm=84, seconds=28, fps=30, noise=0.12):
    rng = np.random.default_rng(11)
    t = np.arange(0, seconds, 1 / fps)
    rois = []
    for _ in range(3):
        phase = 2 * np.pi * bpm / 60 * t
        rois.append(np.column_stack([
            110 + 1.7 * np.sin(phase) + rng.normal(0, noise, len(t)),
            112 + 0.7 * np.sin(phase + 0.2) + rng.normal(0, noise, len(t)),
            108 + 0.1 * np.sin(phase) + rng.normal(0, noise, len(t)),
        ]).tolist())
    return {'timestamps': t.tolist(), 'rgb': rois[0],
            'rois': {'left_cheek': rois[1], 'right_cheek': rois[2]}}


def test_three_region_synthetic_pulse():
    for bpm in (72, 84, 90, 120):
        r = mod.infer(payload(bpm))
        assert r['bpm'] is not None
        assert abs(r['bpm'] - bpm) < 3
        assert r['roi_count'] >= 2


def test_calibration_before_18_seconds():
    r = mod.infer(payload(seconds=12))
    assert r['status'] == 'calibrating' and r['bpm'] is None


def test_reject_uniform_signal():
    p = payload()
    for key in ('rgb',):
        p[key] = [[120, 120, 120] for _ in p[key]]
    for key in ('left_cheek', 'right_cheek'):
        p['rois'][key] = [[120, 120, 120] for _ in p['rois'][key]]
    r = mod.infer(p)
    assert r['bpm'] is None and r['status'] == 'no_evaluable'
