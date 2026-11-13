# Triagem de atendimento com LLM

> Classifies delivery-app customer messages with an LLM (Gemini or Ollama), extracts the order number and urgency, and measures accuracy on 100 labeled messages.

[![CI](https://github.com/ibsondiniz/triagem-atendimento-llm/actions/workflows/ci.yml/badge.svg)](https://github.com/ibsondiniz/triagem-atendimento-llm/actions/workflows/ci.yml)

Cada mensagem de cliente de um app de delivery vira três campos:
- **categoria**: atraso, pedido errado, item faltando, qualidade, reembolso, cancelamento, pagamento, elogio ou outro;
- **número do pedido**: só os dígitos, ou vazio se a mensagem não traz;
- **urgência**: alta, média ou baixa, com regras escritas no prompt.

O foco é **medir** e não só chamar a IA. O projeto traz 100 mensagens inventadas, cada uma com a resposta esperada, e um avaliador. O avaliador mostra o acerto, a precisão e a revocação por categoria, as confusões mais comuns e cada erro.

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
| Gemini 3.5 Flash-Lite, lotes de 10 mensagens | 100% | 84% | 100% | [gemini-flash-lite.md](reports/gemini-flash-lite.md) |

**O que os números mostram:**
- **Categoria.** O LLM acertou as 100. Numa rodada anterior, idêntica, acertou 97: errou dois pedidos errados por restrição alimentar (sem glúten, vegano), que tomou por problema de qualidade. Mesmo com temperatura 0 a resposta varia um pouco entre rodadas, então o número honesto é "97% a 100%".
- **Urgência.** Empatou com as regras. Quase todos os erros são o modelo dizendo **alta** onde o rótulo diz média: comida fria, cabelo no prato, "cancela urgente". O modelo é mais cauteloso que a regra escrita no prompt. Corrigir isso é trabalho de prompt e de rótulo (exemplos no prompt, critério mais claro), e o relatório lista cada caso.
- **Número do pedido.** Os dois acertam tudo. Extrair 6 dígitos é tarefa para regex; o LLM não é necessário aí.

As regras foram escritas por quem montou as mensagens, então o acerto delas é otimista. Elas servem de piso para comparação e deixam rodar tudo sem internet. O LLM só vê o prompt, nunca os rótulos.

**Por que lotes e Flash-Lite.** No plano grátis, o `gemini-3.5-flash` aceita só 20 chamadas por dia. Com `--lote 10`, as 100 mensagens viram 10 chamadas, numeradas, e o modelo devolve um item por número. A classificação de uma mensagem por vez (`triagem classificar`) continua usando o `gemini-3.5-flash`.

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
uv run --env-file .env triagem avaliar --modelo gemini-3.5-flash-lite --lote 10 --saida reports/gemini-flash-lite.md
uv run triagem avaliar --provider regras             # sem chave e sem internet
uv run triagem avaliar --provider ollama --modelo qwen3:4b
```

No Gemini grátis, o avaliador espera 4 s entre chamadas (`--pausa`), tenta de novo quando a cota por minuto estoura e para depois de 3 falhas seguidas, que costumam ser o limite diário.

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

Feito por Ibson Diniz com auxílio do Claude Code, a IA de programação da Anthropic. As mensagens e os rótulos são inventados para o projeto e estão em [data/mensagens.jsonl](data/mensagens.jsonl).

Licença [MIT](LICENSE).
