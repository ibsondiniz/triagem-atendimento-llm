"""No test calls a real LLM: the CI runs offline with the keyword baseline and a faked Ollama server."""

import io
import json

import pytest

from triagem import core
from triagem.cli import main
from triagem.core import Triage, classify_rules, get_classifier
from triagem.evaluate import load, report, score


def test_dataset_is_complete_and_valid():
    rows = load()
    assert len(rows) == 100
    assert len({r["id"] for r in rows}) == 100
    for r in rows:
        Triage(category=r["category"], order_id=r["order_id"], urgency=r["urgency"])  # raises on a bad label
        if r["order_id"]:
            assert r["order_id"] in r["text"]


@pytest.mark.parametrize("text, category, order_id, urgency", [
    ("Fui cobrado duas vezes pelo pedido #123456!", "pagamento", "123456", "alta"),
    ("Entregador muito educado, parabéns", "elogio", None, "baixa"),
    ("Faltou o refrigerante, pedido 654321", "item_faltando", "654321", "media"),
    ("Qual o horário de funcionamento?", "outro", None, "baixa"),
])
def test_rules_baseline(text, category, order_id, urgency):
    assert classify_rules(text) == Triage(category=category, order_id=order_id, urgency=urgency)


def test_score_counts_hits_and_failures():
    rows = [
        {"id": 1, "text": "a", "category": "atraso", "order_id": "111111", "urgency": "alta"},
        {"id": 2, "text": "b", "category": "elogio", "order_id": None, "urgency": "baixa"},
        {"id": 3, "text": "c", "category": "pagamento", "order_id": None, "urgency": "media"},
    ]
    preds = [Triage(category="atraso", order_id="111111", urgency="media"), Triage(category="outro", urgency="baixa"), None]
    s = score(rows, preds)
    assert s["category_accuracy"] == pytest.approx(1 / 3)
    assert s["urgency_accuracy"] == pytest.approx(1 / 3)
    assert s["order_id_accuracy"] == pytest.approx(2 / 3)
    assert s["failed"] == 1
    assert s["per_category"]["atraso"] == {"n": 1, "precision": 1.0, "recall": 1.0, "f1": 1.0}
    assert [m[0] for m in s["mistakes"]] == [2, 3]
    md = report("teste", s, 1.0)
    assert "| Categoria | 33% |" in md and "| elogio | outro | 1 |" in md


def test_ollama_sends_schema_and_parses_answer(monkeypatch):
    sent = {}

    def fake_urlopen(req, timeout):
        sent.update(json.loads(req.data))
        answer = {"message": {"content": '{"category": "atraso", "order_id": "222222", "urgency": "media"}'}}
        return io.BytesIO(json.dumps(answer).encode())

    monkeypatch.setattr(core.urllib.request, "urlopen", fake_urlopen)
    classify = get_classifier("ollama", "modelo-teste")
    assert classify("pedido 222222 atrasado") == Triage(category="atraso", order_id="222222", urgency="media")
    assert sent["model"] == "modelo-teste" and sent["format"]["title"] == "Triage"
    assert sent["messages"][0]["content"] == core.PROMPT


def test_gemini_without_key_explains_what_to_do(monkeypatch):
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    with pytest.raises(SystemExit, match="GEMINI_API_KEY"):
        get_classifier("gemini")


def test_cli_classify_and_evaluate(tmp_path, capsys):
    main(["classificar", "Quero cancelar o pedido 333333", "--provider", "regras"])
    assert json.loads(capsys.readouterr().out)["category"] == "cancelamento"
    out = tmp_path / "regras.md"
    main(["avaliar", "--provider", "regras", "--saida", str(out)])
    assert "categoria" in capsys.readouterr().out
    assert out.read_text(encoding="utf-8").startswith("# Avaliação: regras")
