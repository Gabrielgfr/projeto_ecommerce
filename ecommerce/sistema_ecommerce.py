from typing import List, Dict, Optional, Any
from decimal import Decimal
import uuid
from .produto import Produto
from .carrinho import Carrinho
from .sistema_pagamento import SistemaPagamento
from .pedido import Pedido, StatusPedido

class SistemaEcommerce:
    def __init__(self, sistema_pagamento: Optional[SistemaPagamento] = None):
        self.produtos: Dict[int, Produto] = {} # cria o catálogo de produtos como um dicionário vazio
        self.pedidos: Dict[str, Pedido] = {}
        self.sistema_pagamento = sistema_pagamento if sistema_pagamento else SistemaPagamento() 
        print("Sistema de E-commerce inicializado.")

    # --- Gerenciamento de Produtos ---

    def adicionar_produto(self, produto: Produto): 
        if produto.id_produto in self.produtos: # Verifica se o produto já existe no catálogo
            raise ValueError(f"Produto com ID {produto.id_produto} já existe no catálogo.")
        self.produtos[produto.id_produto] = produto # Adiciona o produto ao dicionário de produtos
        print(f"Produto '{produto.nome}' (ID: {produto.id_produto}) adicionado ao catálogo.")

    def buscar_produto_por_id(self, id_produto: int) -> Optional[Produto]: 
        return self.produtos.get(id_produto)

    def listar_produtos(self) -> List[Produto]: 
        return list(self.produtos.values())

    def buscar_produtos_por_nome(self, termo_busca: str) -> List[Produto]:
        termo_busca_lower = termo_busca.lower() 
        return [p for p in self.produtos.values() if termo_busca_lower in p.nome.lower()] 

    # --- Gerenciamento de Pedidos ---

    def criar_pedido(self, id_cliente: str, carrinho: Carrinho, endereco_entrega: Dict[str, str], metodo_pagamento: str) -> Optional[Pedido]: # Cria um pedido a partir de um carrinho
        print(f"\n--- Iniciando criação de pedido para cliente {id_cliente} ---") 
        # 1. Validar estoque para todos os itens do carrinho ANTES de criar o pedido
        itens_carrinho = carrinho.obter_itens() 
        if not itens_carrinho:
            print("Erro: Carrinho está vazio. Não é possível criar pedido.")
            return None

        for produto, quantidade in itens_carrinho.items(): 
            produto_catalogo = self.buscar_produto_por_id(produto.id_produto) # Busca o produto no catálogo
            if not produto_catalogo: # Verifica se o produto existe no catálogo
                print(f"Erro: Produto '{produto.nome}' (ID: {produto.id_produto}) não encontrado no catálogo.")
                return None 
            if not produto_catalogo.verificar_disponibilidade(quantidade): # Verifica se o produto está disponível em estoque
                print(f"Erro: Estoque insuficiente para '{produto.nome}' (ID: {produto.id_produto}). Pedido: {quantidade}, Disponível: {produto_catalogo.quantidade_estoque}.")
                return None 

        # 2. Criar a instância do Pedido (se estoque OK)
        try:
            novo_pedido = Pedido(id_cliente, carrinho, endereco_entrega, metodo_pagamento)
        except ValueError as e: # Se houver erro na criação do pedido, dados inválidos
            print(f"Erro ao instanciar Pedido: {e}")
            return None

        # 3. Decrementar o estoque dos produtos
        try:
            for produto, quantidade in itens_carrinho.items():
                produto_catalogo = self.buscar_produto_por_id(produto.id_produto)
                if produto_catalogo:
                    produto_catalogo.atualizar_estoque(-quantidade) # Remove do estoque
                    print(f"Estoque do produto '{produto_catalogo.nome}' atualizado para {produto_catalogo.quantidade_estoque}.")
                else:
                     print(f"AVISO: Produto {produto.id_produto} não encontrado durante a baixa de estoque!")
        except ValueError as e: # Se houver erro ao atualizar o estoque, estoque negativo)
            print(f"Erro CRÍTICO ao atualizar estoque para o pedido {novo_pedido.id_pedido}: {e}") 
            return None

        # 4. Adicionar o pedido ao sistema e retornar
        self.pedidos[novo_pedido.id_pedido] = novo_pedido
        print(f"Pedido {novo_pedido.id_pedido} criado com sucesso e adicionado ao sistema.")
        # Limpar o carrinho após criar o pedido
        carrinho.limpar_carrinho()
        print("Carrinho esvaziado.")
        return novo_pedido

    def buscar_pedido_por_id(self, id_pedido: str) -> Optional[Pedido]: 
        return self.pedidos.get(id_pedido)

    def listar_pedidos_por_cliente(self, id_cliente: str) -> List[Pedido]: 
        return [p for p in self.pedidos.values() if p.id_cliente == id_cliente] # lista de pedidos que pertencem ao cliente especificado

    # --- Processamento de Pagamento --- 

    def processar_pagamento_pedido(self, id_pedido: str, dados_pagamento: Dict[str, Any]) -> bool: 
        pedido = self.buscar_pedido_por_id(id_pedido) 
        if not pedido: # Verifica se o pedido existe
            print(f"Erro: Pedido com ID {id_pedido} não encontrado.")
            return False

        # Verifica se o pedido está em um status que permite pagamento
        if pedido.status not in [StatusPedido.PENDENTE, StatusPedido.FALHA_PAGAMENTO]:
            print(f"Erro: Pedido {id_pedido} não está pendente de pagamento (Status: {pedido.status.name}).")

        print(f"\n--- Processando pagamento para o pedido {id_pedido} via {pedido.metodo_pagamento} ---")
        pedido.atualizar_status(StatusPedido.PROCESSANDO_PAGAMENTO)  
        sucesso = False
        mensagem = "Método de pagamento não suportado ou erro interno."
        id_transacao = None
        valor_pago_final = Decimal('0.0')
        num_parcelas_final = None
        valor_parcela_final = None

        try:
            # Processa o pagamento de acordo com o método escolhido
            if pedido.metodo_pagamento == "Cartão de Crédito":
                num_parcelas = dados_pagamento.get('num_parcelas', 1) 
                dados_cartao = dados_pagamento.get('dados_cartao', {}) 
                if not isinstance(num_parcelas, int) or num_parcelas < 1: #número de parcelas é válido
                     raise ValueError("Número de parcelas inválido.")

                sucesso, mensagem, valor_pago_final, valor_parcela_final = self.sistema_pagamento.processar_cartao_credito(
                    float(pedido.valor_total), #valor total calculado no pedido (itens+frete)
                    num_parcelas, 
                    dados_cartao
                )
                if sucesso:
                    num_parcelas_final = num_parcelas 
                    id_transacao = f"cc_{str(uuid.uuid4())[:8]}" #ID de transação de cartão de crédito

            elif pedido.metodo_pagamento == "PIX":
                sucesso, mensagem, valor_pago_final = self.sistema_pagamento.processar_pix(
                    float(pedido.valor_total) # valor total original para aplicar desconto
                )
                if sucesso:
                    id_transacao = f"pix_{str(uuid.uuid4())[:8]}"

            else:
                print(f"Erro: Método de pagamento '{pedido.metodo_pagamento}' não suportado.")
                pedido.atualizar_status(StatusPedido.FALHA_PAGAMENTO) 
                return False

            # Registra o resultado do pagamento no pedido
            print(f"Resultado do processamento: {mensagem}")
            pedido.registrar_pagamento(sucesso, id_transacao, valor_pago_final, num_parcelas_final, valor_parcela_final)

        except Exception as e: # Captura qualquer exceção inesperada durante o processamento
            print(f"Erro inesperado durante o processamento do pagamento para o pedido {id_pedido}: {e}")
            pedido.registrar_pagamento(False, None, Decimal('0.0'))
            sucesso = False

        return sucesso

    # --- Cancelamento e Reabastecimento ---

    def cancelar_pedido(self, id_pedido: str) -> bool: # Cancela um pedido existente
        pedido = self.buscar_pedido_por_id(id_pedido) 
        if not pedido:
            print(f"Erro: Pedido com ID {id_pedido} não encontrado para cancelamento.")
            return False

        print(f"\n--- Tentando cancelar pedido {id_pedido} (Status atual: {pedido.status.name}) ---") 

        # Verifica se o pedido está em um status que permite cancelamento
        if pedido.status not in [StatusPedido.PENDENTE, StatusPedido.PROCESSANDO_PAGAMENTO, StatusPedido.FALHA_PAGAMENTO, StatusPedido.PAGO, StatusPedido.EM_SEPARACAO]:
            print(f"Erro: Não é possível cancelar o pedido {id_pedido} no status {pedido.status.name}.")
            return False

        # Tenta atualizar o status para CANCELADO
        if pedido.atualizar_status(StatusPedido.CANCELADO):
            # Se o cancelamento foi bem-sucedido, reabastecer o estoque
            print(f"Pedido {id_pedido} cancelado. Reabastecendo estoque...")
            try:
                for produto_pedido, quantidade in pedido.itens.items():
                    produto_catalogo = self.buscar_produto_por_id(produto_pedido.id_produto)
                    if produto_catalogo:
                        produto_catalogo.atualizar_estoque(quantidade) # Adiciona de volta ao estoque
                        print(f"Estoque do produto '{produto_catalogo.nome}' reabastecido para {produto_catalogo.quantidade_estoque}.")
                    else:
                        print(f"AVISO: Produto {produto_pedido.id_produto} do pedido cancelado não encontrado no catálogo para reabastecimento!")
                if pedido.data_pagamento and pedido.id_transacao_pagamento: 
                    print(f"Atenção: Pedido {id_pedido} estava pago. É necessário processar o reembolso para a transação {pedido.id_transacao_pagamento}.") 
                return True
            except ValueError as e:
                print(f"Erro CRÍTICO ao reabastecer estoque para o pedido cancelado {id_pedido}: {e}")
                return False 
        else:
            print(f"Falha ao atualizar status para CANCELADO para o pedido {id_pedido}.")
            return False

    # --- Outras Funcionalidades  ---

    def gerar_relatorio_vendas(self) -> str: 
        relatorio = "--- Relatório de Vendas ---\n"
        total_vendido = Decimal('0.0') 
        pedidos_pagos = 0 # Contador de pedidos pagos ou concluídos
        for pedido in self.pedidos.values(): 
            if pedido.status == StatusPedido.PAGO or pedido.status == StatusPedido.EM_SEPARACAO or pedido.status == StatusPedido.ENVIADO or pedido.status == StatusPedido.ENTREGUE:
                relatorio += f"- Pedido: {pedido.id_pedido}, Cliente: {pedido.id_cliente}, Valor: R$ {pedido.valor_total:.2f}, Status: {pedido.status.name}\n"
                total_vendido += pedido.valor_total # Adiciona o valor total do pedido ao total vendido
                pedidos_pagos += 1

        relatorio += f"\nTotal de Pedidos Pagos/Concluídos: {pedidos_pagos}\n"
        relatorio += f"Valor Total Vendido: R$ {total_vendido:.2f}\n"
        relatorio += "--------------------------\n"
        return relatorio 

