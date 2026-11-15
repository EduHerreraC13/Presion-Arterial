"""Métricas de PA, comparación contra el predictor trivial y evaluación con calibración por sujeto."""
from __future__ import annotations

import numpy as np

NAMES = ("sbp", "dbp")


def bhs_grade(w5: float, w10: float, w15: float) -> str:
    """Clasificación de la British Hypertension Society según % de error absoluto <= 5/10/15 mmHg."""
    if w5 >= .60 and w10 >= .85 and w15 >= .95:
        return "A"
    if w5 >= .50 and w10 >= .75 and w15 >= .90:
        return "B"
    if w5 >= .40 and w10 >= .65 and w15 >= .85:
        return "C"
    return "D"


def bp_metrics(pred, ref) -> dict:
    pred, ref = np.asarray(pred, float), np.asarray(ref, float)
    e = pred - ref
    n = len(e)
    me = float(e.mean())
    sd = float(e.std(ddof=1)) if n > 1 else float("nan")
    r = float(np.corrcoef(pred, ref)[0, 1]) if n > 2 and pred.std() > 0 and ref.std() > 0 else float("nan")
    w = {k: float((np.abs(e) <= k).mean()) for k in (5, 10, 15)}
    return {"n": n, "me": me, "sd": sd, "mae": float(np.abs(e).mean()), "rmse": float(np.sqrt((e ** 2).mean())),
            "r": r, "within_5": w[5], "within_10": w[10], "within_15": w[15],
            "bhs": bhs_grade(w[5], w[10], w[15]), "aami": bool(abs(me) <= 5 and sd <= 8)}   # criterio 5 ± 8 mmHg


MIN_GAIN_MMHG = 1.0   # una mejora menor que esto en MAE se considera ruido, no evidencia


def compare(true, pred, baseline, min_gain: float = MIN_GAIN_MMHG) -> dict:
    """Modelo vs. predictor trivial, por separado para SBP y DBP (arrays (n, 2) en mmHg).

    `beats_baseline` exige una ganancia de MAE mayor que `min_gain` mmHg (y >5 % del MAE trivial):
    ganar por décimas de mmHg es ruido.
    """
    out = {}
    for j, nm in enumerate(NAMES):
        m, b = bp_metrics(pred[:, j], true[:, j]), bp_metrics(baseline[:, j], true[:, j])
        gain = b["mae"] - m["mae"]
        out[nm] = {"model": m, "baseline": b, "mae_gain": gain,
                   "beats_baseline": bool(gain > max(min_gain, 0.05 * b["mae"]))}
    return out


def trivial_baseline(train_mean, n: int) -> np.ndarray:
    return np.tile(np.asarray(train_mean, float), (n, 1))


def calibrated_eval(true, pred, subjects, k: int = 1):
    """Simula UNA lectura de tensiómetro por persona (las k primeras ventanas) para calibrar el desfase.

    Modelo calibrado : pred + (media(ref_k) - media(pred_k))
    Referencia justa : 'arrastrar' la lectura del tensiómetro (media(ref_k)) sin usar la señal.
    Si el modelo no supera a esa referencia, la señal no aporta nada sobre la PA de calibración.
    OJO: en este modo la correlación r sale inflada (la varianza entre sujetos entra por la lectura de
    calibración); fíjate en la ganancia de MAE, no en r.
    Devuelve (true, pred_cal, base_cal) sobre las ventanas restantes, o None si no hay datos.
    """
    true, pred, subjects = np.asarray(true, float), np.asarray(pred, float), np.asarray(subjects)
    T, P, B = [], [], []
    for s in np.unique(subjects):
        ii = np.flatnonzero(subjects == s)
        if len(ii) <= k:
            continue
        cal, rest = ii[:k], ii[k:]
        ref0 = true[cal].mean(0)
        P.append(pred[rest] + (ref0 - pred[cal].mean(0)))
        B.append(np.tile(ref0, (len(rest), 1)))
        T.append(true[rest])
    if not T:
        return None
    return np.concatenate(T), np.concatenate(P), np.concatenate(B)


def to_jsonable(o):
    if isinstance(o, dict):
        return {k: to_jsonable(v) for k, v in o.items()}
    if isinstance(o, (list, tuple)):
        return [to_jsonable(v) for v in o]
    if isinstance(o, (np.floating, float)):
        return None if not np.isfinite(o) else float(o)
    if isinstance(o, (np.integer,)):
        return int(o)
    if isinstance(o, np.ndarray):
        return to_jsonable(o.tolist())
    return o


def format_report(title: str, res: dict) -> str:
    lines = [title]
    for nm in NAMES:
        m, b = res[nm]["model"], res[nm]["baseline"]
        lines.append(f"  {nm.upper()}  modelo : ME {m['me']:+6.1f} ± {m['sd']:5.1f}  MAE {m['mae']:5.1f}  r {m['r']:5.2f}  "
                     f"BHS {m['bhs']}  5±8 mmHg: {'cumple' if m['aami'] else 'NO cumple'}")
        lines.append(f"       trivial: ME {b['me']:+6.1f} ± {b['sd']:5.1f}  MAE {b['mae']:5.1f}")
        lines.append(f"       ¿supera al trivial con margen claro (> {MIN_GAIN_MMHG:g} mmHg)? {'SÍ' if res[nm]['beats_baseline'] else 'NO'}  (ganancia de MAE: {res[nm]['mae_gain']:+.2f} mmHg)")
    return "\n".join(lines)
