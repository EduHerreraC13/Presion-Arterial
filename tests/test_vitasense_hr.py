"""Smoke tests with synthetic RGB traces (NOT clinical accuracy tests)."""
import numpy as np
import servidor_camara as mod


def make_payload(bpm, fps=9.4, seconds=24, noise=.12):
    rng=np.random.default_rng(11)
    t=np.arange(0,seconds,1/fps)
    wave=2*np.pi*bpm/60*t
    traces=[]
    for _ in range(3):
        traces.append(np.column_stack([
            110+1.7*np.sin(wave)+rng.normal(0,noise,len(t)),
            112+0.7*np.sin(wave+.2)+rng.normal(0,noise,len(t)),
            108+0.1*np.sin(wave)+rng.normal(0,noise,len(t))]).tolist())
    return {'timestamps':t.tolist(),'rgb':traces[0],
            'rois':{'left_cheek':traces[1], 'right_cheek':traces[2]}}


def test_frequencies_9_fps():
    previous=mod.LOW_FPS_MODE
    mod.LOW_FPS_MODE=True
    try:
        for bpm in (72,84,90,120):
            result=mod.infer(make_payload(bpm))
            assert result['bpm'] is not None, (bpm,result)
            assert abs(result['bpm']-bpm)<3
            assert result['roi_count']>=2
    finally:
        mod.LOW_FPS_MODE=previous


def test_constant_rgb_not_accepted():
    previous=mod.LOW_FPS_MODE
    mod.LOW_FPS_MODE=True
    try:
        p=make_payload(84)
        for key in ('rgb',):p[key]=[[110,110,110] for _ in p[key]]
        for key in ('left_cheek','right_cheek'):
            p['rois'][key]=[[110,110,110] for _ in p['rois'][key]]
        r=mod.infer(p)
        assert r['bpm'] is None
    finally:
        mod.LOW_FPS_MODE=previous
