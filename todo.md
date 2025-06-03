# Lista de Tarefas - Sistema de E-commerce e Testes

## Implementação das Classes (Clean Code & SOLID)

- [X] Implementar a classe `Produto` (id, nome, descrição, preço, estoque, categoria, verificar_disponibilidade, atualizar_estoque, obter_informacoes)
- [X] Implementar a classe `Carrinho` (lista de produtos/quantidades, adicionar, remover, atualizar, calcular_total, aplicar_descontos, limpar)
- [X] Implementar a classe `SistemaPagamento` (processar transações, suportar cartão de crédito à vista/parcelado e PIX, autorizar, verificar fraude, processar reembolso, gerar comprovante)
- [X] Implementar a classe `Pedido` (id, cliente, itens, entrega, pagamento, status, datas, atualizar_status, calcular_frete, gerar_nota_fiscal)
- [X] Implementar a classe `SistemaEcommerce` (integrar classes, gerenciar fluxo de compra, busca, recomendações, gestão de usuários, relatórios)

## Implementação dos Testes

- [ ] **Questão 1 (Pytest):** Testes para `Produto` (criação, disponibilidade, redução de estoque).
- [ ] **Questão 2 (unittest):** Testes para `Carrinho` (adição, remoção, cálculo total, adição sem estoque).
- [ ] **Questão 3 (Testify):** Testes para `SistemaPagamento` (cálculo cartão à vista, cartão parcelado, PIX com desconto, valor parcelas).
- [ ] **Questão 4 (Pytest):** Testes de integração `Carrinho` e `Produto` (atualização total, bloqueio sem estoque, remoção parcial).
- [ ] **Questão 5 (unittest):** Testes para `Pedido` (transição de status, processamento de pagamentos, restrições de transição).
- [ ] **Questão 6 (Testify):** Testes para `SistemaEcommerce` (adição/recuperação produtos, criação pedidos, processamento pagamentos, cancelamento/reabastecimento).
- [ ] **Questão 7 (Pytest + Mock):** Testes de falha em `SistemaPagamento` (falha autorização cartão, timeout gateway, manutenção estado pedido).
- [ ] **Questão 8 (unittest + Fixtures):** Testes de integração do fluxo completo (PIX, cartão à vista, cartão parcelado).
- [ ] **Questão 9 (Testify + Parametrização):** Testes de configuração (taxas juros, descontos PIX, nº parcelas).
- [ ] **Questão 10 (Pytest, unittest, Testify):** Testes de performance (adição múltipla carrinho, processamento pagamento, volume pedidos).

## Como executar o projeto: 
   1. Navegue até a pasta do projeto: cd projeto_ecommerce
   2. Crie um Ambiente virtual: python -m venv venv
   3. Ative o ambiente virtual: venv\Scripts\activate
   4. Instale as dependências: pip install -r requirements.txt
   5. Execute automaticamente todos os testes nas pastas tests: pytest
   6. Execute o exemplo principal que simula a criação de produtos, carrinhos e pedidos:python -m ecommerce.sistema_ecommerce


