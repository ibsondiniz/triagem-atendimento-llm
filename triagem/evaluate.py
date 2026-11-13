"""Run a classifier over the labeled messages and score it: accuracy, per-category precision/recall/F1,
confusion matrix and the list of mistakes."""

import json
import time
from collections import Counter
from pathlib import Path

from triagem.core import CATEGORIES

DATASET = Path(__file__).resolve().parent.parent / "data" / "mensagens.jsonl"


def load(path=DATASET):
    return [json.loads(line) for line in Path(path).read_text(encoding="utf-8").splitlines() if line.strip()]


def predict_all(classify, rows, pause=0.0):
    """One prediction per row; a failed call becomes None instead of stopping the run."""
    preds, streak = [], 0
    for i, r in enumerate(rows):
        if i and pause:
            time.sleep(pause)  # ponytail: fixed pause for free-tier rate limits; a token bucket if this ever runs in parallel
        try:
            preds.append(classify(r["text"]))
            streak = 0
        except Exception as e:
            print(f"  erro na mensagem {r['id']}: {str(e)[:200]}")
            preds.append(None)
            streak += 1
            if streak == 3:  # likely a daily quota or an outage: stop instead of burning hours on retries
                raise SystemExit("3 falhas seguidas: avaliação interrompida.") from e
    return preds


def score(rows, preds):
    pairs = [(r, p) for r, p in zip(rows, preds)]
    cat = [(r["category"], p.category if p else "falhou") for r, p in pairs]
    n = len(rows)
    per_cat = {}
    for c in CATEGORIES:
        tp = sum(e == c and g == c for e, g in cat)
        pred_c = sum(g == c for _, g in cat)
        true_c = sum(e == c for e, _ in cat)
        prec = tp / pred_c if pred_c else 0.0
        rec = tp / true_c if true_c else 0.0
        f1 = 2 * prec * rec / (prec + rec) if prec + rec else 0.0
        per_cat[c] = {"n": true_c, "precision": prec, "recall": rec, "f1": f1}
    return {
        "n": n,
        "failed": sum(p is None for p in preds),
        "category_accuracy": sum(e == g for e, g in cat) / n,
        "urgency_accuracy": sum(bool(p) and p.urgency == r["urgency"] for r, p in pairs) / n,
        "order_id_accuracy": sum(bool(p) and p.order_id == r["order_id"] for r, p in pairs) / n,
        "per_category": per_cat,
        "confusion": Counter(cat),
        "mistakes": [(r["id"], r["text"], r["category"], g) for (r, _), (_, g) in zip(pairs, cat) if r["category"] != g],
    }


def pct(x):
    return f"{x * 100:.0f}%"


def report(label, s, seconds):
    lines = [
        f"# Avaliação: {label}",
        "",
        f"{s['n']} mensagens rotuladas, {seconds:.0f} s, {s['failed']} chamada(s) com falha.",
        "",
        "| Medida | Acerto |",
        "|---|---|",
        f"| Categoria | {pct(s['category_accuracy'])} |",
        f"| Urgência | {pct(s['urgency_accuracy'])} |",
        f"| Número do pedido | {pct(s['order_id_accuracy'])} |",
        "",
        "## Por categoria",
        "",
        "| Categoria | Mensagens | Precisão | Revocação | F1 |",
        "|---|---|---|---|---|",
        *[f"| {c} | {m['n']} | {pct(m['precision'])} | {pct(m['recall'])} | {m['f1']:.2f} |" for c, m in s["per_category"].items()],
        "",
        "## Confusões mais comuns",
        "",
        "| Esperado | Previsto | Vezes |",
        "|---|---|---|",
        *[f"| {e} | {g} | {k} |" for (e, g), k in s["confusion"].most_common() if e != g],
        "",
        "## Erros de categoria",
        "",
        "| # | Mensagem | Esperado | Previsto |",
        "|---|---|---|---|",
        *[f"| {i} | {t.replace('|', '/')} | {e} | {g} |" for i, t, e, g in s["mistakes"]],
        "",
    ]
    return "\n".join(lines)
