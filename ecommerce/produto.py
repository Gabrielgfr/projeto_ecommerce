class Produto:   
    def __init__(self, id_produto: int, nome: str, descricao: str, preco: float, quantidade_estoque: int, categoria: str): # Construtor da classe Produto
        if preco <= 0:
            raise ValueError("O preço do produto deve ser positivo.")
        if quantidade_estoque < 0:
            raise ValueError("A quantidade em estoque não pode ser negativa.")

        # Atribuição dos atributos da instância
        self.id_produto = id_produto 
        self.nome = nome
        self.descricao = descricao
        self.preco = preco
        self.quantidade_estoque = quantidade_estoque
        self.categoria = categoria

    def verificar_disponibilidade(self, quantidade_desejada: int = 1) -> bool: # Verifica se o produto está disponível em estoque       
        if quantidade_desejada <= 0:
            raise ValueError("A quantidade desejada deve ser positiva.")
        # Retorna True se a quantidade em estoque for maior ou igual à desejada
        return self.quantidade_estoque >= quantidade_desejada

    def atualizar_estoque(self, quantidade: int): # Atualiza a quantidade em estoque
        nova_quantidade = self.quantidade_estoque + quantidade # Verifica se a nova quantidade é válida
        if nova_quantidade < 0:
            raise ValueError("A atualização resultaria em estoque negativo.")
        # Atualiza a quantidade em estoque
        self.quantidade_estoque = nova_quantidade

    def obter_informacoes(self) -> dict: # Retorna as informações do produto em um dicionário
        return {
            "id_produto": self.id_produto,
            "nome": self.nome,
            "descricao": self.descricao,
            "preco": self.preco,
            "quantidade_estoque": self.quantidade_estoque,
            "categoria": self.categoria
        }

    def __str__(self) -> str: # Retorna uma representação amigável do objeto Produto.
        return f"{self.nome} - R$ {self.preco:.2f}"

    def __repr__(self) -> str: # Retorna uma representação detalhada do objeto Produto.
        return (f"Produto(id_produto={self.id_produto}, nome='{self.nome}', "
                f"descricao='{self.descricao}', preco={self.preco}, "
                f"quantidade_estoque={self.quantidade_estoque}, categoria='{self.categoria}')")

