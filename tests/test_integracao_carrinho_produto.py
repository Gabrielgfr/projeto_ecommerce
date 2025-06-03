import pytest
# Ajusta o path para encontrar o módulo ecommerce
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from ecommerce.produto import Produto
from ecommerce.carrinho import Carrinho

# --- Fixtures ---

@pytest.fixture
def produto_a() -> Produto:
    """Produto A com estoque inicial."""
    # Retorna uma nova instância a cada teste para evitar efeitos colaterais
    return Produto(id_produto=201, nome="Produto A", descricao="Desc A", preco=10.0, quantidade_estoque=5, categoria="Integ")

@pytest.fixture
def produto_b() -> Produto:
    """Produto B com estoque inicial."""
    return Produto(id_produto=202, nome="Produto B", descricao="Desc B", preco=25.0, quantidade_estoque=3, categoria="Integ")

@pytest.fixture
def produto_sem_estoque() -> Produto:
    """Produto C inicialmente sem estoque."""
    return Produto(id_produto=203, nome="Produto C", descricao="Desc C", preco=50.0, quantidade_estoque=0, categoria="Integ")

@pytest.fixture
def carrinho_vazio() -> Carrinho:
    """Carrinho vazio para cada teste."""
    return Carrinho()

# --- Testes de Integração (Carrinho e Produto) ---

def test_integracao_adicionar_atualiza_total(carrinho_vazio, produto_a, produto_b):
    """Verifica se o carrinho atualiza corretamente o valor total ao adicionar produtos.

    Questão 4: Se o carrinho atualiza corretamente o valor total ao adicionar produtos
    """
    # Adiciona Produto A (1 * 10.0 = 10.0)
    carrinho_vazio.adicionar_item(produto_a, 1)
    assert carrinho_vazio.calcular_total() == 10.0

    # Adiciona Produto B (2 * 25.0 = 50.0)
    carrinho_vazio.adicionar_item(produto_b, 2)
    # Total esperado = 10.0 + 50.0 = 60.0
    assert carrinho_vazio.calcular_total() == 60.0

    # Adiciona mais do Produto A (3 * 10.0 = 30.0)
    carrinho_vazio.adicionar_item(produto_a, 3)
    # Total esperado = (1+3)*10.0 + 2*25.0 = 40.0 + 50.0 = 90.0
    assert carrinho_vazio.calcular_total() == 90.0

def test_integracao_impede_adicao_sem_estoque(carrinho_vazio, produto_a, produto_sem_estoque):
    """Verifica se o carrinho impede a adição de produtos sem estoque.

    Questão 4: Se o carrinho impede a adição de produtos sem estoque
    """
    # Tenta adicionar produto_sem_estoque (estoque 0)
    with pytest.raises(ValueError, match="Estoque insuficiente para adicionar 1 unidade\(s\) de Produto C."):
        carrinho_vazio.adicionar_item(produto_sem_estoque, 1)
    assert len(carrinho_vazio) == 0 # Carrinho deve continuar vazio

    # Adiciona produto_a (estoque 5)
    carrinho_vazio.adicionar_item(produto_a, 5)
    assert carrinho_vazio.itens[produto_a] == 5

    # Tenta adicionar mais uma unidade de produto_a (excedendo o estoque)
    with pytest.raises(ValueError, match="Estoque insuficiente para adicionar mais 1 unidade\(s\) de Produto A. Total desejado: 6, Estoque: 5"):
        carrinho_vazio.adicionar_item(produto_a, 1)
    # Quantidade no carrinho deve permanecer 5
    assert carrinho_vazio.itens[produto_a] == 5

