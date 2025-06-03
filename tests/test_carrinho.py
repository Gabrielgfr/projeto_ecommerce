import unittest
# Ajusta o path para encontrar o módulo ecommerce
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from ecommerce.produto import Produto
from ecommerce.carrinho import Carrinho

"""Classe de teste para a classe Carrinho usando unittest."""
class TestCarrinho(unittest.TestCase):
    

    def setUp(self):
        """Configura o ambiente para cada teste. 
           Cria instâncias de produtos e um carrinho vazio antes de cada método de teste."""

        # Cria produtos com estoque suficiente para a maioria dos testes
        self.produto1 = Produto(id_produto=101, nome="Produto A", descricao="Desc A", preco=50.0, quantidade_estoque=10, categoria="Cat A")
        self.produto2 = Produto(id_produto=102, nome="Produto B", descricao="Desc B", preco=25.5, quantidade_estoque=5, categoria="Cat B")
        
        # Cria um produto com estoque baixo para testes específicos
        self.produto_sem_estoque = Produto(id_produto=103, nome="Produto C", descricao="Desc C", preco=100.0, quantidade_estoque=1, categoria="Cat C")
        
        # Cria um carrinho vazio
        self.carrinho = Carrinho()

    def test_adicao_item_novo(self):
        """ Verifica a adição de um novo item ao carrinho.
            Questão 2: Adição de itens no carrinho """
         
        self.carrinho.adicionar_item(self.produto1, 2)
        self.assertEqual(len(self.carrinho), 1) # Verifica se há 1 tipo de produto
        self.assertIn(self.produto1, self.carrinho.itens) # Verifica se o produto está no carrinho
        self.assertEqual(self.carrinho.itens[self.produto1], 2) # Verifica a quantidade

    def test_adicao_item_existente(self):
        """Verifica a adição de mais unidades de um item já existente.
           Questão 2: Adição de itens no carrinho"""
         
        self.carrinho.adicionar_item(self.produto1, 1) # Adiciona 1 unidade
        self.carrinho.adicionar_item(self.produto1, 3) # Adiciona mais 3 unidades
        self.assertEqual(len(self.carrinho), 1)
        self.assertEqual(self.carrinho.itens[self.produto1], 4) # Verifica a quantidade total (1+3)

    def test_adicao_multiplos_itens(self):
        """Verifica a adição de diferentes itens ao carrinho.
            Questão 2: Adição de itens no carrinho"""
        
        self.carrinho.adicionar_item(self.produto1, 1)
        self.carrinho.adicionar_item(self.produto2, 3)
        self.assertEqual(len(self.carrinho), 2) # Verifica se há 2 tipos de produtos
        self.assertEqual(self.carrinho.itens[self.produto1], 1)
        self.assertEqual(self.carrinho.itens[self.produto2], 3)

    def test_remocao_item_parcial(self):
        """Verifica a remoção parcial de um item do carrinho.
         Questão 2: Remoção de itens do carrinho"""
        
        self.carrinho.adicionar_item(self.produto1, 5)
        self.carrinho.remover_item(self.produto1, 2) # Remove 2 unidades
        self.assertEqual(len(self.carrinho), 1)
        self.assertEqual(self.carrinho.itens[self.produto1], 3) # Verifica a quantidade restante (5-2)

    def test_remocao_item_total(self):
        """Verifica a remoção total de um item (quantidade >= existente).
           Questão 2: Remoção de itens do carrinho"""
        
        self.carrinho.adicionar_item(self.produto1, 3)
        self.carrinho.adicionar_item(self.produto2, 1)
        self.carrinho.remover_item(self.produto1, 3) # Remove todas as unidades do produto1
        self.assertEqual(len(self.carrinho), 1) # Apenas produto2 deve permanecer
        self.assertNotIn(self.produto1, self.carrinho.itens)
        self.assertIn(self.produto2, self.carrinho.itens)

        # Tenta remover mais do que existe (deve remover o item completamente)
        self.carrinho.adicionar_item(self.produto1, 2)
        self.carrinho.remover_item(self.produto1, 5)
        self.assertNotIn(self.produto1, self.carrinho.itens)

    def test_remocao_item_inexistente(self):
        """Verifica a tentativa de remover um item que não está no carrinho.
           Questão 2: Remoção de itens do carrinho (caso de erro)"""
        
        with self.assertRaisesRegex(ValueError, "Produto Produto A não encontrado no carrinho."):
            self.carrinho.remover_item(self.produto1, 1)

    def test_calculo_total_carrinho_vazio(self):
        """Verifica o cálculo do total com o carrinho vazio.
           Questão 2: Cálculo do valor total do carrinho"""
        
        self.assertEqual(self.carrinho.calcular_total(), 0.0)

    def test_calculo_total_um_item(self):
        """Verifica o cálculo do total com um tipo de item.
            Questão 2: Cálculo do valor total do carrinho"""
        
        self.carrinho.adicionar_item(self.produto1, 3) # 3 * 50.0 = 150.0
        self.assertAlmostEqual(self.carrinho.calcular_total(), 150.0)

    def test_calculo_total_multiplos_itens(self):
        """Verifica o cálculo do total com múltiplos itens.
           Questão 2: Cálculo do valor total do carrinho"""
        
        self.carrinho.adicionar_item(self.produto1, 2) # 2 * 50.0 = 100.0
        self.carrinho.adicionar_item(self.produto2, 4) # 4 * 25.5 = 102.0
        # Total = 100.0 + 102.0 = 202.0
        self.assertAlmostEqual(self.carrinho.calcular_total(), 202.0)

    def test_adicao_item_sem_estoque_suficiente(self):
        """Verifica o comportamento ao tentar adicionar produto sem estoque.
           Questão 2: Comportamento quando tenta adicionar um produto sem estoque suficiente"""
        
        # Tenta adicionar mais do que o estoque inicial (produto_sem_estoque tem 1)
        with self.assertRaisesRegex(ValueError, "Estoque insuficiente para adicionar 2 unidade\(s\) de Produto C."):
            self.carrinho.adicionar_item(self.produto_sem_estoque, 2)

        # Verifica se o carrinho não foi modificado
        self.assertNotIn(self.produto_sem_estoque, self.carrinho.itens)
        self.assertEqual(len(self.carrinho), 0)

    def test_adicao_item_existente_sem_estoque_suficiente(self):
        """Verifica o comportamento ao adicionar mais de um item existente, excedendo o estoque.
           Questão 2: Comportamento quando tenta adicionar um produto sem estoque suficiente"""
        
        # Adiciona 1 unidade (estoque permite)
        self.carrinho.adicionar_item(self.produto_sem_estoque, 1)
        self.assertEqual(self.carrinho.itens[self.produto_sem_estoque], 1)

        # Tenta adicionar mais 1 unidade (total 2, estoque é 1)
        with self.assertRaisesRegex(ValueError, "Estoque insuficiente para adicionar mais 1 unidade\(s\) de Produto C. Total desejado: 2, Estoque: 1"):
            self.carrinho.adicionar_item(self.produto_sem_estoque, 1)

        # Verifica se a quantidade no carrinho permaneceu 1
        self.assertEqual(self.carrinho.itens[self.produto_sem_estoque], 1)

    def test_atualizar_quantidade_sem_estoque_suficiente(self):
        """Verifica a atualização de quantidade para um valor maior que o estoque.
            Questão 2: Comportamento quando tenta adicionar um produto sem estoque suficiente (via atualização)"""
        
        self.carrinho.adicionar_item(self.produto_sem_estoque, 1)
        # Tenta atualizar para 2 (estoque é 1)
        with self.assertRaisesRegex(ValueError, "Estoque insuficiente para atualizar para 2 unidade\(s\) de Produto C."):
            self.carrinho.atualizar_quantidade(self.produto_sem_estoque, 2)

        # Verifica se a quantidade no carrinho permaneceu 1
        self.assertEqual(self.carrinho.itens[self.produto_sem_estoque], 1)

    def test_limpar_carrinho(self):
        """Verifica se o método limpar_carrinho esvazia o carrinho."""
        
        self.carrinho.adicionar_item(self.produto1, 1)
        self.carrinho.adicionar_item(self.produto2, 1)
        self.assertGreater(len(self.carrinho), 0)
        self.carrinho.limpar_carrinho()
        self.assertEqual(len(self.carrinho), 0)
        self.assertEqual(self.carrinho.itens, {})

#  executar os testes diretamente pelo script
if __name__ == '__main__':
    unittest.main()

