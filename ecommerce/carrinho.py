from .produto import Produto  # Importa a classe Produto
from typing import Dict, Tuple

class Carrinho:
   
    def __init__(self):
        self.itens: Dict[Produto, int] = {} #inicializa o carrinho como um dicionário vazio, onde a chave é o produto e o valor é a quantidade

    def adicionar_item(self, produto: Produto, quantidade: int = 1):     

        
        if quantidade <= 0: #Verifica se há estoque suficiente antes de adicionar.
            raise ValueError("A quantidade a ser adicionada deve ser positiva.")        
        if not produto.verificar_disponibilidade(quantidade): # Verifica a disponibilidade do produto no estoque
            raise ValueError(f"Estoque insuficiente para adicionar {quantidade} unidade(s) de {produto.nome}.")

        # Adiciona ou atualiza a quantidade do produto no carrinho
        if produto in self.itens:
            # Verifica se a quantidade total (existente + nova) excede o estoque
            quantidade_total_desejada = self.itens[produto] + quantidade
            if not produto.verificar_disponibilidade(quantidade_total_desejada):
                 raise ValueError(f"Estoque insuficiente para adicionar mais {quantidade} unidade(s) de {produto.nome}. Total desejado: {quantidade_total_desejada}, Estoque: {produto.quantidade_estoque}")
            self.itens[produto] += quantidade
        else:
            self.itens[produto] = quantidade

    def remover_item(self, produto: Produto, quantidade: int = 1):
        if quantidade <= 0: # Verifica se a quantidade a ser removida é positiva
            raise ValueError("A quantidade a ser removida deve ser positiva.")

        # Verifica se o produto está no carrinho
        if produto not in self.itens:
            raise ValueError(f"Produto {produto.nome} não encontrado no carrinho.")

        # Remove a quantidade especificada ou o item inteiro
        if self.itens[produto] > quantidade:
            self.itens[produto] -= quantidade
        else:
            # Se a quantidade a remover for maior ou igual, remove o produto
            del self.itens[produto]

    def atualizar_quantidade(self, produto: Produto, nova_quantidade: int):
        # Verifica se a nova quantidade é válida
        if nova_quantidade < 0:
            raise ValueError("A nova quantidade não pode ser negativa.")

        if produto not in self.itens: # Verifica se o produto está no carrinho
            raise ValueError(f"Produto {produto.nome} não encontrado no carrinho para atualização.")

        if nova_quantidade == 0:
            # Remove o produto se a nova quantidade for zero
            del self.itens[produto]
        else:
            # Verifica a disponibilidade no estoque para a nova quantidade
            if not produto.verificar_disponibilidade(nova_quantidade):
                raise ValueError(f"Estoque insuficiente para atualizar para {nova_quantidade} unidade(s) de {produto.nome}.")
            # Atualiza a quantidade do produto no carrinho
            self.itens[produto] = nova_quantidade

    def calcular_total(self) -> float:
        #Calcula o valor total dos itens no carrinho.
        total = 0.0
        
        # Itera sobre os itens (produto, quantidade) no carrinho
        for produto, quantidade in self.itens.items():
            total += produto.preco * quantidade
        return total

    def aplicar_desconto(self, percentual_desconto: float) -> float:
        if not 0 <= percentual_desconto <= 100: # Verifica se o percentual de desconto é válido
            raise ValueError("O percentual de desconto deve estar entre 0 e 100.")

        # Calcula o valor total atual
        total_sem_desconto = self.calcular_total()
        # Calcula o valor do desconto
        valor_desconto = total_sem_desconto * (percentual_desconto / 100)
        # Retorna o valor final com desconto
        return total_sem_desconto - valor_desconto

    def limpar_carrinho(self): # Esvazia o carrinho
        self.itens = {} # Inicializa o carrinho como um dicionário vazio

    def obter_itens(self) -> Dict[Produto, int]:# Retorna o dicionário de itens do carrinho
        return self.itens

    def __len__(self) -> int: # Retorna o número de itens no carrinho
        return len(self.itens)

    def __str__(self) -> str:
        # Verifica se o carrinho está vazio
         # Se o carrinho estiver vazio, retorna uma mensagem apropriada
         # Caso contrário, retorna uma string formatada com os itens e seus preços e quantidades     
        if not self.itens:
            return "Carrinho vazio."

        # Cria uma string formatada com os itens do carrinho
        # Itera sobre os itens (produto, quantidade) no carrinho
        # Formata cada item como "Produto: quantidade x preço"
        # Junta todos os itens em uma string separada por quebras de linha
        itens_str = "\n".join([f"- {produto.nome}: {quantidade} x R$ {produto.preco:.2f}" for produto, quantidade in self.itens.items()])
        total_str = f"Total: R$ {self.calcular_total():.2f}"
        return f"Itens no Carrinho:\n{itens_str}\n{total_str}"