def test_integracao_permite_remocao_parcial(carrinho_vazio, produto_a, produto_b):
    """Verifica se o carrinho permite remover produtos parcialmente, atualizando o total.

    Questão 4: Se o carrinho permite remover produtos parcialmente
    """
    # Adiciona itens
    carrinho_vazio.adicionar_item(produto_a, 4) # 4 * 10.0 = 40.0
    carrinho_vazio.adicionar_item(produto_b, 3) # 3 * 25.0 = 75.0
    # Total inicial = 40.0 + 75.0 = 115.0
    assert carrinho_vazio.calcular_total() == 115.0
    assert carrinho_vazio.itens[produto_a] == 4
    assert carrinho_vazio.itens[produto_b] == 3

    # Remove parcialmente Produto A
    carrinho_vazio.remover_item(produto_a, 2) # Remove 2 unidades
    # Quantidade restante Produto A = 4 - 2 = 2
    # Novo total = (2 * 10.0) + (3 * 25.0) = 20.0 + 75.0 = 95.0
    assert carrinho_vazio.itens[produto_a] == 2
    assert carrinho_vazio.calcular_total() == 95.0

    # Remove parcialmente Produto B
    carrinho_vazio.remover_item(produto_b, 1) # Remove 1 unidade
    # Quantidade restante Produto B = 3 - 1 = 2
    # Novo total = (2 * 10.0) + (2 * 25.0) = 20.0 + 50.0 = 70.0
    assert carrinho_vazio.itens[produto_b] == 2
    assert carrinho_vazio.calcular_total() == 70.0

def test_integracao_remocao_total_atualiza_total(carrinho_vazio, produto_a, produto_b):
    """Verifica se a remoção total de um item atualiza o total corretamente.

    Questão 4: Integração de remoção e cálculo de total.
    """
    carrinho_vazio.adicionar_item(produto_a, 2) # 2 * 10.0 = 20.0
    carrinho_vazio.adicionar_item(produto_b, 1) # 1 * 25.0 = 25.0
    # Total inicial = 20.0 + 25.0 = 45.0
    assert carrinho_vazio.calcular_total() == 45.0

    # Remove totalmente Produto A
    carrinho_vazio.remover_item(produto_a, 2)
    # Total esperado = 25.0 (apenas Produto B)
    assert produto_a not in carrinho_vazio.itens
    assert carrinho_vazio.calcular_total() == 25.0

def test_integracao_atualizar_quantidade_impacta_total(carrinho_vazio, produto_a):
    """Verifica se atualizar a quantidade de um item impacta o total.

    Questão 4: Integração de atualização de quantidade e cálculo de total.
    """
    carrinho_vazio.adicionar_item(produto_a, 1) # 1 * 10.0 = 10.0
    assert carrinho_vazio.calcular_total() == 10.0

    # Atualiza quantidade para 3
    carrinho_vazio.atualizar_quantidade(produto_a, 3) # 3 * 10.0 = 30.0
    assert carrinho_vazio.itens[produto_a] == 3
    assert carrinho_vazio.calcular_total() == 30.0

    # Atualiza quantidade para 0 (remove o item)
    carrinho_vazio.atualizar_quantidade(produto_a, 0)
    assert produto_a not in carrinho_vazio.itens
    assert carrinho_vazio.calcular_total() == 0.0

def test_integracao_atualizar_quantidade_sem_estoque(carrinho_vazio, produto_b):
    """Verifica se a atualização de quantidade falha se não houver estoque.

    Questão 4: Se o carrinho impede a adição (via atualização) de produtos sem estoque
    """
    # produto_b tem estoque 3
    carrinho_vazio.adicionar_item(produto_b, 1)
    assert carrinho_vazio.itens[produto_b] == 1

    # Tenta atualizar para 4 (estoque é 3)
    with pytest.raises(ValueError, match="Estoque insuficiente para atualizar para 4 unidade\(s\) de Produto B."):
        carrinho_vazio.atualizar_quantidade(produto_b, 4)

    # Quantidade deve permanecer 1
    assert carrinho_vazio.itens[produto_b] == 1
    # Total deve permanecer 1 * 25.0 = 25.0
    assert carrinho_vazio.calcular_total() == 25.0

