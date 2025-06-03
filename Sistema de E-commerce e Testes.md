# Lista de Tarefas - Sistema de E-commerce e Testes

## Implementação das Classes (Clean Code & SOLID)

- [X] Implementar a classe `Produto` (id, nome, descrição, preço, estoque, categoria, verificar_disponibilidade, atualizar_estoque, obter_informacoes)
- [X] Implementar a classe `Carrinho` (lista de produtos/quantidades, adicionar, remover, atualizar, calcular_total, aplicar_descontos, limpar)
- [X] Implementar a classe `SistemaPagamento` (processar transações, suportar cartão de crédito à vista/parcelado e PIX, autorizar, verificar fraude, processar reembolso, gerar comprovante)
- [X] Implementar a classe `Pedido` (id, cliente, itens, entrega, pagamento, status, datas, atualizar_status, calcular_frete, gerar_nota_fiscal)
- [X] Implementar a classe `SistemaEcommerce` (integrar classes, gerenciar fluxo de compra, busca, recomendações gestão de usuários, relatórios)

## Implementação dos Testes

- [X] **Questão 1 (Pytest):** Testes para `Produto` (criação, disponibilidade, redução de estoque).
- [X] **Questão 2 (unittest):** Testes para `Carrinho` (adição, remoção, cálculo total, adição sem estoque).
- [X] **Questão 3 (Testify):** Testes para `SistemaPagamento` (cálculo cartão à vista, cartão parcelado, PIX com desconto, valor parcelas).
- [X] **Questão 4 (Pytest):** Testes de integração `Carrinho` e `Produto` (atualização total, bloqueio sem estoque, remoção parcial).
- [X] **Questão 5 (unittest):** Testes para `Pedido` (transição de status, processamento de pagamentos, restrições de transição).
- [X] **Questão 6 (Testify):** Testes para `SistemaEcommerce` (adição/recuperação produtos, criação pedidos, processamento pagamentos, cancelamento/reabastecimento).
- [X] **Questão 7 (Pytest + Mock):** Testes de falha em `SistemaPagamento` (falha autorização cartão, timeout gateway, manutenção estado pedido).
- [X] **Questão 8 (unittest + Fixtures):** Testes de integração do fluxo completo (PIX, cartão à vista, cartão parcelado).
- [X] **Questão 9 (Testify + Parametrização):** Testes de configuração (taxas juros, descontos PIX, nº parcelas).
- [X] **Questão 10 (Pytest, unittest, Testify):** Testes de performance (adição múltipla carrinho, processamento pagamento, volume pedidos).
