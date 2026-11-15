"""Genera el PANEL WEB de visualización con los resultados reales de una corrida.

    python -m presion_arterial.report --run runs/exp1
    python -m presion_arterial.report --run runs/exp1 --external runs/exp1/externa.json --out panel.html

El panel es un solo .html autocontenido (se abre con doble clic): los resultados se incrustan en la
plantilla `web/dashboard.html`, así que no hace falta servidor. `train.py` lo genera solo al terminar
(`<out>/dashboard.html`). Abierta sin datos, la plantilla muestra un ejemplo sintético.
"""
from __future__ import annotations

import argparse
import json
from datetime import datetime
from pathlib import Path

TEMPLATE = Path(__file__).parent / "web" / "dashboard.html"
MARK = "/*__DATA__*/null"


def build_payload(run, external=None) -> dict:
    run = Path(run)
    m = json.loads((run / "metrics.json").read_text(encoding="utf-8"))
    res, args = m["results"], m.get("args", {})
    blocks = [{"title": "Test: sujetos nunca vistos, sin calibrar", "res": res["test"]}]
    if "test_calibrated_1_reading" in res:
        blocks.append({"title": "Test con 1 lectura de tensiómetro por sujeto", "res": res["test_calibrated_1_reading"]})
    if external:
        e = json.loads(Path(external).read_text(encoding="utf-8"))
        blocks.append({"title": "Validación externa, sin calibrar", "res": e["all"]})
        if "calibrated_1_reading" in e:
            blocks.append({"title": "Validación externa con 1 lectura por sujeto", "res": e["calibrated_1_reading"]})
    sp = run / "splits.json"
    splits = {k: len(v) for k, v in json.loads(sp.read_text(encoding="utf-8")).items()} if sp.exists() else {}
    return {"run": run.name, "synthetic": bool(args.get("synthetic")), "data": args.get("data"),
            "epochs": args.get("epochs"), "splits": splits, "history": m.get("history", []),
            "blocks": blocks, "generated": datetime.now().strftime("%Y-%m-%d %H:%M")}


def render(payload: dict) -> str:
    html = TEMPLATE.read_text(encoding="utf-8")
    if html.count(MARK) != 1:
        raise RuntimeError("La plantilla no contiene el marcador de datos esperado")
    return html.replace(MARK, json.dumps(payload, ensure_ascii=False).replace("</", "<\\/"))


def write_report(run, out=None, external=None) -> Path:
    out = Path(out) if out else Path(run) / "dashboard.html"
    out.write_text(render(build_payload(run, external)), encoding="utf-8")
    return out


def main(argv=None) -> Path:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--run", required=True, help="carpeta de la corrida (con metrics.json)")
    ap.add_argument("--external", help="json de evaluate.py --json (validación externa)")
    ap.add_argument("--out", help="destino (por defecto <run>/dashboard.html)")
    a = ap.parse_args(argv)
    p = write_report(a.run, a.out, a.external)
    print(f"Panel generado: {p}")
    return p


if __name__ == "__main__":
    main()
