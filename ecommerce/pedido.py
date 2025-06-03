import uuid
from datetime import datetime
from enum import Enum, auto
from typing import Dict, Any
from decimal import Decimal
from .produto import Produto
from .carrinho import Carrinho # Usado para obter itens ao criar o pedido

class StatusPedido(Enum):
    """Enumeração para os possíveis status de um pedido."""
    PENDENTE = auto()       # Pedido criado, aguardando pagamento
    PROCESSANDO_PAGAMENTO = auto() # Pagamento em andamento
    PAGO = auto()           # Pagamento confirmado
    EM_SEPARACAO = auto()   # Produtos sendo separados no estoque
    ENVIADO = auto()        # Pedido despachado para entrega
    ENTREGUE = auto()       # Pedido recebido pelo cliente
    CANCELADO = auto()      # Pedido cancelado
    FALHA_PAGAMENTO = auto() # Pagamento falhou


class Pedido: 

    # Define as transições de status permitidas
    TRANSICOES_PERMITIDAS = {
        StatusPedido.PENDENTE: [StatusPedido.PROCESSANDO_PAGAMENTO, StatusPedido.CANCELADO],
        StatusPedido.PROCESSANDO_PAGAMENTO: [StatusPedido.PAGO, StatusPedido.FALHA_PAGAMENTO, StatusPedido.CANCELADO],
        StatusPedido.FALHA_PAGAMENTO: [StatusPedido.PROCESSANDO_PAGAMENTO, StatusPedido.CANCELADO], # Permitir tentar pagar novamente
        StatusPedido.PAGO: [StatusPedido.EM_SEPARACAO, StatusPedido.CANCELADO], # Cancelamento pós-pagamento pode exigir reembolso
        StatusPedido.EM_SEPARACAO: [StatusPedido.ENVIADO, StatusPedido.CANCELADO],
        StatusPedido.ENVIADO: [StatusPedido.ENTREGUE, StatusPedido.CANCELADO], # Cancelar após envio é complexo (devolução)
        StatusPedido.ENTREGUE: [], # Estado final (exceto devoluções, não modeladas aqui)
        StatusPedido.CANCELADO: []  # Estado final
    }

    # Inicializa um novo pedido com os detalhes fornecidos.
    def __init__(self, id_cliente: str, carrinho: Carrinho, endereco_entrega: Dict[str, str], metodo_pagamento: str):
        # Verifica se o carrinho não está vazio
        # Se o carrinho estiver vazio, não é possível criar um pedido 
        if not carrinho.obter_itens():
            raise ValueError("Não é possível criar um pedido com um carrinho vazio.")

        # Atributos básicos do pedido
        self.id_pedido = str(uuid.uuid4()) # Gera um ID único para o pedido
        self.id_cliente = id_cliente 

        # Copia os itens do carrinho para o pedido para evitar modificações externas
        self.itens = dict(carrinho.obter_itens())
        self.endereco_entrega = endereco_entrega # Armazena o endereço de entrega
        self.metodo_pagamento = metodo_pagamento 

        # Cálculos iniciais (frete e total)
        self.valor_frete = self.calcular_frete() # Calcula o frete
        self.valor_total = Decimal(str(carrinho.calcular_total())) + self.valor_frete # Total = itens + frete

        # Status inicial e datas
        self.status = StatusPedido.PENDENTE # Status inicial do pedido
        self.data_criacao = datetime.now() 
        self.data_pagamento = None # Data de pagamento (preenchida após processamento)
        self.data_envio = None
        self.data_entrega = None

        # Informações de pagamento (preenchidas após processamento)
        self.id_transacao_pagamento = None 
        self.num_parcelas = None
        self.valor_parcela = None

        print(f"Pedido {self.id_pedido} criado para o cliente {self.id_cliente}. Status: {self.status.name}")

    def atualizar_status(self, novo_status: StatusPedido) -> bool: # Atualiza o status do pedido
        if novo_status in self.TRANSICOES_PERMITIDAS.get(self.status, []): # Verifica se a transição é permitida
            status_anterior = self.status # Armazena o status anterior
            self.status = novo_status # Atualiza o status do pedido
            print(f"Status do pedido {self.id_pedido} atualizado de {status_anterior.name} para {self.status.name}.") 

            # Atualiza datas relevantes com base no novo status
            now = datetime.now()
            if novo_status == StatusPedido.PAGO and not self.data_pagamento:
                self.data_pagamento = now
            elif novo_status == StatusPedido.ENVIADO and not self.data_envio:
                self.data_envio = now
            elif novo_status == StatusPedido.ENTREGUE and not self.data_entrega:
                self.data_entrega = now
            # Adicionar lógica para CANCELADO se necessário (ex: log, reembolso)
            elif novo_status == StatusPedido.CANCELADO:
                print(f"Pedido {self.id_pedido} foi cancelado.")
        
            return True
        else:
            print(f"Erro: Transição de status inválida de {self.status.name} para {novo_status.name} no pedido {self.id_pedido}.")
            return False # Retorna False se a transição não for permitida
        
    # Registra o resultado do processamento do pagamento
    def registrar_pagamento(self, sucesso: bool, id_transacao: str | None, valor_pago: Decimal, num_parcelas: int | None = None, valor_parcela: Decimal | None = None):

        if self.status not in [StatusPedido.PENDENTE, StatusPedido.PROCESSANDO_PAGAMENTO, StatusPedido.FALHA_PAGAMENTO]: # Verifica se o status permite registrar pagamento
            print(f"Aviso: Tentativa de registrar pagamento para pedido {self.id_pedido} com status {self.status.name}.") # verifica se o status é válido
            
        if sucesso: # Se o pagamento foi bem-sucedido qtualiza os detalhes do pagamento
            self.id_transacao_pagamento = id_transacao
            self.valor_total = valor_pago # Atualiza o valor total com o valor efetivamente pago
            self.num_parcelas = num_parcelas
            self.valor_parcela = valor_parcela
            self.atualizar_status(StatusPedido.PAGO)
        else: # Se o pagamento falhou, atualiza o status
            self.atualizar_status(StatusPedido.FALHA_PAGAMENTO)
            print(f"Falha ao registrar pagamento para o pedido {self.id_pedido}. ID da tentativa: {id_transacao}")

    def calcular_frete(self) -> Decimal: # Calcula o valor do frete com base no número de itens
        num_itens_total = sum(self.itens.values()) # Soma as quantidades de todos os itens
        if num_itens_total == 0: # Se não houver itens, o frete é zero
             return Decimal("0.00")
        
        frete = Decimal(str(num_itens_total)) * Decimal("5.00") 
        frete_maximo = Decimal("50.00") 
        valor_frete_calculado = min(frete, frete_maximo)

        print(f"Frete calculado para pedido {self.id_pedido}: R$ {valor_frete_calculado:.2f}")
        return valor_frete_calculado.quantize(Decimal("0.01"))

    def gerar_nota_fiscal(self) -> str: # Gera uma nota fiscal para o pedido
        if self.status not in [StatusPedido.PAGO, StatusPedido.EM_SEPARACAO, StatusPedido.ENVIADO, StatusPedido.ENTREGUE]: # Verifica se o status permite gerar nota fiscal
            raise ValueError(f"Não é possível gerar nota fiscal para o pedido {self.id_pedido} com status {self.status.name}.") # verifica se o status é válido

        # Formatação da nota fiscal
        nf = f"--- Nota Fiscal ---\n"
        nf += f"Pedido ID: {self.id_pedido}\n"
        nf += f"Cliente ID: {self.id_cliente}\n"
        nf += f"Data Emissão: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        nf += f"Endereço Entrega: {self.endereco_entrega}\n"
        nf += f"\n--- Itens ---\n"
        subtotal_itens = Decimal("0.00")
        for produto, quantidade in self.itens.items():
            valor_item_total = Decimal(str(produto.preco)) * Decimal(quantidade)
            nf += f"- {produto.nome} ({quantidade}x R$ {produto.preco:.2f}) = R$ {valor_item_total:.2f}\n"
            subtotal_itens += valor_item_total

        nf += f"\nSubtotal Itens: R$ {subtotal_itens:.2f}\n"
        nf += f"Frete: R$ {self.valor_frete:.2f}\n"
        # O valor total já considera descontos/juros do pagamento
        nf += f"Valor Total Pago: R$ {self.valor_total:.2f}\n"
        nf += f"Método Pagamento: {self.metodo_pagamento}\n"
        if self.num_parcelas and self.num_parcelas > 1 and self.valor_parcela:
             nf += f"Pagamento: {self.num_parcelas}x de R$ {self.valor_parcela:.2f}\n"
        if self.id_transacao_pagamento:
            nf += f"ID Transação: {self.id_transacao_pagamento}\n"
        nf += f"------------------\n"

        print(f"Nota fiscal gerada para o pedido {self.id_pedido}.")
        return nf

    def obter_detalhes(self) -> Dict[str, Any]:
        #Retorna um dicionário com os detalhes completos do pedido.
        return {
            "id_pedido": self.id_pedido,
            "id_cliente": self.id_cliente,
            "itens": {p.nome: q for p, q in self.itens.items()}, # Simplifica itens para exibição
            "endereco_entrega": self.endereco_entrega,
            "metodo_pagamento": self.metodo_pagamento,
            "valor_total": float(self.valor_total), # Converte Decimal para float para JSON/API
            "valor_frete": float(self.valor_frete),
            "status": self.status.name,
            "data_criacao": self.data_criacao.isoformat(),
            "data_pagamento": self.data_pagamento.isoformat() if self.data_pagamento else None,
            "data_envio": self.data_envio.isoformat() if self.data_envio else None,
            "data_entrega": self.data_entrega.isoformat() if self.data_entrega else None,
            "id_transacao_pagamento": self.id_transacao_pagamento,
            "num_parcelas": self.num_parcelas,
            "valor_parcela": float(self.valor_parcela) if self.valor_parcela else None
        }

    def __str__(self) -> str: # Retorna uma string formatada com os detalhes do pedido.
        return f"Pedido(ID: {self.id_pedido}, Status: {self.status.name}, Total: R$ {self.valor_total:.2f})" # Formata a string de exibição do pedido

    def __repr__(self) -> str: # Retorna uma representação mais detalhada do pedido.
        return f"<Pedido {self.id_pedido} - Status: {self.status.name}>"

