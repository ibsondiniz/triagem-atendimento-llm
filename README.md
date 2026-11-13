# Triagem de atendimento com LLM

> Classifies delivery-app customer messages with an LLM (Gemini or Ollama), extracts the order number and urgency, and measures accuracy on 100 labeled messages.

[![CI](https://github.com/ibsondiniz/triagem-atendimento-llm/actions/workflows/ci.yml/badge.svg)](https://github.com/ibsondiniz/triagem-atendimento-llm/actions/workflows/ci.yml)

Cada mensagem de cliente de um app de delivery vira três campos:
- **categoria**: atraso, pedido errado, item faltando, qualidade, reembolso, cancelamento, pagamento, elogio ou outro;
- **número do pedido**: só os dígitos, ou vazio se a mensagem não traz;
- **urgência**: alta, média ou baixa, com regras escritas no prompt.

O foco é **medir** e não só chamar a IA. O projeto traz 100 mensagens inventadas e rotuladas à mão e um avaliador. O avaliador mostra o acerto, a precisão e a revocação por categoria, as confusões mais comuns e cada erro.

```
$ triagem classificar "Fui cobrado duas vezes pelo pedido #249016!"
{
  "category": "pagamento",
  "order_id": "249016",
  "urgency": "alta"
}
```

## Resultados

| Classificador | Categoria | Urgência | Nº do pedido | Relatório |
|---|---|---|---|---|
| Regras por palavra-chave (linha de base) | 87% | 84% | 100% | [regras.md](reports/regras.md) |
| Gemini | _em breve_ | | | |

As regras foram escritas por quem montou as mensagens, então o acerto delas é otimista. Elas servem de piso para comparação e deixam rodar tudo sem internet. O LLM só vê o prompt, nunca os rótulos.

## Classificadores

| `--provider` | O que usa | Precisa de |
|---|---|---|
| `gemini` (padrão) | Google Gemini com saída JSON estruturada | `GEMINI_API_KEY` (plano grátis do Google AI Studio) |
| `ollama` | qualquer modelo local servido pelo Ollama | Ollama rodando, modelo baixado |
| `regras` | palavras-chave e expressões regulares | nada |

Os três seguem a mesma assinatura, `classify(texto) -> Triage`. Trocar de modelo não muda o resto do código.

## Como rodar

```bash
uv sync
cp .env.example .env   # cole a chave do Gemini em GEMINI_API_KEY
uv run --env-file .env triagem classificar "Meu pedido 551203 está atrasado"
uv run --env-file .env triagem avaliar --saida reports/gemini.md
uv run triagem avaliar --provider regras             # sem chave e sem internet
uv run triagem avaliar --provider ollama --modelo qwen3:4b
```

No Gemini grátis, o avaliador espera 4 s entre chamadas (`--pausa`) e tenta de novo quando a cota por minuto estoura.

Com Docker:

```bash
docker build -t triagem .
docker run --rm triagem                                     # linha de base, sem chave
docker run --rm --env-file .env triagem avaliar             # Gemini
```

## Testes

```bash
uv run pytest
uv run ruff check .
```

Nenhum teste chama um LLM de verdade. O CI roda com a linha de base e com um servidor Ollama simulado, então não gasta cota nem depende de chave.

## Como funciona

[COMO_FUNCIONA.md](COMO_FUNCIONA.md) explica o prompt, a saída estruturada, as métricas e as decisões de projeto.

## Autoria

Feito por Ibson Diniz com auxílio do Claude Code, a IA de programação da Anthropic. Eu defini as categorias, as regras de urgência e os rótulos, e revisei e testei o código.

Licença [MIT](LICENSE).
