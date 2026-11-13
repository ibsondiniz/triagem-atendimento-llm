# Como funciona

Resumo para estudar antes de uma entrevista técnica.

## 1. Peças

```
triagem/core.py       modelo de saída (Triage), prompt e os três classificadores
triagem/evaluate.py   carrega as mensagens rotuladas, roda o classificador e calcula as métricas
triagem/cli.py        comandos "classificar" e "avaliar"
data/mensagens.jsonl  100 mensagens inventadas, uma por linha, com categoria, nº do pedido e urgência
reports/              relatórios gerados pelo avaliador
```

## 2. Saída estruturada

A classe `Triage` (Pydantic) define o formato da resposta:
- `category` só aceita uma das 9 categorias;
- `urgency` só aceita alta, media ou baixa;
- `order_id` é texto ou nulo.

- **No Gemini**, a classe vai em `response_schema`. A API devolve JSON que já segue o esquema, e `response.parsed` entrega o objeto pronto.
- **No Ollama**, o esquema vai no campo `format` como JSON Schema (`Triage.model_json_schema()`). A resposta passa por `Triage.model_validate_json`, que dá erro se o modelo inventar uma categoria.

Por que isso importa: sem esquema, o modelo pode responder "Categoria: Atraso na entrega" em vez de `atraso`, e o código quebra. Com esquema, a saída é sempre um dos valores esperados.

## 3. O prompt

O prompt (`PROMPT` em `core.py`) define:
- cada categoria, com o que entra nela;
- a regra de desempate: reembolso só quando o estorno é o assunto principal;
- o formato do número do pedido: só dígitos, sem `#`;
- regras objetivas de urgência (atraso acima de 1 hora, risco à saúde, cobrança duplicada, ameaça de Procon).

Regras objetivas deixam a urgência medível. "Cliente irritado" seria subjetivo demais para comparar com um rótulo. A temperatura é 0, para a mesma mensagem dar a mesma resposta.

## 4. Métricas

- **Acerto (accuracy)**: fração de mensagens com a categoria certa. Vale também para urgência e número do pedido.
- **Precisão** de uma categoria: das vezes que o modelo disse "reembolso", quantas eram reembolso. Baixa precisão significa alarme falso.
- **Revocação (recall)**: das mensagens que eram reembolso, quantas o modelo achou. Baixa revocação significa caso perdido.
- **F1**: média harmônica das duas. Só é alta quando as duas são.
- **Confusões mais comuns**: pares (esperado → previsto) que mais se repetem. Mostram onde as definições das categorias se sobrepõem, por exemplo item faltando e pedido errado.

Tudo é calculado com a biblioteca padrão, sem scikit-learn: são poucas contas e fica fácil de explicar.

Uma chamada que falha (rede, cota, JSON inválido) vira "falhou" e conta como erro, sem derrubar a avaliação inteira.

## 5. Decisões de projeto

- **Três classificadores com a mesma assinatura.** O avaliador recebe uma função e não sabe qual modelo está por trás. Trocar Gemini por Ollama ou por outro modelo é mudar um parâmetro.
- **Linha de base sem IA.** Responde "a IA vale o custo?". Se as regras acertassem quase tanto quanto o LLM, não valeria. Ela também permite rodar testes e CI sem internet.
- **Testes nunca chamam LLM.** Chamadas reais são lentas, gastam cota e variam. Os testes usam as regras e um Ollama falso: `monkeypatch` troca o `urlopen` e confere o JSON enviado.
- **Pausa e nova tentativa no Gemini grátis.** O plano grátis limita chamadas por minuto. O avaliador espera 4 s entre mensagens e, se receber erro 429, espera e tenta de novo.
- **Lotes no plano grátis.** O limite é de chamadas por dia, não de mensagens. Com `--lote 10`, cada chamada leva 10 mensagens numeradas, e o esquema de saída (`Batch`) pede um item por número. Se o modelo pular um número, aquela mensagem conta como falha.
- **Resultado que varia.** Duas rodadas idênticas deram 97% e 100% na categoria. Temperatura 0 reduz a variação, mas não zera. Por isso o README mostra a faixa.
- **Chave fora do código.** A chave fica no `.env`, que está no `.gitignore`, e é carregada com `uv run --env-file .env`.
- **Dados inventados.** Nenhuma mensagem é de cliente real.

## 6. Limites honestos

- **100 mensagens é pouco.** Um erro a mais ou a menos muda o acerto em 1 ponto. Serve para comparar modelos e prompts, não para garantir qualidade em produção.
- **Mesmo autor nas mensagens e nas regras.** A linha de base é otimista porque as regras foram escritas por quem conhecia as mensagens.
- **Mensagem com dois problemas.** "Veio errado e quero meu dinheiro de volta" tem dois assuntos. O projeto escolhe um principal; um sistema real poderia devolver uma lista de categorias.

## 7. Perguntas prováveis

**Como você melhoraria o acerto?**
1. Ler a tabela de confusões.
2. Ajustar a definição das categorias que se sobrepõem.
3. Pôr 2 ou 3 exemplos no prompt (few-shot).
4. Medir de novo.

Tudo isso numa parte das mensagens; outra parte fica guardada só para a medida final, para não "decorar" o teste.

**Como colocaria isso em produção?**
- Uma API recebendo as mensagens.
- Fila para não estourar a cota do modelo.
- Log de cada classificação.
- Amostra revisada por pessoas toda semana, para virar novos rótulos e reavaliar o modelo.

**E se o modelo errar uma urgência alta?**
O custo do erro não é simétrico: perder uma urgência alta é pior que um alarme falso. Dá para olhar a revocação de "alta" separada e ajustar o prompt para priorizá-la.

**Qual foi o papel da IA no projeto?**
Eu defini o problema: um classificador de atendimento de delivery que pudesse ser medido. O Claude Code escreveu o código, os testes, as mensagens e os rótulos, seguindo as regras do prompt.