if __name__ == '__main__':
    # 1. Inicializa o sistema
    sistema = SistemaEcommerce()

    # 2. Adiciona produtos ao catálogo
    try:
        p1 = Produto(1, "Teclado Mecânico RGB", "Teclado gamer com switches blue", 350.00, 20, "Periféricos")
        p2 = Produto(2, "Monitor Ultrawide 34\"", "Monitor curvo para produtividade e jogos", 2800.00, 5, "Monitores")
        p3 = Produto(3, "SSD NVMe 1TB", "Armazenamento rápido", 600.00, 30, "Componentes")
        sistema.adicionar_produto(p1)
        sistema.adicionar_produto(p2)
        sistema.adicionar_produto(p3)
    except ValueError as e:
        print(f"Erro ao adicionar produto: {e}")

    # 3. Simula um cliente adicionando itens ao carrinho
    carrinho_cliente1 = Carrinho()
    produto_escolhido1 = sistema.buscar_produto_por_id(1) 
    produto_escolhido2 = sistema.buscar_produto_por_id(3)

    if produto_escolhido1 and produto_escolhido2: # Verifica se os produtos existem
        try: # Adiciona os produtos ao carrinho
            carrinho_cliente1.adicionar_item(produto_escolhido1, 1)
            carrinho_cliente1.adicionar_item(produto_escolhido2, 2)
            print("\n--- Carrinho Cliente 1 ---")
            print(carrinho_cliente1)
        except ValueError as e:
            print(f"Erro ao adicionar ao carrinho: {e}")

        # 4. Cliente finaliza a compra - Cria o pedido
        endereco_cliente1 = {"rua": "Av. Principal", "numero": "1000", "cidade": "Metropolis", "cep": "99888-777"}
        pedido1 = sistema.criar_pedido("cliente123", carrinho_cliente1, endereco_cliente1, "Cartão de Crédito")

        if pedido1:
            print(f"\nPedido {pedido1.id_pedido} criado. Status: {pedido1.status.name}")

            # 5. Processa o pagamento do pedido
            dados_pgto_cc = {'num_parcelas': 3, 'dados_cartao': {'numero': '**** **** **** 1111'}} 
            pagamento_ok = sistema.processar_pagamento_pedido(pedido1.id_pedido, dados_pgto_cc)

            if pagamento_ok:
                print(f"Pagamento do pedido {pedido1.id_pedido} realizado com sucesso.")
                pedido1.atualizar_status(StatusPedido.EM_SEPARACAO) 
                pedido1.atualizar_status(StatusPedido.ENVIADO)
                pedido1.atualizar_status(StatusPedido.ENTREGUE)
            else:
                print(f"Falha no pagamento do pedido {pedido1.id_pedido}.")

    # 6. Simula cliente comprando com PIX e cancelando
    carrinho_cliente2 = Carrinho()
    produto_escolhido3 = sistema.buscar_produto_por_id(2)
    if produto_escolhido3:
        try:
            carrinho_cliente2.adicionar_item(produto_escolhido3, 1)
            print("\n--- Carrinho Cliente 2 ---")
            print(carrinho_cliente2)
        except ValueError as e:
            print(f"Erro ao adicionar ao carrinho: {e}")

        endereco_cliente2 = {"rua": "Rua Secundaria", "numero": "50", "cidade": "Gotham", "cep": "11222-333"}
        pedido2 = sistema.criar_pedido("cliente456", carrinho_cliente2, endereco_cliente2, "PIX")

        if pedido2:
            print(f"\nPedido {pedido2.id_pedido} criado. Status: {pedido2.status.name}")
            # Cliente decide cancelar antes de pagar
            cancelamento_ok = sistema.cancelar_pedido(pedido2.id_pedido)
            if cancelamento_ok:
                print(f"Pedido {pedido2.id_pedido} cancelado com sucesso.")
            else:
                print(f"Falha ao cancelar o pedido {pedido2.id_pedido}.")

    # 7. Gera um relatório de vendas
    print("\n--- Gerando Relatório de Vendas ---")
    relatorio = sistema.gerar_relatorio_vendas()
    print(relatorio)

    # 8. Verifica estoque após as operações
    print("\n--- Estoque Atualizado ---")
    for prod_id, prod in sistema.produtos.items():
        print(f"- {prod.nome}: {prod.quantidade_estoque} unidades")

