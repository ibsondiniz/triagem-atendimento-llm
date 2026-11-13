# Avaliação: regras (palavras-chave)

100 mensagens rotuladas, 0 s, 0 chamada(s) com falha.

| Medida | Acerto |
|---|---|
| Categoria | 87% |
| Urgência | 84% |
| Número do pedido | 100% |

## Por categoria

| Categoria | Mensagens | Precisão | Revocação | F1 |
|---|---|---|---|---|
| atraso | 15 | 100% | 80% | 0.89 |
| pedido_errado | 12 | 100% | 58% | 0.74 |
| item_faltando | 11 | 100% | 64% | 0.78 |
| qualidade | 12 | 100% | 100% | 1.00 |
| reembolso | 10 | 100% | 100% | 1.00 |
| cancelamento | 10 | 100% | 100% | 1.00 |
| pagamento | 12 | 73% | 92% | 0.81 |
| elogio | 10 | 100% | 100% | 1.00 |
| outro | 8 | 47% | 100% | 0.64 |

## Confusões mais comuns

| Esperado | Previsto | Vezes |
|---|---|---|
| pedido_errado | outro | 4 |
| atraso | outro | 3 |
| item_faltando | pagamento | 3 |
| pedido_errado | pagamento | 1 |
| item_faltando | outro | 1 |
| pagamento | outro | 1 |

## Erros de categoria

| # | Mensagem | Esperado | Previsto |
|---|---|---|---|
| 4 | Já faz 1h40 que pedi e nada da comida. Meu filho tá com fome, isso é um absurdo!! | atraso | outro |
| 13 | o restaurante ainda nem aceitou meu pedido e já se passaram 40 minutos | atraso | outro |
| 14 | Entregador parece perdido, está rodando o bairro há meia hora. Pedido 109877 | atraso | outro |
| 16 | Pedi pizza de calabresa e veio de frango. Pedido #440192 | pedido_errado | outro |
| 19 | Pedido 667301: pedi coca zero e mandaram coca normal. Sou diabético. | pedido_errado | outro |
| 20 | O açaí veio de 300ml e eu paguei pelo de 500ml | pedido_errado | pagamento |
| 23 | pedi sem glúten e veio pão comum, minha filha é celíaca e quase comeu | pedido_errado | outro |
| 27 | pedi o prato vegano e veio com bacon. não como carne. | pedido_errado | outro |
| 29 | Veio só 1 dos 2 hambúrgueres que paguei | item_faltando | pagamento |
| 33 | Pedido 845670 veio sem o molho que paguei à parte | item_faltando | pagamento |
| 36 | faltou um item inteiro do pedido 128834, o yakisoba. paguei 45 reais por ele | item_faltando | pagamento |
| 38 | A caixa veio com 10 nuggets e o anúncio fala em 20 | item_faltando | outro |
| 80 | Por que o valor do pedido mudou depois que finalizei? | pagamento | outro |

## Erros de urgência

| # | Mensagem | Esperado | Previsto |
|---|---|---|---|
| 1 | Meu pedido #483920 era pra chegar às 19h e já são 20h30. Cadê? | alta | media |
| 8 | Previsão era 12h15, agora é 13h40 e o app só aumenta o tempo | alta | media |
| 13 | o restaurante ainda nem aceitou meu pedido e já se passaram 40 minutos | media | baixa |
| 14 | Entregador parece perdido, está rodando o bairro há meia hora. Pedido 109877 | media | baixa |
| 16 | Pedi pizza de calabresa e veio de frango. Pedido #440192 | media | baixa |
| 26 | Meu pedido 774102 chegou mas é de outro restaurante, não reconheço nada | media | alta |
| 27 | pedi o prato vegano e veio com bacon. não como carne. | media | baixa |
| 38 | A caixa veio com 10 nuggets e o anúncio fala em 20 | media | baixa |
| 53 | Quanto tempo leva pro reembolso aparecer na fatura? | baixa | media |
| 56 | Posso receber o reembolso em crédito no app em vez de no cartão? | baixa | media |
| 57 | o estorno do pedido 640078 apareceu como pendente, é normal? | baixa | media |
| 62 | Como cancelo? Pedi duas vezes sem querer | media | alta |
| 72 | Meu cartão foi recusado mas o valor aparece na fatura | alta | media |
| 80 | Por que o valor do pedido mudou depois que finalizei? | media | baixa |
| 97 | Esqueci minha senha e o e-mail de recuperação não chega | media | baixa |
| 99 | Minha conta foi bloqueada sem motivo | media | baixa |
