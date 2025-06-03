import pytest
# Ajusta o path para encontrar o módulo ecommerce
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from ecommerce.produto import Produto

# --- Fixtures (opcional, mas útil para reutilizar instâncias) ---

@pytest.fixture
def produto_valido() -> Produto:
    """Fixture que retorna uma instância válida de Produto."""
    return Produto(id_produto=1, nome="Teste", descricao="Desc Teste", preco=10.0, quantidade_estoque=5, categoria="Testes")

# --- Testes para a Classe Produto ---

def test_criacao_produto_sucesso(produto_valido):
    """Verifica se a criação de um produto com dados válidos funciona.

    Questão 1: Verificação da criação de um produto
    """
    assert produto_valido.id_produto == 1
    assert produto_valido.nome == "Teste"
    assert produto_valido.descricao == "Desc Teste"
    assert produto_valido.preco == 10.0
    assert produto_valido.quantidade_estoque == 5
    assert produto_valido.categoria == "Testes"

def test_criacao_produto_preco_invalido():
    """Verifica se a criação de produto falha com preço inválido (zero ou negativo).

    Questão 1: Verificação da criação de um produto (caso de erro)
    """
    with pytest.raises(ValueError, match="O preço do produto deve ser positivo."):
        Produto(id_produto=2, nome="Preco Zero", descricao="", preco=0.0, quantidade_estoque=1, categoria="Erro")
    with pytest.raises(ValueError, match="O preço do produto deve ser positivo."):
        Produto(id_produto=3, nome="Preco Negativo", descricao="", preco=-5.0, quantidade_estoque=1, categoria="Erro")

def test_criacao_produto_estoque_invalido():
    """Verifica se a criação de produto falha com estoque inválido (negativo).

    Questão 1: Verificação da criação de um produto (caso de erro)
    """
    with pytest.raises(ValueError, match="A quantidade em estoque não pode ser negativa."):
        Produto(id_produto=4, nome="Estoque Negativo", descricao="", preco=10.0, quantidade_estoque=-1, categoria="Erro")

def test_verificar_disponibilidade_estoque_suficiente(produto_valido):
    """Verifica a disponibilidade quando há estoque suficiente.

    Questão 1: Verificação da disponibilidade de estoque
    """
    assert produto_valido.verificar_disponibilidade(1) is True
    assert produto_valido.verificar_disponibilidade(5) is True

def test_verificar_disponibilidade_estoque_insuficiente(produto_valido):
    """Verifica a disponibilidade quando não há estoque suficiente.

    Questão 1: Verificação da disponibilidade de estoque
    """
    assert produto_valido.verificar_disponibilidade(6) is False
    assert produto_valido.verificar_disponibilidade(100) is False

def test_verificar_disponibilidade_quantidade_invalida(produto_valido):
    """Verifica se a verificação de disponibilidade falha com quantidade inválida.

    Questão 1: Verificação da disponibilidade de estoque (caso de erro)
    """
    with pytest.raises(ValueError, match="A quantidade desejada deve ser positiva."):
        produto_valido.verificar_disponibilidade(0)
    with pytest.raises(ValueError, match="A quantidade desejada deve ser positiva."):
        produto_valido.verificar_disponibilidade(-1)

def test_atualizar_estoque_reducao_sucesso(produto_valido):
    """Verifica a redução de estoque válida.

    Questão 1: Verificação da redução de estoque
    """
    estoque_inicial = produto_valido.quantidade_estoque
    quantidade_reduzir = -2
    produto_valido.atualizar_estoque(quantidade_reduzir)
    assert produto_valido.quantidade_estoque == estoque_inicial + quantidade_reduzir # 5 - 2 = 3

def test_atualizar_estoque_aumento_sucesso(produto_valido):
    """Verifica o aumento de estoque válido.

    Questão 1: Verificação da atualização de estoque (aumento)
    """
    estoque_inicial = produto_valido.quantidade_estoque
    quantidade_aumentar = 3
    produto_valido.atualizar_estoque(quantidade_aumentar)
    assert produto_valido.quantidade_estoque == estoque_inicial + quantidade_aumentar # 5 + 3 = 8

def test_atualizar_estoque_para_zero(produto_valido):
    """Verifica se o estoque pode ser zerado.

    Questão 1: Verificação da redução de estoque
    """
    produto_valido.atualizar_estoque(-produto_valido.quantidade_estoque)
    assert produto_valido.quantidade_estoque == 0
    assert produto_valido.verificar_disponibilidade(1) is False # Confirma indisponibilidade

def test_atualizar_estoque_negativo_falha(produto_valido):
    """Verifica se a atualização falha ao tentar deixar o estoque negativo.

    Questão 1: Verificação da redução de estoque (caso de erro)
    """
    estoque_inicial = produto_valido.quantidade_estoque
    quantidade_reduzir_excesso = -(estoque_inicial + 1) # Tenta remover mais do que existe
    with pytest.raises(ValueError, match="A atualização resultaria em estoque negativo."):
        produto_valido.atualizar_estoque(quantidade_reduzir_excesso)
    # Garante que o estoque não foi alterado após a falha
    assert produto_valido.quantidade_estoque == estoque_inicial

def test_obter_informacoes(produto_valido):
    """Verifica se o método obter_informacoes retorna o dicionário correto.
    """
    info = produto_valido.obter_informacoes()
    assert info == {
        "id_produto": 1,
        "nome": "Teste",
        "descricao": "Desc Teste",
        "preco": 10.0,
        "quantidade_estoque": 5,
        "categoria": "Testes"
    }

def test_representacao_string(produto_valido):
    """Verifica a representação em string (__str__) do produto.
    """
    assert str(produto_valido) == "Teste - R$ 10.00"

def test_representacao_oficial(produto_valido):
    """Verifica a representação oficial (__repr__) do produto.
    """
    expected_repr = "Produto(id_produto=1, nome='Teste', descricao='Desc Teste', preco=10.0, quantidade_estoque=5, categoria='Testes')"
    assert repr(produto_valido) == expected_repr

