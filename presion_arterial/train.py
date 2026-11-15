"""Entrena y EVALÚA un modelo de PA (partición por sujeto, comparado siempre con el predictor trivial).

Ejemplos:
    python -m presion_arterial.train --data data/pulsedb.npz --epochs 30 --out runs/exp1
    python -m presion_arterial.train --synthetic --epochs 10 --out runs/demo      # solo prueba de humo
"""
from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

import numpy as np
import torch
from torch import nn
from torch.utils.data import DataLoader

from .config import FS_MODEL, IN_CH, WIN_N
from .data import BPWindowDataset, from_dict, load_npz, split_by_subject
from .metrics import bp_metrics, calibrated_eval, compare, format_report, to_jsonable, trivial_baseline
from .model import BPNet
from .synthetic import synth_dataset


def build_parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--data", help=".npz con ppg/sbp/dbp/subject/fs (ver data.py)")
    ap.add_argument("--synthetic", action="store_true", help="datos de juguete (solo prueba de humo)")
    ap.add_argument("--n-subjects", type=int, default=40)
    ap.add_argument("--windows-per-subject", type=int, default=60)
    ap.add_argument("--signal-strength", type=float, default=1.0, help="sintético: 0 = sin información de PA")
    ap.add_argument("--epochs", type=int, default=30)
    ap.add_argument("--batch-size", type=int, default=128)
    ap.add_argument("--lr", type=float, default=1e-3)
    ap.add_argument("--weight-decay", type=float, default=1e-2)
    ap.add_argument("--base", type=int, default=32, help="canales base de la red")
    ap.add_argument("--dropout", type=float, default=0.2)
    ap.add_argument("--val-frac", type=float, default=0.15)
    ap.add_argument("--test-frac", type=float, default=0.15)
    ap.add_argument("--workers", type=int, default=0)
    ap.add_argument("--device", default="auto")
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--out", default="runs/exp")
    return ap


@torch.no_grad()
def predict(model: nn.Module, ds: BPWindowDataset, device, mu, sd, batch_size=256, workers=0) -> np.ndarray:
    model.eval()
    P = []
    for x, _, _ in DataLoader(ds, batch_size=batch_size, shuffle=False, num_workers=workers):
        P.append(model(x.to(device)).cpu().numpy())
    return np.concatenate(P).astype(np.float64) * sd + mu


def main(argv=None) -> dict:
    args = build_parser().parse_args(argv)
    torch.manual_seed(args.seed); np.random.seed(args.seed)
    device = torch.device("cuda" if (args.device == "auto" and torch.cuda.is_available()) else ("cpu" if args.device == "auto" else args.device))

    if args.synthetic:
        raw = from_dict(synth_dataset(args.n_subjects, args.windows_per_subject, seed=args.seed, signal_strength=args.signal_strength))
        print("AVISO: datos SINTÉTICOS; los resultados no dicen nada sobre PA real.")
    elif args.data:
        raw = load_npz(args.data)
    else:
        raise SystemExit("Indica --data archivo.npz o --synthetic")

    split = split_by_subject(raw.subject, args.val_frac, args.test_frac, args.seed)
    tr_t = np.stack([raw.sbp[split["train"]], raw.dbp[split["train"]]], 1)
    mu, sd = tr_t.mean(0).astype(np.float32), (tr_t.std(0) + 1e-6).astype(np.float32)
    ds = {k: BPWindowDataset(raw, split[k], mu, sd, train=(k == "train"), seed=args.seed) for k in split}
    print(f"Ventanas: train {len(ds['train'])} | val {len(ds['val'])} | test {len(ds['test'])}   "
          f"(sujetos: {len(set(raw.subject[split['train']]))}/{len(set(raw.subject[split['val']]))}/{len(set(raw.subject[split['test']]))})   dispositivo: {device}")

    cfg = {"in_ch": IN_CH, "base": args.base, "n_blocks": [2, 2, 2], "dropout": args.dropout}
    model = BPNet(**cfg).to(device)
    opt = torch.optim.AdamW(model.parameters(), lr=args.lr, weight_decay=args.weight_decay)
    sched = torch.optim.lr_scheduler.CosineAnnealingLR(opt, T_max=max(args.epochs, 1))
    loss_fn = nn.SmoothL1Loss()
    loader = DataLoader(ds["train"], batch_size=args.batch_size, shuffle=True, num_workers=args.workers, drop_last=len(ds["train"]) > args.batch_size)

    out = Path(args.out); out.mkdir(parents=True, exist_ok=True)
    best, best_state, history = float("inf"), None, []
    t0 = time.time()
    for ep in range(1, args.epochs + 1):
        model.train(); tot = 0.0
        for x, y, _ in loader:
            x, y = x.to(device), y.to(device)
            opt.zero_grad(); loss = loss_fn(model(x), y); loss.backward()
            nn.utils.clip_grad_norm_(model.parameters(), 5.0); opt.step(); tot += loss.item() * len(x)
        sched.step()
        pv = predict(model, ds["val"], device, mu, sd, workers=args.workers)
        tv = ds["val"].targets_mmhg()
        mae = [bp_metrics(pv[:, j], tv[:, j])["mae"] for j in range(2)]
        score = float(np.mean(mae))
        history.append({"epoch": ep, "train_loss": tot / len(ds["train"]), "val_mae_sbp": mae[0], "val_mae_dbp": mae[1]})
        if score < best:
            best = score; best_state = {k: v.detach().cpu().clone() for k, v in model.state_dict().items()}
        print(f"época {ep:3d}/{args.epochs}  loss {tot / len(ds['train']):.4f}  val MAE SBP {mae[0]:5.1f} DBP {mae[1]:5.1f}   ({time.time() - t0:.0f}s)")

    model.load_state_dict(best_state)
    pt = predict(model, ds["test"], device, mu, sd, workers=args.workers)
    tt, subj = ds["test"].targets_mmhg(), ds["test"].subjects()
    res = {"test": compare(tt, pt, trivial_baseline(mu, len(tt)))}
    print("\n" + format_report("== TEST (sujetos nunca vistos), sin calibrar ==", res["test"]))
    cal = calibrated_eval(tt, pt, subj, k=1)
    if cal is not None:
        res["test_calibrated_1_reading"] = compare(*cal)
        print("\n" + format_report("== TEST con 1 lectura de tensiómetro por sujeto (trivial = arrastrar esa lectura) ==", res["test_calibrated_1_reading"]))
    print("\nSi el modelo no supera con claridad al trivial, NO aprendió PA a partir de la señal. (En modo calibrado, r sale inflado: mira la ganancia de MAE.)")

    torch.save({"state_dict": best_state, "cfg": cfg, "mu": mu.tolist(), "sd": sd.tolist(),
                "fs": FS_MODEL, "win_n": WIN_N}, out / "best.pt")
    (out / "metrics.json").write_text(json.dumps(to_jsonable({"args": vars(args), "results": res, "history": history}), indent=2), encoding="utf-8")
    (out / "splits.json").write_text(json.dumps({k: sorted(set(raw.subject[v].tolist())) for k, v in split.items()}, indent=2), encoding="utf-8")
    print(f"Guardado en {out}/ (best.pt, metrics.json, splits.json)")
    try:
        from .report import write_report
        print(f"Panel de visualización: {write_report(out)}  (ábrelo en el navegador)")
    except Exception as e:                       # el panel es accesorio: nunca debe romper el entrenamiento
        print(f"(No se pudo generar el panel: {e})")
    return res


if __name__ == "__main__":
    main()
