import pytest
from unittest.mock import patch
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

# --- Fixtures ---

@pytest.fixture
def sistema_com_produto():
    sistema = SistemaEcommerce()
    produto = Produto(id_produto=701, nome="Produto Falha Pagto", descricao="Desc FP", preco=100.0, quantidade_estoque=10, categoria="Falha")
    sistema.adicionar_produto(produto)
    return sistema, produto

@pytest.fixture
def pedido_pendente(sistema_com_produto):
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

# --- Testes de Falha no Pagamento ---

def test_falha_autorizacao_cartao_credito(pedido_pendente, mocker): 
    #Questão 7: Simular falha na autorização do cartão de crédito
    #Questão 7: Verificar se o sistema mantém o pedido no estado correto após falhas
    
    sistema, pedido = pedido_pendente
    id_pedido = pedido.id_pedido

    mocker.patch.object(sistema.sistema_pagamento, 
                        "_autorizar_pagamento", 
                        return_value=False, 
                        autospec=True) # garante que a assinatura do mock está correta
    
    # Mock a verificação de fraude para sem fraudepara isolar a falha na autorização
    mocker.patch.object(sistema.sistema_pagamento, 
                        "_verificar_fraude", 
                        return_value=True, 
                        autospec=True)

    # Tenta processar o pagamento com cartão
    dados_pagamento_cc = {"num_parcelas": 1, "dados_cartao": {}}
    resultado = sistema.processar_pagamento_pedido(id_pedido, dados_pagamento_cc)

    # Verifica o resultado
    assert resultado is False 

    # Verifica o estado do pedido
    pedido_apos_falha = sistema.buscar_pedido_por_id(id_pedido)
    assert pedido_apos_falha is not None
    assert pedido_apos_falha.status == StatusPedido.FALHA_PAGAMENTO
    assert pedido_apos_falha.data_pagamento is None
    assert pedido_apos_falha.id_transacao_pagamento is None

def test_simular_timeout_gateway(pedido_pendente, mocker):
    #Questão 7: timeout na comunicação com o gateway de pagamento
    #Questão 7: o sistema mantém o pedido no estado correto após falhas
    
    sistema, pedido = pedido_pendente
    id_pedido = pedido.id_pedido
    pedido.metodo_pagamento = "PIX"

    # Mock _autorizar_pagamento para retornar False paara falha/timeout
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
    #Questão 7: Verificar se o sistema mantém o pedido no estado correto após falhas/fraude
    
    sistema, pedido = pedido_pendente
    id_pedido = pedido.id_pedido

    # Mock _verificar_fraude
    mocker.patch.object(sistema.sistema_pagamento, "_verificar_fraude", return_value=False, autospec=True)
    mock_autorizar = mocker.patch.object(sistema.sistema_pagamento, "_autorizar_pagamento", return_value=True, autospec=True)

    # Tenta processar o pagamento com cartão
    dados_pagamento_cc = {"num_parcelas": 1, "dados_cartao": {}}
    resultado = sistema.processar_pagamento_pedido(id_pedido, dados_pagamento_cc)

    assert resultado is False 

    # Verifica o estado do pedido
    pedido_apos_fraude = sistema.buscar_pedido_por_id(id_pedido)
    assert pedido_apos_fraude is not None
    assert pedido_apos_fraude.status == StatusPedido.FALHA_PAGAMENTO
    assert pedido_apos_fraude.data_pagamento is None
    assert pedido_apos_fraude.id_transacao_pagamento is None

    mock_autorizar.assert_not_called()