# Exemplo 
if __name__ == '__main__':
    # Cria produtos de exemplo
    prod1 = Produto(1, "Laptop Gamer", "Notebook com RTX 4090", 15000.00, 10, "Eletrônicos")
    prod2 = Produto(2, "Mouse Sem Fio", "Mouse ergonômico", 150.00, 50, "Acessórios")

    # Cria um carrinho e adiciona itens
    carrinho_exemplo = Carrinho()
    try:
        carrinho_exemplo.adicionar_item(prod1, 1)
        carrinho_exemplo.adicionar_item(prod2, 2)
    except ValueError as e:
        print(f"Erro ao adicionar item: {e}")

    print("\n--- Carrinho --- ")
    print(carrinho_exemplo)

    # Define endereço e cliente
    endereco = {"rua": "Rua Exemplo", "numero": "123", "cidade": "Cidade Teste", "cep": "12345-678"}
    cliente_id = "cliente_abc"

    # Cria um pedido
    print("\n--- Criando Pedido --- ")
    try:
        pedido_exemplo = Pedido(cliente_id, carrinho_exemplo, endereco, "Cartão de Crédito")
        print(pedido_exemplo)
        print(f"Valor inicial do pedido (itens + frete): R$ {pedido_exemplo.valor_total:.2f}")

        # Simula registro de pagamento (sucesso)
        print("\n--- Registrando Pagamento (Sucesso) --- ")
        pedido_exemplo.registrar_pagamento(True, "transacao_12345", Decimal("15310.00"), 3, Decimal("5103.33")) # Valor pode incluir juros
        print(pedido_exemplo)

        # Tenta atualizar status
        print("\n--- Atualizando Status --- ")
        pedido_exemplo.atualizar_status(StatusPedido.EM_SEPARACAO)
        pedido_exemplo.atualizar_status(StatusPedido.ENVIADO)
        pedido_exemplo.atualizar_status(StatusPedido.ENTREGUE)
        print(pedido_exemplo)

        #Gerar nota fiscal
        print("\n--- Gerando Nota Fiscal --- ")
        try:
            nota = pedido_exemplo.gerar_nota_fiscal()
            print(nota) 
        except ValueError as e:
            print(f"Erro ao gerar nota: {e}")

        # Tenta uma transição inválida
        print("\n--- Tentando Transição Inválida --- ")
        pedido_exemplo.atualizar_status(StatusPedido.PENDENTE) # Inválido a partir de ENTREGUE

        # Obtém detalhes
        print("\n--- Detalhes do Pedido --- ")
        detalhes = pedido_exemplo.obter_detalhes()
        import json
        print(json.dumps(detalhes, indent=2))

    except ValueError as e:
        print(f"Erro ao criar pedido: {e}")

    # Exemplo de pedido cancelado
    print("\n--- Criando Pedido para Cancelar --- ")
    carrinho_cancel = Carrinho()
    try:
        carrinho_cancel.adicionar_item(prod2, 1)
        pedido_cancel = Pedido("cliente_xyz", carrinho_cancel, endereco, "PIX")
        print(pedido_cancel)
        pedido_cancel.atualizar_status(StatusPedido.CANCELADO)
        print(pedido_cancel)
    except ValueError as e:
        print(f"Erro: {e}")

