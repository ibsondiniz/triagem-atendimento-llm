# Avaliação: gemini (gemini-3.5-flash-lite), lotes de 10 mensagens

100 mensagens rotuladas, 51 s, 0 chamada(s) com falha.

| Medida | Acerto |
|---|---|
| Categoria | 100% |
| Urgência | 84% |
| Número do pedido | 100% |

## Por categoria

| Categoria | Mensagens | Precisão | Revocação | F1 |
|---|---|---|---|---|
| atraso | 15 | 100% | 100% | 1.00 |
| pedido_errado | 12 | 100% | 100% | 1.00 |
| item_faltando | 11 | 100% | 100% | 1.00 |
| qualidade | 12 | 100% | 100% | 1.00 |
| reembolso | 10 | 100% | 100% | 1.00 |
| cancelamento | 10 | 100% | 100% | 1.00 |
| pagamento | 12 | 100% | 100% | 1.00 |
| elogio | 10 | 100% | 100% | 1.00 |
| outro | 8 | 100% | 100% | 1.00 |

## Confusões mais comuns

| Esperado | Previsto | Vezes |
|---|---|---|

## Erros de categoria

| # | Mensagem | Esperado | Previsto |
|---|---|---|---|

## Erros de urgência

| # | Mensagem | Esperado | Previsto |
|---|---|---|---|
| 5 | Pedido #702144 não chegou ainda. O status ficou parado em 'saiu para entrega'. | media | alta |
| 6 | Oi, só queria saber se o pedido 390218 vai demorar muito, pedi há 35 min | media | baixa |
| 26 | Meu pedido 774102 chegou mas é de outro restaurante, não reconheço nada | media | alta |
| 27 | pedi o prato vegano e veio com bacon. não como carne. | media | alta |
| 39 | A comida chegou fria e a embalagem toda aberta. Pedido #392018 | media | alta |
| 40 | Encontrei um cabelo no meu prato. Nojento. | media | alta |
| 43 | O lacre da sacola estava rompido, não tenho coragem de comer | media | alta |
| 50 | O bolo veio com mofo. Pedido #118204. Felizmente vi antes de comer. | media | alta |
| 60 | reembolso negado?? o pedido nem chegou! 811462 | media | alta |
| 63 | Cancela por favor, já se passou muito tempo e eu vou sair | media | alta |
| 66 | Quero cancelar minha assinatura do clube de vantagens | media | baixa |
| 69 | Preciso cancelar urgente, o pedido é pra festa que foi adiada. #560219 | media | alta |
| 70 | cancelem o pedido 431088 imediatamente, o endereço é de uma casa que vendi | media | alta |
| 74 | Paguei no pix e o pedido continua como aguardando pagamento | media | alta |
| 81 | Paguei R$ 89,90 mas o restaurante diz que ficou faltando pagar R$ 10 | media | alta |
| 99 | Minha conta foi bloqueada sem motivo | media | alta |
