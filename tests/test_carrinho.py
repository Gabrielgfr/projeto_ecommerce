import unittest
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from ecommerce.produto import Produto
from ecommerce.carrinho import Carrinho

class TestCarrinho(unittest.TestCase):
    

    def setUp(self):
        # Cria produtos com estoque suficiente para a maioria dos testes
        self.produto1 = Produto(id_produto=101, nome="Produto A", descricao="Desc A", preco=50.0, quantidade_estoque=10, categoria="Cat A")
        self.produto2 = Produto(id_produto=102, nome="Produto B", descricao="Desc B", preco=25.5, quantidade_estoque=5, categoria="Cat B")
        
        # Cria um produto com estoque baixo para testes específicos
        self.produto_sem_estoque = Produto(id_produto=103, nome="Produto C", descricao="Desc C", preco=100.0, quantidade_estoque=1, categoria="Cat C")
        
        #carrinho vazio
        self.carrinho = Carrinho()

    def test_adicao_item_novo(self):
        #Questão 2: Adição de itens no carrinho 
         
        self.carrinho.adicionar_item(self.produto1, 2)
        self.assertEqual(len(self.carrinho), 1) # se há 1 tipo de produto
        self.assertIn(self.produto1, self.carrinho.itens) #  o produto está no carrinho
        self.assertEqual(self.carrinho.itens[self.produto1], 2) # quantidade

    def test_adicao_item_existente(self):
        #Questão 2: Adição de itens no carrinho
         
        self.carrinho.adicionar_item(self.produto1, 1) # Adiciona 1 unidade
        self.carrinho.adicionar_item(self.produto1, 3) 
        self.assertEqual(len(self.carrinho), 1)
        self.assertEqual(self.carrinho.itens[self.produto1], 4) #total (1+3)

    def test_adicao_multiplos_itens(self): 
        #Questão 2: Adição de itens no carrinho
        
        self.carrinho.adicionar_item(self.produto1, 1)
        self.carrinho.adicionar_item(self.produto2, 3)
        self.assertEqual(len(self.carrinho), 2) # se há 2 tipos de produtos
        self.assertEqual(self.carrinho.itens[self.produto1], 1)
        self.assertEqual(self.carrinho.itens[self.produto2], 3)

    def test_remocao_item_parcial(self):
         #Questão 2: Remoção de itens do carrinho
        
        self.carrinho.adicionar_item(self.produto1, 5)
        self.carrinho.remover_item(self.produto1, 2) # Remove 2 unidades
        self.assertEqual(len(self.carrinho), 1)
        self.assertEqual(self.carrinho.itens[self.produto1], 3) # Verifica a quantidade restante (5-2)

    def test_remocao_item_total(self):
        #Questão 2: Remoção de itens do carrinho
        
        self.carrinho.adicionar_item(self.produto1, 3)
        self.carrinho.adicionar_item(self.produto2, 1)
        self.carrinho.remover_item(self.produto1, 3) # Remove todas as unidades do produto1
        self.assertEqual(len(self.carrinho), 1) # Apenas produto2 deve permanecer
        self.assertNotIn(self.produto1, self.carrinho.itens)
        self.assertIn(self.produto2, self.carrinho.itens)

        # remover mais do que existe 
        self.carrinho.adicionar_item(self.produto1, 2)
        self.carrinho.remover_item(self.produto1, 5)
        self.assertNotIn(self.produto1, self.carrinho.itens)

    def test_remocao_item_inexistente(self):
        #Questão 2: Remoção de itens do carrinho caso dom erro
        
        with self.assertRaisesRegex(ValueError, "Produto Produto A não encontrado no carrinho."):
            self.carrinho.remover_item(self.produto1, 1)

    def test_calculo_total_carrinho_vazio(self):
        #Questão 2: Cálculo do valor total do carrinho
        
        self.assertEqual(self.carrinho.calcular_total(), 0.0)

    def test_calculo_total_um_item(self):
        #Questão 2: Cálculo do valor total do carrinho
        
        self.carrinho.adicionar_item(self.produto1, 3) # 3 * 50.0 = 150.0
        self.assertAlmostEqual(self.carrinho.calcular_total(), 150.0)

    def test_calculo_total_multiplos_itens(self):
        self.carrinho.adicionar_item(self.produto1, 2) # 2 * 50.0 = 100.0
        self.carrinho.adicionar_item(self.produto2, 4) # 4 * 25.5 = 102.0
        self.assertAlmostEqual(self.carrinho.calcular_total(), 202.0) 

    def test_adicao_item_sem_estoque_suficiente(self):
        #Questão 2: Comportamento quando tenta adicionar um produto sem estoque suficiente
        
        # Tenta adicionar mais do que o estoque inicial, produto_sem_estoque tem 1
        with self.assertRaisesRegex(ValueError, r"Estoque insuficiente para adicionar 2 unidade\(s\) de Produto C."):
            self.carrinho.adicionar_item(self.produto_sem_estoque, 2)

        #carrinho não foi modificado
        self.assertNotIn(self.produto_sem_estoque, self.carrinho.itens)
        self.assertEqual(len(self.carrinho), 0)

    def test_adicao_item_existente_sem_estoque_suficiente(self):
           #Questão 2: Comportamento quando tenta adicionar um produto sem estoque suficiente
        
        # Adiciona 1 unidade 
        self.carrinho.adicionar_item(self.produto_sem_estoque, 1)
        self.assertEqual(self.carrinho.itens[self.produto_sem_estoque], 1)

        # adicionar mais 1 unidade 
        with self.assertRaisesRegex(ValueError, r"Estoque insuficiente para adicionar mais 1 unidade\(s\) de Produto C. Total desejado: 2, Estoque: 1"):
            self.carrinho.adicionar_item(self.produto_sem_estoque, 1)

        #a quantidade no carrinho permaneceu 1
        self.assertEqual(self.carrinho.itens[self.produto_sem_estoque], 1)

    def test_atualizar_quantidade_sem_estoque_suficiente(self):
            #Questão 2: Comportamento quando tenta adicionar um produto sem estoque suficiente, via atualização
        
        self.carrinho.adicionar_item(self.produto_sem_estoque, 1)
        # Tenta atualizar para 2 
        with self.assertRaisesRegex(ValueError, r"Estoque insuficiente para atualizar para 2 unidade\(s\) de Produto C."):
            self.carrinho.atualizar_quantidade(self.produto_sem_estoque, 2)
        self.assertEqual(self.carrinho.itens[self.produto_sem_estoque], 1)

    def test_limpar_carrinho(self):
        #esvazia o carrinho
        
        self.carrinho.adicionar_item(self.produto1, 1)
        self.carrinho.adicionar_item(self.produto2, 1)
        self.assertGreater(len(self.carrinho), 0)
        self.carrinho.limpar_carrinho()
        self.assertEqual(len(self.carrinho), 0)
        self.assertEqual(self.carrinho.itens, {})

if __name__ == '__main__':
    unittest.main()

