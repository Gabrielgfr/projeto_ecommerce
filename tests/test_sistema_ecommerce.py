import unittest
from decimal import Decimal

# Ajusta o path para encontrar o módulo ecommerce
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), ".")))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from ecommerce.produto import Produto
from ecommerce.carrinho import Carrinho
from ecommerce.sistema_pagamento import SistemaPagamento
from ecommerce.pedido import Pedido, StatusPedido
from ecommerce.sistema_ecommerce import SistemaEcommerce

class SistemaEcommerceTest(unittest.TestCase):
    """Testa a classe principal SistemaEcommerce."""

    def setUp(self):
        """Inicializa o sistema e adiciona produtos."""
        self.sistema = SistemaEcommerce()
        self.produto1 = Produto(601, "Produto Sistema A", "Desc SA", 20.0, 10, "Sys")
        self.produto2 = Produto(602, "Produto Sistema B", "Desc SB", 5.5, 5, "Sys")
        self.produto_sem_estoque = Produto(603, "Produto Sistema C", "Desc SC", 10.0, 0, "Sys")

        self.sistema.adicionar_produto(self.produto1)
        self.sistema.adicionar_produto(self.produto2)
        self.sistema.adicionar_produto(self.produto_sem_estoque)

        self.id_cliente = "cliente_sys_test"
        self.endereco = {"rua": "Rua Sistema", "cep": "66666-000"}

    def test_adicao_e_recuperacao_produtos(self):
        """Verifica se produtos são adicionados e recuperados corretamente.

        Questão 6: Adição e recuperação de produtos
        """
        p1 = self.sistema.buscar_produto_por_id(601)
        p2 = self.sistema.buscar_produto_por_id(602)
        p3 = self.sistema.buscar_produto_por_id(603)

        self.assertIsNotNone(p1)
        self.assertEqual(p1.nome, "Produto Sistema A")
        self.assertIsNotNone(p2)
        self.assertEqual(p2.nome, "Produto Sistema B")
        self.assertIsNotNone(p3)
        self.assertEqual(p3.nome, "Produto Sistema C")

        self.assertIsNone(self.sistema.buscar_produto_por_id(999))

        lista = self.sistema.listar_produtos()
        self.assertEqual(len(lista), 3)
        self.assertIn(self.produto1, lista)
        self.assertIn(self.produto2, lista)
        self.assertIn(self.produto_sem_estoque, lista)

        busca1 = self.sistema.buscar_produtos_por_nome("Sistema A")
        self.assertEqual(len(busca1), 1)
        self.assertEqual(busca1[0], self.produto1)

        busca2 = self.sistema.buscar_produtos_por_nome("Sistema")
        self.assertEqual(len(busca2), 3)

    def test_criacao_pedido_sucesso(self):
        """Verifica a criação bem-sucedida de um pedido.

        Questão 6: Criação de pedidos
        """
        carrinho = Carrinho()
        carrinho.adicionar_item(self.produto1, 2)
        carrinho.adicionar_item(self.produto2, 1)

        estoque_p1 = self.produto1.quantidade_estoque
        estoque_p2 = self.produto2.quantidade_estoque

        pedido = self.sistema.criar_pedido(self.id_cliente, carrinho, self.endereco, "PIX")

        self.assertIsNotNone(pedido)
        self.assertIsInstance(pedido, Pedido)
        self.assertEqual(pedido.status, StatusPedido.PENDENTE)
        self.assertEqual(pedido.id_cliente, self.id_cliente)
        self.assertEqual(len(pedido.itens), 2)

        pedido_buscado = self.sistema.buscar_pedido_por_id(pedido.id_pedido)
        self.assertEqual(pedido, pedido_buscado)

        self.assertEqual(self.produto1.quantidade_estoque, estoque_p1 - 2)
        self.assertEqual(self.produto2.quantidade_estoque, estoque_p2 - 1)
        self.assertEqual(len(carrinho), 0)

    def test_criacao_pedido_falha_estoque_insuficiente(self):
        """Verifica se a criação do pedido falha se um item não tiver estoque.

        Questão 6: Criação de pedidos (falha por estoque)
        """
        carrinho = Carrinho()
        carrinho.adicionar_item(self.produto1, 1)

        with self.assertRaises(ValueError):
            carrinho.adicionar_item(self.produto_sem_estoque, 1)

        carrinho_valido = Carrinho()
        carrinho_valido.adicionar_item(self.produto2, 3)

        estoque_original = self.produto2.quantidade_estoque
        self.produto2.quantidade_estoque = 1

        pedido = self.sistema.criar_pedido(self.id_cliente, carrinho_valido, self.endereco, "PIX")
        self.assertIsNone(pedido)
        self.assertEqual(self.produto2.quantidade_estoque, 1)
        self.produto2.quantidade_estoque = estoque_original

    def test_processamento_pagamento(self):
        """Verifica a integração do processamento de pagamento.

        Questão 6: Processamento de pagamentos
        """
        carrinho = Carrinho()
        carrinho.adicionar_item(self.produto1, 1)
        pedido = self.sistema.criar_pedido(self.id_cliente, carrinho, self.endereco, "Cartão de Crédito")

        self.assertIsNotNone(pedido)
        self.assertEqual(pedido.status, StatusPedido.PENDENTE)

        dados_pagamento = {"num_parcelas": 1, "dados_cartao": {}}
        self.sistema.processar_pagamento_pedido(pedido.id_pedido, dados_pagamento)

        pedido_atualizado = self.sistema.buscar_pedido_por_id(pedido.id_pedido)
        self.assertIsNotNone(pedido_atualizado)
        self.assertIn(pedido_atualizado.status, [StatusPedido.PAGO, StatusPedido.FALHA_PAGAMENTO])

    def test_cancelamento_pedido_pendente_reabastece_estoque(self):
        """Verifica o cancelamento de um pedido pendente e o reabastecimento.

        Questão 6: Cancelamento de pedidos e reabastecimento do estoque
        """
        carrinho = Carrinho()
        carrinho.adicionar_item(self.produto1, 3)
        carrinho.adicionar_item(self.produto2, 2)

        estoque_p1 = self.produto1.quantidade_estoque
        estoque_p2 = self.produto2.quantidade_estoque

        pedido = self.sistema.criar_pedido(self.id_cliente, carrinho, self.endereco, "Boleto")
        self.assertIsNotNone(pedido)

        self.assertEqual(self.produto1.quantidade_estoque, estoque_p1 - 3)
        self.assertEqual(self.produto2.quantidade_estoque, estoque_p2 - 2)

        self.sistema.cancelar_pedido(pedido.id_pedido)

        self.assertEqual(self.produto1.quantidade_estoque, estoque_p1)
        self.assertEqual(self.produto2.quantidade_estoque, estoque_p2)
        self.assertEqual(pedido.status, StatusPedido.CANCELADO)

if __name__ == '__main__':
    unittest.main()
