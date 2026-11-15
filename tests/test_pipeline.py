import json
import numpy as np
import pytest
import torch

from presion_arterial.config import FS_MODEL, WIN_N
from presion_arterial.data import split_by_subject
from presion_arterial.degrade import degrade_ppg, make_channels, crop_window
from presion_arterial.metrics import bp_metrics, calibrated_eval
from presion_arterial.model import BPNet
from presion_arterial.synthetic import synth_dataset
from presion_arterial.train import main as train_main
from presion_arterial.vitasense_adapter import DeepBPModel


def test_degrade_shape_and_band():
    d = synth_dataset(2, 2, seed=1)
    x = degrade_ppg(d["ppg"][0], d["fs"], np.random.default_rng(0))
    assert len(x) == int(8 * FS_MODEL) and np.isfinite(x).all()
    p = np.abs(np.fft.rfft(x)) ** 2
    f = np.fft.rfftfreq(len(x), 1 / FS_MODEL)
    assert p[(f >= 0.6) & (f <= 3.2)].sum() / p.sum() > 0.8     # energía casi toda en la banda del pulso


def test_channels_and_crop():
    c = make_channels(np.random.default_rng(0).standard_normal(240))
    assert c.shape == (3, 240) and np.allclose(c.mean(1), 0, atol=1e-5)
    assert len(crop_window(np.zeros(240))) == WIN_N
    with pytest.raises(ValueError):
        crop_window(np.zeros(10))


def test_split_has_no_subject_leak():
    subj = np.repeat([f"S{i}" for i in range(20)], 5)
    s = split_by_subject(subj, 0.2, 0.2, seed=3)
    sets = {k: set(subj[v]) for k, v in s.items()}
    assert not (sets["train"] & sets["val"]) and not (sets["train"] & sets["test"]) and not (sets["val"] & sets["test"])
    assert sum(len(v) for v in s.values()) == len(subj)


def test_model_forward():
    y = BPNet(base=8)(torch.randn(4, 3, WIN_N))
    assert y.shape == (4, 2)


def test_metrics_known_values():
    ref = np.array([100., 110, 120, 130])
    m = bp_metrics(ref + 5, ref)
    assert m["me"] == pytest.approx(5) and m["mae"] == pytest.approx(5) and m["sd"] == pytest.approx(0)
    assert m["within_5"] == 1.0 and m["bhs"] == "A"


def test_calibrated_eval_carries_reference():
    true = np.array([[120., 80]] * 4 + [[140., 90]] * 4)
    pred = true + 7
    subj = np.array(["a"] * 4 + ["b"] * 4)
    T, P, B = calibrated_eval(true, pred, subj, k=1)
    assert len(T) == 6 and np.allclose(P, T)           # un desfase constante se corrige exacto
    assert np.allclose(B[:3], [120, 80])                # el trivial arrastra la lectura de calibración


@pytest.fixture(scope="module")
def trained(tmp_path_factory):
    out = tmp_path_factory.mktemp("run")
    res = train_main(["--synthetic", "--n-subjects", "12", "--windows-per-subject", "12", "--epochs", "2",
                      "--batch-size", "32", "--base", "8", "--out", str(out)])
    return out, res


def test_train_smoke_outputs(trained):
    out, res = trained
    assert (out / "best.pt").exists() and (out / "splits.json").exists()
    m = json.loads((out / "metrics.json").read_text())
    assert {"sbp", "dbp"} <= set(m["results"]["test"])
    sp = json.loads((out / "splits.json").read_text())
    assert not set(sp["train"]) & set(sp["test"])


def test_adapter_vitasense_contract(trained):
    out, _ = trained
    model = DeepBPModel(str(out / "best.pt"))
    window = np.random.default_rng(0).random(750)       # contrato VitaSense: 6 s a 125 Hz
    sbp, dbp = model.predict({}, window)
    assert np.isfinite([sbp, dbp]).all() and 30 < sbp < 300
    sbp2, dbp2 = model.predict_pulse(np.random.default_rng(1).standard_normal(300), 30.0)   # 10 s a 30 Hz
    assert np.isfinite([sbp2, dbp2]).all()


def test_dashboard_embeds_real_results(trained):
    from presion_arterial.report import MARK, write_report
    out, _ = trained
    html = (out / "dashboard.html").read_text(encoding="utf-8")        # lo genera train.py
    assert MARK not in html and '"blocks"' in html and '"synthetic": true' in html
    ext = write_report(out, out / "otro.html")
    assert ext.exists()
