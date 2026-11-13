"""Usage:
  triagem classificar "texto da mensagem" [--provider gemini|ollama|regras]
  triagem avaliar [--provider ...] [--pausa 4] [--saida reports/gemini.md]
"""

import argparse
import sys
import time
from pathlib import Path

from triagem.core import get_classifier
from triagem.evaluate import load, pct, predict_all, report, score


def main(argv=None):
    sys.stdout.reconfigure(encoding="utf-8")
    p = argparse.ArgumentParser(prog="triagem", description="Triagem de mensagens de clientes de delivery.")
    sub = p.add_subparsers(dest="cmd", required=True)
    c = sub.add_parser("classificar", help="classifica uma mensagem")
    c.add_argument("texto")
    a = sub.add_parser("avaliar", help="mede o acerto nas mensagens rotuladas de data/mensagens.jsonl")
    a.add_argument("--pausa", type=float, default=None, help="segundos entre chamadas (padrão: 4 no gemini, 0 nos outros)")
    a.add_argument("--saida", help="grava o relatório em Markdown neste arquivo")
    a.add_argument("--lote", type=int, default=1, help="mensagens por chamada no Gemini (o plano grátis limita chamadas por dia)")
    for s in (c, a):
        s.add_argument("--provider", default="gemini", choices=["gemini", "ollama", "regras"])
        s.add_argument("--modelo", help="nome do modelo (padrão: GEMINI_MODEL ou OLLAMA_MODEL)")
    args = p.parse_args(argv)

    classify = get_classifier(args.provider, args.modelo)
    if args.cmd == "classificar":
        print(classify(args.texto).model_dump_json(indent=2))
        return

    rows = load()
    pause = args.pausa if args.pausa is not None else (4.0 if args.provider == "gemini" else 0.0)
    start = time.time()
    s = score(rows, predict_all(classify, rows, pause, args.lote))
    if args.lote > 1 and hasattr(classify, "many"):
        classify.label += f", lotes de {args.lote} mensagens"
    print(f"{classify.label}: categoria {pct(s['category_accuracy'])}, urgência {pct(s['urgency_accuracy'])}, "
          f"pedido {pct(s['order_id_accuracy'])}, falhas {s['failed']}")
    if args.saida:
        Path(args.saida).parent.mkdir(parents=True, exist_ok=True)
        Path(args.saida).write_text(report(classify.label, s, time.time() - start), encoding="utf-8")
        print(f"relatório em {args.saida}")
