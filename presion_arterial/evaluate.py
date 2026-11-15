"""Validación EXTERNA: evalúa un checkpoint en un .npz de personas/datasets que no se usaron para entrenar.

    python -m presion_arterial.evaluate --ckpt runs/exp1/best.pt --data data/otro_dataset.npz
"""
from __future__ import annotations

import argparse
import json

import numpy as np
import torch

from .data import BPWindowDataset, load_npz
from .metrics import calibrated_eval, compare, format_report, to_jsonable, trivial_baseline
from .model import BPNet
from .train import predict


def main(argv=None) -> dict:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--ckpt", required=True)
    ap.add_argument("--data", required=True)
    ap.add_argument("--device", default="cpu")
    ap.add_argument("--json", help="guardar resultados en este .json")
    args = ap.parse_args(argv)

    ck = torch.load(args.ckpt, map_location=args.device, weights_only=True)
    model = BPNet(**ck["cfg"]).to(args.device); model.load_state_dict(ck["state_dict"])
    mu, sd = np.array(ck["mu"], np.float32), np.array(ck["sd"], np.float32)
    raw = load_npz(args.data)
    ds = BPWindowDataset(raw, np.arange(len(raw)), mu, sd, train=False)
    pred, true = predict(model, ds, torch.device(args.device), mu, sd), ds.targets_mmhg()

    res = {"all": compare(true, pred, trivial_baseline(mu, len(true)))}
    print(format_report(f"== Evaluación externa: {len(true)} ventanas, {len(set(raw.subject))} sujetos ==", res["all"]))
    cal = calibrated_eval(true, pred, ds.subjects(), k=1)
    if cal is not None:
        res["calibrated_1_reading"] = compare(*cal)
        print("\n" + format_report("== Con 1 lectura de tensiómetro por sujeto (trivial = arrastrar esa lectura) ==", res["calibrated_1_reading"]))
    if args.json:
        with open(args.json, "w", encoding="utf-8") as f:
            json.dump(to_jsonable(res), f, indent=2)
    return res


if __name__ == "__main__":
    main()
