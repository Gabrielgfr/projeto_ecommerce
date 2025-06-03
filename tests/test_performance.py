import unittest
import time
import pytest
from unittest.mock import patch
from decimal import Decimal

# Ajusta o path para encontrar o módulo ecommerce
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), ".")))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from ecommerce.produto import Produto
from ecommerce.carrinho import Carrinho
from ecommerce.pedido import Pedido, StatusPedido
from ecommerce.sistema_ecommerce import SistemaEcommerce
from ecommerce.sistema_pagamento import SistemaPagamento

# --- Configurações de Performance (Exemplos) ---
NUM_ITENS_CARRINHO_PERF = 1000
NUM_PEDIDOS_VOLUME_PERF = 100
TEMPO_LIMITE_CARRINHO_MS = 500
TEMPO_LIMITE_PAGAMENTO_MS = 100
TEMPO_LIMITE_PEDIDO_MEDIO_MS = 150

# --- Testes com Pytest (Adição ao Carrinho) ---

@pytest.fixture(scope="module")
def produtos_para_carrinho():
    produtos = []
    for i in range(NUM_ITENS_CARRINHO_PERF):
        produtos.append(Produto(id_produto=1000 + i, nome=f"Perf Produto {i}",
                                descricao="Desc Perf", preco=10.0,
                                quantidade_estoque=NUM_ITENS_CARRINHO_PERF * 2,
                                categoria="PerfTest"))
    return produtos

@pytest.fixture
def carrinho_perf():
    return Carrinho()

# Teste de adição de múltiplos produtos distintos ao carrinho
def test_performance_adicao_multiplos_produtos_distintos(carrinho_perf, produtos_para_carrinho):
    # Questão 10:O tempo de resposta para adição de múltiplos produtos ao carrinho

    start_time = time.perf_counter()

    for produto in produtos_para_carrinho:
        try:
            carrinho_perf.adicionar_item(produto, 1)
        except ValueError as e:
            pytest.fail(f"Erro ao adicionar item {produto.id_produto}: {e}")

    end_time = time.perf_counter()
    duration_ms = (end_time - start_time) * 1000

    print(f"\n[Perf Carrinho - Distintos] Tempo: {duration_ms:.2f} ms")
    assert duration_ms < TEMPO_LIMITE_CARRINHO_MS
    assert len(carrinho_perf) == NUM_ITENS_CARRINHO_PERF

#Mede o tempo para adicionar múltiplas unidades do mesmo produto.
def test_performance_adicao_multiplas_unidades_mesmo_produto(carrinho_perf, produtos_para_carrinho):
    # Questão 10:O tempo de resposta para adição de múltiplas unidades do mesmo produto ao carrinho
    produto_unico = produtos_para_carrinho[0]

    start_time = time.perf_counter()

    for i in range(NUM_ITENS_CARRINHO_PERF):
        try:
            carrinho_perf.adicionar_item(produto_unico, 1)
        except ValueError as e:
            pytest.fail(f"Erro ao adicionar unidade {i+1} do produto {produto_unico.id_produto}: {e}")

    end_time = time.perf_counter()
    duration_ms = (end_time - start_time) * 1000

    print(f"\n[Perf Carrinho - Mesmo Item] Tempo: {duration_ms:.2f} ms")
    assert duration_ms < TEMPO_LIMITE_CARRINHO_MS
    assert len(carrinho_perf) == 1
    assert carrinho_perf.itens[produto_unico] == NUM_ITENS_CARRINHO_PERF

# --- Testes com unittest (Pagamento e Volume de Pedidos) ---

