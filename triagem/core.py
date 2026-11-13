"""Triage of delivery-app customer messages: category, order number and urgency.

Three interchangeable providers share one signature, `classify(text) -> Triage`:
  regras  keyword baseline, no network; used by the tests and CI
  gemini  Google Gemini with structured JSON output (needs GEMINI_API_KEY)
  ollama  any local model served by Ollama
"""

import json
import os
import re
import time
import urllib.request
from typing import Literal

from pydantic import BaseModel, Field

Category = Literal["atraso", "pedido_errado", "item_faltando", "qualidade", "reembolso", "cancelamento", "pagamento", "elogio", "outro"]
Urgency = Literal["alta", "media", "baixa"]
CATEGORIES = list(Category.__args__)


class Triage(BaseModel):
    category: Category
    order_id: str | None = Field(None, description="Número do pedido, só os dígitos; null se a mensagem não traz")
    urgency: Urgency


PROMPT = """Você faz a triagem das mensagens de clientes de um app de delivery de comida e mercado.
Responda só com o JSON pedido.

category, o problema principal da mensagem:
- atraso: pedido atrasado, que não chegou ou foi marcado como entregue sem chegar
- pedido_errado: veio item, sabor, tamanho ou pedido diferente do escolhido
- item_faltando: o pedido chegou, mas faltou algum item ou quantidade
- qualidade: comida fria, estragada, crua, amassada, vazada, com corpo estranho ou embalagem violada
- reembolso: o cliente pergunta pelo estorno ou pede o dinheiro de volta, e esse é o assunto principal
- cancelamento: o cliente quer cancelar ou pergunta por que um pedido ou assinatura foi cancelado
- pagamento: cobrança, cartão, Pix, cupom, taxa ou forma de pagamento
- elogio: agradecimento ou elogio
- outro: dúvidas e pedidos que não se encaixam acima (conta, horário, cadastro, sugestão)

order_id: o número do pedido citado na mensagem, só os dígitos (sem #). null se não houver.

urgency:
- alta: atraso acima de 1 hora; pedido marcado como entregue sem chegar; risco à saúde (alergia, intolerância,
  diabetes, comida estragada que foi consumida); cobrança duplicada ou não reconhecida; ameaça de Procon,
  processo ou reclamação pública
- baixa: elogio, dúvida ou sugestão sem problema acontecendo, ou aviso que não pede nenhuma ação
- media: todo o resto"""


# --- regras: keyword baseline -------------------------------------------------------------

RULES = [  # first match wins, so the order matters
    ("elogio", r"parab|agradec|obrigad|excelente|nota 10|adorei|perfeito|muito bom|atencios|melhor"),
    ("reembolso", r"reembolso|estorno|dinheiro de volta|valor de volta"),
    ("cancelamento", r"cancel"),
    ("pagamento", r"cobra|cart[ãa]o|cupom|\bpix\b|pagamento|\bpag[oa]\b|paguei|taxa|vale-refei|fatura|gorjeta"),
    ("qualidade", r"\bfri[ao]\b|\bcru\b|estragad|mofo|cabelo|amassad|derretid|vazou|lacre|pl[áa]stico|murch|cheiro|dor de barriga|passou mal"),
    ("item_faltando", r"faltou|faltaram|faltando|n[ãa]o veio|veio s[óo]|vieram s[óo]|veio sem|chegou sem"),
    ("pedido_errado", r"errad|troca|outra pessoa|diferente|de outro|veio .{0,40}\b(pedi|eu pedi)\b"),
    ("atraso", r"atras|cad[êe]|n[ãa]o chegou|demor|a caminho|previs[ãa]o|parad|n[ãa]o recebi"),
]
HIGH = (r"procon|reclame aqui|processo|al[ée]rgic|alergia|cel[íi]ac|diab[ée]tic|passou mal|dor de barriga|duas vezes|"
        r"n[ãa]o reconhe[çc]o|\b[2-9] ?h(oras)? de atraso|\b1h[1-5]\d|marcou como entregue")


def classify_rules(text: str) -> Triage:
    t = text.lower()
    category = next((c for c, p in RULES if re.search(p, t)), "outro")
    order = re.search(r"\b\d{6}\b", text)
    urgency = "alta" if re.search(HIGH, t) else "baixa" if category in ("elogio", "outro") or "só avisando" in t else "media"
    return Triage(category=category, order_id=order and order.group(0), urgency=urgency)


# --- gemini -------------------------------------------------------------------------------

def gemini_classifier(model: str | None = None):
    from google import genai
    from google.genai import errors, types

    if not os.environ.get("GEMINI_API_KEY"):
        raise SystemExit("Defina GEMINI_API_KEY (chave grátis no Google AI Studio) ou use --provider regras.")
    client = genai.Client()  # reads GEMINI_API_KEY
    model = model or os.environ.get("GEMINI_MODEL", "gemini-3.5-flash")
    config = types.GenerateContentConfig(
        system_instruction=PROMPT, response_mime_type="application/json", response_schema=Triage, temperature=0,
        thinking_config=types.ThinkingConfig(thinking_level="low"),  # a label needs no long reasoning; default thinking timed out
        http_options=types.HttpOptions(timeout=90_000))

    def classify(text: str) -> Triage:
        for attempt in range(4):
            try:
                return client.models.generate_content(model=model, contents=text, config=config).parsed
            except errors.APIError as e:
                if e.code not in (429, 503) or attempt == 3:  # free-tier rate limit or "high demand": worth waiting
                    raise
                time.sleep(30 * (attempt + 1))

    classify.label = f"gemini ({model})"
    return classify


# --- ollama -------------------------------------------------------------------------------

def ollama_classifier(model: str | None = None):
    url = os.environ.get("OLLAMA_URL", "http://localhost:11434") + "/api/chat"
    model = model or os.environ.get("OLLAMA_MODEL", "qwen3:4b")

    def classify(text: str) -> Triage:
        body = {"model": model, "stream": False, "format": Triage.model_json_schema(), "options": {"temperature": 0},
                "messages": [{"role": "system", "content": PROMPT}, {"role": "user", "content": text}]}
        req = urllib.request.Request(url, json.dumps(body).encode(), {"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=120) as r:
            return Triage.model_validate_json(json.load(r)["message"]["content"])

    classify.label = f"ollama ({model})"
    return classify


def get_classifier(provider: str, model: str | None = None):
    if provider == "regras":
        classify_rules.label = "regras (palavras-chave)"
        return classify_rules
    return {"gemini": gemini_classifier, "ollama": ollama_classifier}[provider](model)
