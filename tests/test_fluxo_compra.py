import unittest
from unittest.mock import patch, MagicMock
from decimal import Decimal
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), ".")))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from ecommerce.produto import Produto
from ecommerce.carrinho import Carrinho
from ecommerce.pedido import Pedido, StatusPedido
from ecommerce.sistema_ecommerce import SistemaEcommerce
from ecommerce.sistema_pagamento import SistemaPagamento

class TestFluxoCompraCompleto(unittest.TestCase):
    #Da adição ao carrinho até o pagamento.
    def setUp(self):
        self.sistema = SistemaEcommerce()

        # Adicionar produtos reais ao sistema
        self.produto_pix = Produto(id_produto=801, nome="Produto PIX", descricao="Desc PIX", preco=200.0, quantidade_estoque=10, categoria="Fluxo")
        self.produto_cc_vista = Produto(id_produto=802, nome="Produto CC Vista", descricao="Desc CCV", preco=150.0, quantidade_estoque=10, categoria="Fluxo")
        self.produto_cc_parc = Produto(id_produto=803, nome="Produto CC Parc", descricao="Desc CCP", preco=500.0, quantidade_estoque=10, categoria="Fluxo")

        self.sistema.adicionar_produto(self.produto_pix)
        self.sistema.adicionar_produto(self.produto_cc_vista)
        self.sistema.adicionar_produto(self.produto_cc_parc)

        self.id_cliente = "cliente_fluxo"
        self.endereco = {"rua": "Rua Fluxo Completo", "cep": "88888-000"}

    @patch.object(SistemaPagamento, 
                  "_verificar_fraude", 
                  return_value=True) # Mock para sempre passar na verificação de fraude
    @patch.object(SistemaPagamento, 
                  "_autorizar_pagamento", 
                  return_value=True) # Mock para sempre autorizar o pagamento
    def test_fluxo_completo_pix(self, mock_autorizar, mock_fraude):
        #Questão 8: Fluxo completo com pagamento via PIX
        
        # 1. Adicionar produto ao carrinho
        carrinho = Carrinho()
        carrinho.adicionar_item(self.produto_pix, 1)
        self.assertEqual(len(carrinho), 1)

        # 2. Criar pedido
        # Mockar calcular_frete para isolar o teste
        with patch("ecommerce.pedido.Pedido.calcular_frete", return_value=Decimal("10.00")):
            pedido = self.sistema.criar_pedido(self.id_cliente, carrinho, self.endereco, "PIX")
        
        self.assertIsNotNone(pedido)
        id_pedido = pedido.id_pedido
        self.assertEqual(pedido.status, StatusPedido.PENDENTE)
        self.assertAlmostEqual(pedido.valor_total, Decimal("210.00")) # 200.00 (produto) + 10.00 (frete) = 210.00

        # 3. Processar pagamento PIX 
        dados_pagamento = {}
        resultado_pagamento = self.sistema.processar_pagamento_pedido(id_pedido, dados_pagamento)

        # 4. Verificar resultado
        self.assertTrue(resultado_pagamento)
        mock_fraude.assert_called_once() 
        mock_autorizar.assert_called_once() #se mock foi chamado

        pedido_pago = self.sistema.buscar_pedido_por_id(id_pedido)
        self.assertIsNotNone(pedido_pago)
        self.assertEqual(pedido_pago.status, StatusPedido.PAGO)
        self.assertIsNotNone(pedido_pago.data_pagamento)
        self.assertIsNotNone(pedido_pago.id_transacao_pagamento)
        self.assertAlmostEqual(pedido_pago.valor_total, Decimal("199.50"))  # desconto = 210.00 * (1 - 0.05) = 210.00 * 0.95 = 199.50

        self.assertTrue(pedido_pago.atualizar_status(StatusPedido.EM_SEPARACAO))
        self.assertTrue(pedido_pago.atualizar_status(StatusPedido.ENVIADO))
        self.assertTrue(pedido_pago.atualizar_status(StatusPedido.ENTREGUE))

    @patch.object(SistemaPagamento, "_verificar_fraude", return_value=True)
    @patch.object(SistemaPagamento, "_autorizar_pagamento", return_value=True)
    def test_fluxo_completo_cartao_vista(self, mock_autorizar, mock_fraude):
        #Questão 8: Fluxo completo com pagamento via cartão de crédito à vista
        
        # 1. Adicionar produto ao carrinho
        carrinho = Carrinho()
        carrinho.adicionar_item(self.produto_cc_vista, 2) # 2 * 150.0 = 300.0
        self.assertEqual(len(carrinho), 1)

        # 2. Criar pedido
        with patch("ecommerce.pedido.Pedido.calcular_frete", return_value=Decimal("20.00")):
            pedido = self.sistema.criar_pedido(self.id_cliente, carrinho, self.endereco, "Cartão de Crédito")
        
        self.assertIsNotNone(pedido)
        id_pedido = pedido.id_pedido
        self.assertEqual(pedido.status, StatusPedido.PENDENTE)
        
        self.assertAlmostEqual(pedido.valor_total, Decimal("320.00")) # = 300.00 (produto) + 20.00 (frete) = 320.00

        # 3. Processar pagamento Cartão à Vista 
        dados_pagamento = {"num_parcelas": 1, "dados_cartao": {}}
        resultado_pagamento = self.sistema.processar_pagamento_pedido(id_pedido, dados_pagamento)

        # 4. Verificar resultado
        self.assertTrue(resultado_pagamento)
        mock_fraude.assert_called_once()
        mock_autorizar.assert_called_once()

        pedido_pago = self.sistema.buscar_pedido_por_id(id_pedido)
        self.assertIsNotNone(pedido_pago)
        self.assertEqual(pedido_pago.status, StatusPedido.PAGO)
        self.assertIsNotNone(pedido_pago.data_pagamento)
        self.assertIsNotNone(pedido_pago.id_transacao_pagamento)
        self.assertAlmostEqual(pedido_pago.valor_total, Decimal("320.00"))
        self.assertEqual(pedido_pago.num_parcelas, 1)
        self.assertIsNone(pedido_pago.valor_parcela) # Valor da parcela é None para 1x

    @patch.object(SistemaPagamento, "_verificar_fraude", return_value=True)
    @patch.object(SistemaPagamento, "_autorizar_pagamento", return_value=True)
    def test_fluxo_completo_cartao_parcelado(self, mock_autorizar, mock_fraude):
        #Questão 8: Fluxo completo com pagamento via cartão de crédito parcelado
        
        # 1. Adicionar produto ao carrinho
        carrinho = Carrinho()
        carrinho.adicionar_item(self.produto_cc_parc, 1) # 1 * 500.0 = 500.0
        self.assertEqual(len(carrinho), 1)

        # 2. Criar pedido
        with patch("ecommerce.pedido.Pedido.calcular_frete", return_value=Decimal("25.00")):
            pedido = self.sistema.criar_pedido(self.id_cliente, carrinho, self.endereco, "Cartão de Crédito")
        
        self.assertIsNotNone(pedido)
        id_pedido = pedido.id_pedido
        self.assertEqual(pedido.status, StatusPedido.PENDENTE)
        # Valor total inicial 
        self.assertAlmostEqual(pedido.valor_total, Decimal("525.00")) # = 500.00 (produto) + 25.00 (frete) = 525.00

        # 3. Processar pagamento Cartão Parcelado
        num_parcelas = 3
        dados_pagamento = {"num_parcelas": num_parcelas, "dados_cartao": {}}
        resultado_pagamento = self.sistema.processar_pagamento_pedido(id_pedido, dados_pagamento)

        # 4. Verificar resultado
        self.assertTrue(resultado_pagamento)
        mock_fraude.assert_called_once()
        mock_autorizar.assert_called_once()

        pedido_pago = self.sistema.buscar_pedido_por_id(id_pedido)
        self.assertIsNotNone(pedido_pago)
        self.assertEqual(pedido_pago.status, StatusPedido.PAGO)
        self.assertIsNotNone(pedido_pago.data_pagamento)
        self.assertIsNotNone(pedido_pago.id_transacao_pagamento)
        self.assertEqual(pedido_pago.num_parcelas, num_parcelas)
        self.assertIsNotNone(pedido_pago.valor_parcela) 
        
        valor_parcela_esperado = Decimal("182.05") # Parcela(3x, juros 2%) 
        valor_total_pago_esperado = Decimal("546.15") # 182.05 * 3 = 546.15
        self.assertAlmostEqual(pedido_pago.valor_parcela, valor_parcela_esperado, places=2)
        self.assertAlmostEqual(pedido_pago.valor_total, valor_total_pago_esperado, places=2)

if __name__ == '__main__':
    unittest.main()