class TestPerformancePagamento(unittest.TestCase):
    def setUp(self):
        self.sistema = SistemaEcommerce()
        # Corrigido: 'desc' para 'descricao', 'qtd' para 'quantidade_estoque', 'cat' para 'categoria'
        self.produto = Produto(id_produto=1001, nome="Perf Pagto Prod", descricao="", preco=10.0, quantidade_estoque=10, categoria="Perf")
        self.sistema.adicionar_produto(self.produto)

        carrinho = Carrinho()
        carrinho.adicionar_item(self.produto, 1)
        endereco = {"rua": "Rua Perf Pagto", "cep": "10101-000"}
        id_cliente = "cliente_perf_pagto"

        with patch("ecommerce.pedido.Pedido.calcular_frete", return_value=Decimal("5.00")):
            self.pedido = self.sistema.criar_pedido(id_cliente, carrinho, endereco, "Cartão de Crédito")
        self.assertIsNotNone(self.pedido)

    @patch.object(SistemaPagamento, "_verificar_fraude", return_value=True)
    @patch.object(SistemaPagamento, "_autorizar_pagamento", return_value=True)
    def test_performance_processamento_pagamento(self, mock_autorizar, mock_fraude):
        # Questão 10: O tempo de processamento de pagamento
        dados_pagamento = {"num_parcelas": 1, "dados_cartao": {}}
        start_time = time.perf_counter()

        resultado = self.sistema.processar_pagamento_pedido(self.pedido.id_pedido, dados_pagamento)

        end_time = time.perf_counter()
        duration_ms = (end_time - start_time) * 1000

        print(f"\n[Perf Pagamento] Tempo: {duration_ms:.2f} ms")
        self.assertTrue(resultado)
        self.assertLess(duration_ms, TEMPO_LIMITE_PAGAMENTO_MS)

        pedido_atualizado = self.sistema.buscar_pedido_por_id(self.pedido.id_pedido)
        self.assertEqual(pedido_atualizado.status, StatusPedido.PAGO)

class TestPerformanceVolumePedidos(unittest.TestCase):
    def setUp(self):
        self.sistema_volume = SistemaEcommerce()
        self.produtos_volume = []
        for i in range(NUM_PEDIDOS_VOLUME_PERF):
            # Corrigido: 'desc' para 'descricao', 'qtd' para 'quantidade_estoque', 'cat' para 'categoria'
            p = Produto(id_produto=2000 + i, nome=f"Volume Prod {i}", descricao="",
                        preco=5.0, quantidade_estoque=2, categoria="Volume")
            self.produtos_volume.append(p)
            self.sistema_volume.adicionar_produto(p)

        self.endereco_volume = {"rua": "Rua Volume", "cep": "20202-000"}
        self.id_cliente_base = "cliente_volume_"

    @patch.object(SistemaPagamento, "_verificar_fraude", return_value=True)
    @patch.object(SistemaPagamento, "_autorizar_pagamento", return_value=True)
    def test_performance_volume_pedidos_sequencial(self, mock_autorizar, mock_fraude):
        #Questão 10: O comportamento do sistema com um grande volume de pedidos simultâneos 
        tempos_pedidos = []
        start_total_time = time.perf_counter()

        for i in range(NUM_PEDIDOS_VOLUME_PERF):
            start_pedido_time = time.perf_counter()
            carrinho = Carrinho()
            produto_idx = i % len(self.produtos_volume)
            try:
                carrinho.adicionar_item(self.produtos_volume[produto_idx], 1)
            except ValueError:
                continue

            id_cliente = f"{self.id_cliente_base}{i}"
            metodo_pagamento = "PIX" if i % 2 == 0 else "Cartão de Crédito"

            with patch("ecommerce.pedido.Pedido.calcular_frete", return_value=Decimal("2.00")):
                pedido = self.sistema_volume.criar_pedido(id_cliente, carrinho, self.endereco_volume, metodo_pagamento)

            if pedido:
                dados_pagamento = {"num_parcelas": 1} if metodo_pagamento == "Cartão de Crédito" else {}
                self.sistema_volume.processar_pagamento_pedido(pedido.id_pedido, dados_pagamento)
                end_pedido_time = time.perf_counter()
                tempos_pedidos.append((end_pedido_time - start_pedido_time) * 1000)

        end_total_time = time.perf_counter()
        duration_total_ms = (end_total_time - start_total_time) * 1000

        num_pedidos_sucesso = len(tempos_pedidos)
        tempo_medio_ms = sum(tempos_pedidos) / num_pedidos_sucesso if num_pedidos_sucesso else 0

        print(f"\n[Perf Volume] Total: {duration_total_ms:.2f} ms")
        print(f"[Perf Volume] Média por pedido: {tempo_medio_ms:.2f} ms")
        self.assertLess(tempo_medio_ms, TEMPO_LIMITE_PEDIDO_MEDIO_MS)