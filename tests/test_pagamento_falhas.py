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

# --- Fixtures ---

@pytest.fixture
def sistema_com_produto():
    """Fixture para criar um SistemaEcommerce com um produto."""
    sistema = SistemaEcommerce()
    produto = Produto(id_produto=701, nome="Produto Falha Pagto", descricao="Desc FP", preco=100.0, quantidade_estoque=10, categoria="Falha")
    sistema.adicionar_produto(produto)
    return sistema, produto

@pytest.fixture
def pedido_pendente(sistema_com_produto):
    """Fixture para criar um pedido pendente no sistema."""
    sistema, produto = sistema_com_produto
    carrinho = Carrinho()
    carrinho.adicionar_item(produto, 1)
    endereco = {"rua": "Rua Falha", "cep": "77777-000"}
    id_cliente = "cliente_falha"
    # Usar patch no calcular_frete durante a criação do pedido
    with patch("ecommerce.pedido.Pedido.calcular_frete", return_value=Decimal("10.00")):
        pedido = sistema.criar_pedido(id_cliente, carrinho, endereco, "Cartão de Crédito")
    assert pedido is not None
    assert pedido.status == StatusPedido.PENDENTE
    return sistema, pedido

# --- Testes de Falha no Pagamento (usando Mock) ---

def test_falha_autorizacao_cartao_credito(pedido_pendente, mocker): # mocker é a fixture do pytest-mock
    """Simula falha na autorização do cartão e verifica o status do pedido.

    Questão 7: Simular falha na autorização do cartão de crédito
    Questão 7: Verificar se o sistema mantém o pedido no estado correto após falhas
    """
    sistema, pedido = pedido_pendente
    id_pedido = pedido.id_pedido

    # Mock o método _autorizar_pagamento dentro da instância de SistemaPagamento usada pelo sistema
    # para sempre retornar False (falha na autorização)
    mocker.patch.object(sistema.sistema_pagamento, 
                        "_autorizar_pagamento", 
                        return_value=False, 
                        autospec=True) # autospec garante que a assinatura do mock está correta
    
    # Mock a verificação de fraude para retornar True (sem fraude) para isolar a falha na autorização
    mocker.patch.object(sistema.sistema_pagamento, 
                        "_verificar_fraude", 
                        return_value=True, 
                        autospec=True)

    # Tenta processar o pagamento com cartão
    dados_pagamento_cc = {"num_parcelas": 1, "dados_cartao": {}}
    resultado = sistema.processar_pagamento_pedido(id_pedido, dados_pagamento_cc)

    # Verifica o resultado
    assert resultado is False # Pagamento deve falhar

    # Verifica o estado do pedido
    pedido_apos_falha = sistema.buscar_pedido_por_id(id_pedido)
    assert pedido_apos_falha is not None
    assert pedido_apos_falha.status == StatusPedido.FALHA_PAGAMENTO
    assert pedido_apos_falha.data_pagamento is None
    assert pedido_apos_falha.id_transacao_pagamento is None

def test_simular_timeout_gateway(pedido_pendente, mocker):
    """Simula um timeout (tratado como falha na autorização) e verifica o status.

    Questão 7: Simular timeout na comunicação com o gateway de pagamento
    Questão 7: Verificar se o sistema mantém o pedido no estado correto após falhas"""
    
    sistema, pedido = pedido_pendente
    id_pedido = pedido.id_pedido
    pedido.metodo_pagamento = "PIX" # Muda para PIX para variar o teste

    # Mock _autorizar_pagamento para retornar False (simulando falha/timeout)
    mocker.patch.object(sistema.sistema_pagamento, "_autorizar_pagamento", return_value=False, autospec=True)
    mocker.patch.object(sistema.sistema_pagamento, "_verificar_fraude", return_value=True, autospec=True)

    # Tenta processar o pagamento com PIX
    dados_pagamento_pix = {}
    resultado = sistema.processar_pagamento_pedido(id_pedido, dados_pagamento_pix)

    # Verifica o resultado
    assert resultado is False

    # Verifica o estado do pedido
    pedido_apos_falha = sistema.buscar_pedido_por_id(id_pedido)
    assert pedido_apos_falha is not None
    assert pedido_apos_falha.status == StatusPedido.FALHA_PAGAMENTO
    assert pedido_apos_falha.data_pagamento is None
    assert pedido_apos_falha.id_transacao_pagamento is None

def test_falha_por_fraude(pedido_pendente, mocker):
    """Simula a detecção de fraude durante o processamento.

    Questão 7: Verificar se o sistema mantém o pedido no estado correto após falhas (fraude)
    """
    sistema, pedido = pedido_pendente
    id_pedido = pedido.id_pedido

    # Mock _verificar_fraude para retornar False (fraude detectada)
    mocker.patch.object(sistema.sistema_pagamento, "_verificar_fraude", return_value=False, autospec=True)
    # Mock _autorizar_pagamento para retornar True (não deve ser chamado se fraude for detectada antes)
    mock_autorizar = mocker.patch.object(sistema.sistema_pagamento, "_autorizar_pagamento", return_value=True, autospec=True)

    # Tenta processar o pagamento com cartão
    dados_pagamento_cc = {"num_parcelas": 1, "dados_cartao": {}}
    resultado = sistema.processar_pagamento_pedido(id_pedido, dados_pagamento_cc)

    # Verifica o resultado
    assert resultado is False # Pagamento deve falhar devido à fraude

    # Verifica o estado do pedido
    pedido_apos_fraude = sistema.buscar_pedido_por_id(id_pedido)
    assert pedido_apos_fraude is not None
    # O status deve ir para FALHA_PAGAMENTO (ou um status específico de fraude se existisse)
    # A implementação atual de processar_pagamento_pedido chama registrar_pagamento(False,...)
    # que leva a FALHA_PAGAMENTO.
    assert pedido_apos_fraude.status == StatusPedido.FALHA_PAGAMENTO
    assert pedido_apos_fraude.data_pagamento is None
    assert pedido_apos_fraude.id_transacao_pagamento is None

    # Garante que a autorização não foi chamada
    mock_autorizar.assert_not_called()

