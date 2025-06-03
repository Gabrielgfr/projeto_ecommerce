import unittest
from unittest.mock import MagicMock, patch # Para simular dependências como Carrinho
from decimal import Decimal
from datetime import datetime

# Ajusta o path para encontrar o módulo ecommerce
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), ".")))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from ecommerce.produto import Produto
from ecommerce.carrinho import Carrinho
from ecommerce.pedido import Pedido, StatusPedido

class TestPedido(unittest.TestCase):
    """Classe de teste para a classe Pedido usando unittest."""

    def setUp(self):
        """Configura o ambiente para cada teste.

        Cria um mock de Carrinho com itens e outros dados necessários.
        """
        # Mock Produto (não precisamos da lógica interna do produto aqui)
        self.produto1 = MagicMock(spec=Produto)
        self.produto1.id_produto = 301
        self.produto1.nome = "Produto Mock A"
        self.produto1.preco = Decimal("100.00")

        self.produto2 = MagicMock(spec=Produto)
        self.produto2.id_produto = 302
        self.produto2.nome = "Produto Mock B"
        self.produto2.preco = Decimal("50.50")

        # Mock Carrinho
        self.mock_carrinho = MagicMock(spec=Carrinho)
        # Simula o retorno de obter_itens() e calcular_total()
        self.mock_carrinho.obter_itens.return_value = {self.produto1: 1, self.produto2: 2}
        # Total = 1 * 100.00 + 2 * 50.50 = 100.00 + 101.00 = 201.00
        self.mock_carrinho.calcular_total.return_value = Decimal("201.00")

        # Dados comuns para criar um pedido
        self.id_cliente = "cliente_teste_pedido"
        self.endereco = {"rua": "Rua Teste Pedido", "cep": "11111-000"}
        self.metodo_pagamento_cc = "Cartão de Crédito"
        self.metodo_pagamento_pix = "PIX"

        # Cria uma instância de Pedido para testes de transição
        # Usamos patch para simular o cálculo de frete e evitar dependência externa
        with patch("ecommerce.pedido.Pedido.calcular_frete", return_value=Decimal("15.00")):
            self.pedido = Pedido(self.id_cliente, self.mock_carrinho, self.endereco, self.metodo_pagamento_cc)

        # Valor total esperado inicial = 201.00 (itens) + 15.00 (frete) = 216.00
        self.valor_total_inicial_esperado = Decimal("216.00")

    def test_criacao_pedido(self):
        """Verifica se o pedido é criado com o status e valores iniciais corretos."""
        self.assertEqual(self.pedido.id_cliente, self.id_cliente)
        self.assertEqual(self.pedido.status, StatusPedido.PENDENTE)
        self.assertEqual(len(self.pedido.itens), 2)
        self.assertIn(self.produto1, self.pedido.itens)
        self.assertEqual(self.pedido.itens[self.produto1], 1)
        self.assertIn(self.produto2, self.pedido.itens)
        self.assertEqual(self.pedido.itens[self.produto2], 2)
        self.assertEqual(self.pedido.metodo_pagamento, self.metodo_pagamento_cc)
        self.assertAlmostEqual(self.pedido.valor_total, self.valor_total_inicial_esperado)
        self.assertAlmostEqual(self.pedido.valor_frete, Decimal("15.00"))
        self.assertIsInstance(self.pedido.data_criacao, datetime)
        self.assertIsNone(self.pedido.data_pagamento)
        self.assertIsNone(self.pedido.data_envio)
        self.assertIsNone(self.pedido.data_entrega)
        self.assertIsNone(self.pedido.id_transacao_pagamento)

    def test_transicao_status_valida_fluxo_sucesso(self):
        """Verifica as transições de status válidas no fluxo de sucesso.

        Questão 5: A transição correta entre os diferentes estados do pedido
        """
        # PENDENTE -> PROCESSANDO_PAGAMENTO
        self.assertTrue(self.pedido.atualizar_status(StatusPedido.PROCESSANDO_PAGAMENTO))
        self.assertEqual(self.pedido.status, StatusPedido.PROCESSANDO_PAGAMENTO)

        # PROCESSANDO_PAGAMENTO -> PAGO (Simulado via registrar_pagamento)
        # Precisamos chamar registrar_pagamento para ir para PAGO
        self.pedido.registrar_pagamento(sucesso=True, id_transacao="trans_123", valor_pago=self.valor_total_inicial_esperado)
        self.assertEqual(self.pedido.status, StatusPedido.PAGO)
        self.assertIsNotNone(self.pedido.data_pagamento)
        self.assertEqual(self.pedido.id_transacao_pagamento, "trans_123")

        # PAGO -> EM_SEPARACAO
        self.assertTrue(self.pedido.atualizar_status(StatusPedido.EM_SEPARACAO))
        self.assertEqual(self.pedido.status, StatusPedido.EM_SEPARACAO)

        # EM_SEPARACAO -> ENVIADO
        self.assertTrue(self.pedido.atualizar_status(StatusPedido.ENVIADO))
        self.assertEqual(self.pedido.status, StatusPedido.ENVIADO)
        self.assertIsNotNone(self.pedido.data_envio)

        # ENVIADO -> ENTREGUE
        self.assertTrue(self.pedido.atualizar_status(StatusPedido.ENTREGUE))
        self.assertEqual(self.pedido.status, StatusPedido.ENTREGUE)
        self.assertIsNotNone(self.pedido.data_entrega)

    def test_transicao_status_valida_fluxo_falha_pagamento(self):
        """Verifica as transições de status válidas no fluxo de falha de pagamento.

        Questão 5: A transição correta entre os diferentes estados do pedido
        """
        # PENDENTE -> PROCESSANDO_PAGAMENTO
        self.assertTrue(self.pedido.atualizar_status(StatusPedido.PROCESSANDO_PAGAMENTO))
        self.assertEqual(self.pedido.status, StatusPedido.PROCESSANDO_PAGAMENTO)

        # PROCESSANDO_PAGAMENTO -> FALHA_PAGAMENTO (Simulado via registrar_pagamento)
        self.pedido.registrar_pagamento(sucesso=False, id_transacao="trans_fail", valor_pago=Decimal("0.0"))
        self.assertEqual(self.pedido.status, StatusPedido.FALHA_PAGAMENTO)
        self.assertIsNone(self.pedido.data_pagamento)
        self.assertIsNone(self.pedido.id_transacao_pagamento) # Não deve registrar ID em falha

        # FALHA_PAGAMENTO -> PROCESSANDO_PAGAMENTO (Retentativa)
        self.assertTrue(self.pedido.atualizar_status(StatusPedido.PROCESSANDO_PAGAMENTO))
        self.assertEqual(self.pedido.status, StatusPedido.PROCESSANDO_PAGAMENTO)

        # PROCESSANDO_PAGAMENTO -> PAGO (Agora com sucesso)
        self.pedido.registrar_pagamento(sucesso=True, id_transacao="trans_ok_retry", valor_pago=self.valor_total_inicial_esperado)
        self.assertEqual(self.pedido.status, StatusPedido.PAGO)

    def test_transicao_status_valida_fluxo_cancelamento(self):
        """Verifica as transições de status válidas envolvendo cancelamento.

        Questão 5: A transição correta entre os diferentes estados do pedido
        """
        # PENDENTE -> CANCELADO
        pedido_pendente = Pedido(self.id_cliente, self.mock_carrinho, self.endereco, self.metodo_pagamento_pix)
        self.assertTrue(pedido_pendente.atualizar_status(StatusPedido.CANCELADO))
        self.assertEqual(pedido_pendente.status, StatusPedido.CANCELADO)

        # PROCESSANDO_PAGAMENTO -> CANCELADO
        pedido_processando = Pedido(self.id_cliente, self.mock_carrinho, self.endereco, self.metodo_pagamento_pix)
        pedido_processando.atualizar_status(StatusPedido.PROCESSANDO_PAGAMENTO)
        self.assertTrue(pedido_processando.atualizar_status(StatusPedido.CANCELADO))
        self.assertEqual(pedido_processando.status, StatusPedido.CANCELADO)

        # PAGO -> CANCELADO (Pode exigir reembolso, mas a transição é permitida)
        pedido_pago = Pedido(self.id_cliente, self.mock_carrinho, self.endereco, self.metodo_pagamento_pix)
        pedido_pago.atualizar_status(StatusPedido.PROCESSANDO_PAGAMENTO)
        pedido_pago.registrar_pagamento(True, "trans_cancel", Decimal("216.00"))
        self.assertTrue(pedido_pago.atualizar_status(StatusPedido.CANCELADO))
        self.assertEqual(pedido_pago.status, StatusPedido.CANCELADO)

    def test_transicao_status_invalida(self):
        """Verifica se transições de status inválidas são bloqueadas.

        Questão 5: As restrições de transição de estado (ex: não pode ir de pendente para entregue)
        """
        # PENDENTE -> ENTREGUE (Inválido)
        self.assertFalse(self.pedido.atualizar_status(StatusPedido.ENTREGUE))
        self.assertEqual(self.pedido.status, StatusPedido.PENDENTE) # Status não deve mudar

        # PENDENTE -> ENVIADO (Inválido)
        self.assertFalse(self.pedido.atualizar_status(StatusPedido.ENVIADO))
        self.assertEqual(self.pedido.status, StatusPedido.PENDENTE)

        # PAGO -> PENDENTE (Inválido)
        self.pedido.atualizar_status(StatusPedido.PROCESSANDO_PAGAMENTO)
        self.pedido.registrar_pagamento(True, "t1", Decimal("216.00")) # Vai para PAGO
        self.assertFalse(self.pedido.atualizar_status(StatusPedido.PENDENTE))
        self.assertEqual(self.pedido.status, StatusPedido.PAGO)

        # ENTREGUE -> PAGO (Inválido)
        self.pedido.atualizar_status(StatusPedido.EM_SEPARACAO)
        self.pedido.atualizar_status(StatusPedido.ENVIADO)
        self.pedido.atualizar_status(StatusPedido.ENTREGUE)
        self.assertFalse(self.pedido.atualizar_status(StatusPedido.PAGO))
        self.assertEqual(self.pedido.status, StatusPedido.ENTREGUE)

        # CANCELADO -> PAGO (Inválido)
        pedido_cancelado = Pedido(self.id_cliente, self.mock_carrinho, self.endereco, self.metodo_pagamento_pix)
        pedido_cancelado.atualizar_status(StatusPedido.CANCELADO)
        self.assertFalse(pedido_cancelado.atualizar_status(StatusPedido.PAGO))
        self.assertEqual(pedido_cancelado.status, StatusPedido.CANCELADO)

    def test_processamento_pagamento_sucesso_cc(self):
        """Verifica o registro de pagamento bem-sucedido com Cartão de Crédito.

        Questão 5: O processamento de pagamento com diferentes métodos
        """
        valor_pago_cc = Decimal("220.00") # Simula valor com juros
        num_parcelas = 3
        valor_parcela = Decimal("73.34")
        id_transacao = "cc_trans_success"

        self.pedido.atualizar_status(StatusPedido.PROCESSANDO_PAGAMENTO)
        self.pedido.registrar_pagamento(True, id_transacao, valor_pago_cc, num_parcelas, valor_parcela)

        self.assertEqual(self.pedido.status, StatusPedido.PAGO)
        self.assertEqual(self.pedido.id_transacao_pagamento, id_transacao)
        self.assertAlmostEqual(self.pedido.valor_total, valor_pago_cc) # Valor total atualizado
        self.assertEqual(self.pedido.num_parcelas, num_parcelas)
        self.assertAlmostEqual(self.pedido.valor_parcela, valor_parcela)
        self.assertIsNotNone(self.pedido.data_pagamento)

    def test_processamento_pagamento_sucesso_pix(self):
        """Verifica o registro de pagamento bem-sucedido com PIX.

        Questão 5: O processamento de pagamento com diferentes métodos
        """
        # Cria um pedido específico para PIX
        with patch("ecommerce.pedido.Pedido.calcular_frete", return_value=Decimal("10.00")):
            pedido_pix = Pedido(self.id_cliente, self.mock_carrinho, self.endereco, self.metodo_pagamento_pix)
        # Total inicial PIX = 201.00 + 10.00 = 211.00

        valor_pago_pix = Decimal("199.95") # Simula valor com desconto PIX
        id_transacao = "pix_trans_success"

        pedido_pix.atualizar_status(StatusPedido.PROCESSANDO_PAGAMENTO)
        pedido_pix.registrar_pagamento(True, id_transacao, valor_pago_pix)

        self.assertEqual(pedido_pix.status, StatusPedido.PAGO)
        self.assertEqual(pedido_pix.id_transacao_pagamento, id_transacao)
        self.assertAlmostEqual(pedido_pix.valor_total, valor_pago_pix) # Valor total atualizado
        self.assertIsNone(pedido_pix.num_parcelas)
        self.assertIsNone(pedido_pix.valor_parcela)
        self.assertIsNotNone(pedido_pix.data_pagamento)

    def test_processamento_pagamento_falha(self):
        """Verifica o registro de pagamento com falha.

        Questão 5: O processamento de pagamento com diferentes métodos
        """
        id_transacao_falha = "trans_failed_123" # ID pode ou não ser gerado na falha

        self.pedido.atualizar_status(StatusPedido.PROCESSANDO_PAGAMENTO)
        self.pedido.registrar_pagamento(False, id_transacao_falha, Decimal("0.0"))

        self.assertEqual(self.pedido.status, StatusPedido.FALHA_PAGAMENTO)
        self.assertIsNone(self.pedido.id_transacao_pagamento) # Não deve armazenar ID da falha
        self.assertAlmostEqual(self.pedido.valor_total, self.valor_total_inicial_esperado) # Valor total não deve mudar
        self.assertIsNone(self.pedido.num_parcelas)
        self.assertIsNone(self.pedido.valor_parcela)
        self.assertIsNone(self.pedido.data_pagamento)

    def test_gerar_nota_fiscal_status_invalido(self):
        """Verifica se gerar nota fiscal falha em status inválidos.
        """
        # Status PENDENTE
        with self.assertRaisesRegex(ValueError, "Não é possível gerar nota fiscal.*PENDENTE"):
            self.pedido.gerar_nota_fiscal()

        # Status CANCELADO
        self.pedido.atualizar_status(StatusPedido.CANCELADO)
        with self.assertRaisesRegex(ValueError, "Não é possível gerar nota fiscal.*CANCELADO"):
            self.pedido.gerar_nota_fiscal()

    def test_gerar_nota_fiscal_status_valido(self):
        """Verifica se a nota fiscal pode ser gerada em status válidos (ex: PAGO).
        """
        self.pedido.atualizar_status(StatusPedido.PROCESSANDO_PAGAMENTO)
        self.pedido.registrar_pagamento(True, "nf_test", Decimal("216.00"))
        self.assertEqual(self.pedido.status, StatusPedido.PAGO)

        try:
            nota = self.pedido.gerar_nota_fiscal()
            self.assertIsInstance(nota, str)
            self.assertIn("--- Nota Fiscal ---", nota)
            self.assertIn(f"Pedido ID: {self.pedido.id_pedido}", nota)
            self.assertIn(f"Cliente ID: {self.id_cliente}", nota)
            self.assertIn("Produto Mock A (1x R$ 100.00) = R$ 100.00", nota)
            self.assertIn("Produto Mock B (2x R$ 50.50) = R$ 101.00", nota)
            self.assertIn("Subtotal Itens: R$ 201.00", nota)
            self.assertIn("Frete: R$ 15.00", nota)
            self.assertIn("Valor Total Pago: R$ 216.00", nota)
            self.assertIn(f"Método Pagamento: {self.metodo_pagamento_cc}", nota)
            self.assertIn("ID Transação: nf_test", nota)
        except ValueError:
            self.fail("gerar_nota_fiscal() levantou ValueError inesperadamente em status PAGO")

# Permite executar os testes diretamente pelo script
if __name__ == '__main__':
    unittest.main()

