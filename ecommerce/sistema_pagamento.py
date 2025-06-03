import random
import uuid
from decimal import Decimal, ROUND_HALF_UP

class SistemaPagamento: 
    def __init__(self, taxa_juros_parcelamento: float = 2.0, percentual_desconto_pix: float = 5.0):
        # Validação das taxas
        if not 0 <= taxa_juros_parcelamento <= 100: 
            raise ValueError("A taxa de juros deve estar entre 0 e 100.")
        if not 0 <= percentual_desconto_pix <= 100:
            raise ValueError("O percentual de desconto PIX deve estar entre 0 e 100.")

        # Define as taxas como Decimal
        self.taxa_juros_parcelamento = Decimal(str(taxa_juros_parcelamento)) / Decimal('100.0')  
        self.percentual_desconto_pix = Decimal(str(percentual_desconto_pix)) / Decimal('100.0')

    def _autorizar_pagamento(self, valor: Decimal, metodo: str) -> bool:
        print(f"Tentando autorizar pagamento de R$ {valor:.2f} via {metodo}...")
        autorizado = random.random() < 0.9 # 90% de chance de sucesso
        if autorizado: 
            print("Pagamento autorizado.")
        else:
            print("Falha na autorização do pagamento.")
        return autorizado

    def _verificar_fraude(self, dados_pagamento: dict) -> bool: 
        print("Verificando possível fraude...")
        # chance baixa (5%) de detectar fraude
        suspeita_fraude = random.random() < 0.05
        if suspeita_fraude:
            print("Alerta: Suspeita de fraude detectada!")
            return False
        else:
            print("Nenhuma suspeita de fraude.")
            return True

    def calcular_valor_parcela(self, valor_total: Decimal, num_parcelas: int) -> Decimal: # com base no valor total e no número de parcelas.
        if num_parcelas <= 0: 
            raise ValueError("O número de parcelas deve ser positivo.")

        valor_total_decimal = Decimal(str(valor_total)) 

        if num_parcelas == 1:
            # Pagamento à vista, sem juros
            return valor_total_decimal.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

        if self.taxa_juros_parcelamento == 0:
            # Parcelamento sem juros
            valor_parcela = valor_total_decimal / Decimal(num_parcelas)
        else:
            # juros compostos 
            # M = C * (1 + i)^n * i / ((1 + i)^n - 1)
            taxa = self.taxa_juros_parcelamento
            n = Decimal(num_parcelas)
            fator = (Decimal('1.0') + taxa) ** n
            if fator == Decimal('1.0'): # Evita divisão por zero se taxa for 0 e n > 1 
                 valor_parcela = valor_total_decimal / n
            else:
                valor_parcela = valor_total_decimal * fator * taxa / (fator - Decimal('1.0'))

        # Arredonda para 2 casas decimais
        return valor_parcela.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

    def processar_cartao_credito(self, valor_total: float, num_parcelas: int, dados_cartao: dict) -> tuple[bool, str, Decimal, Decimal | None]:
        valor_total_decimal = Decimal(str(valor_total)) 
        if num_parcelas < 1:
            return False, "Número de parcelas inválido.", Decimal('0.0'), None

        # Calcula o valor da parcela e o valor total com juros se houver
        valor_parcela = self.calcular_valor_parcela(valor_total_decimal, num_parcelas)
        valor_total_pagar = (valor_parcela * Decimal(num_parcelas)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

        #  verificação de fraude
        if not self._verificar_fraude({"valor": valor_total_pagar, "metodo": "Cartão de Crédito"}):
            return False, "Pagamento bloqueado por suspeita de fraude.", Decimal('0.0'), None

        #  autorização do pagamento
        if self._autorizar_pagamento(valor_total_pagar, "Cartão de Crédito"):
            comprovante = self._gerar_comprovante(valor_total_pagar, "Cartão de Crédito", num_parcelas, valor_parcela)
            print(f"Comprovante gerado: {comprovante}")
            valor_parcela_retorno = valor_parcela if num_parcelas > 1 else None
            return True, "Pagamento com cartão de crédito aprovado.", valor_total_pagar, valor_parcela_retorno
        else:
            return False, "Pagamento com cartão de crédito recusado.", Decimal('0.0'), None

    def processar_pix(self, valor_total: float) -> tuple[bool, str, Decimal]:
        valor_total_decimal = Decimal(str(valor_total)) 

        # Calcula o valor do desconto
        desconto = (valor_total_decimal * self.percentual_desconto_pix).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        valor_a_pagar = (valor_total_decimal - desconto).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

        print(f"Valor original: R$ {valor_total_decimal:.2f}")
        print(f"Desconto PIX ({self.percentual_desconto_pix * 100:.1f}%): R$ {desconto:.2f}")
        print(f"Valor a pagar com PIX: R$ {valor_a_pagar:.2f}")

        # verificação de fraude menos comum em PIX, mantido por consistência
        if not self._verificar_fraude({"valor": valor_a_pagar, "metodo": "PIX"}):
            return False, "Pagamento bloqueado por suspeita de fraude.", Decimal('0.0')

        # autorização/confirmação do PIX
        if self._autorizar_pagamento(valor_a_pagar, "PIX"):
            comprovante = self._gerar_comprovante(valor_a_pagar, "PIX")
            print(f"Comprovante gerado: {comprovante}")
            return True, "Pagamento PIX confirmado.", valor_a_pagar
        else:
            return False, "Falha ao confirmar pagamento PIX.", Decimal('0.0')

    def processar_reembolso(self, id_transacao_original: str, valor: float) -> bool:
        valor_decimal = Decimal(str(valor)) 
        print(f"Processando reembolso de R$ {valor_decimal:.2f} para transação {id_transacao_original}...")
        reembolso_ok = random.random() < 0.95 #chance alta de sucesso
        if reembolso_ok:
            print("Reembolso processado com sucesso.")
            return True
        else:
            print("Falha ao processar reembolso.")
            return False

    def _gerar_comprovante(self, valor_pago: Decimal, metodo: str, num_parcelas: int | None = None, valor_parcela: Decimal | None = None) -> str:
        # Gera um ID único para simular o comprovante/ID da transação
        id_transacao = str(uuid.uuid4())
        print(f"--- Comprovante de Pagamento ---")
        print(f"ID da Transação: {id_transacao}") 
        print(f"Método: {metodo}") 
        if metodo == "Cartão de Crédito" and num_parcelas and num_parcelas > 1 and valor_parcela: # Se for parcelado, mostra o número de parcelas e o valor de cada parcela
            print(f"Valor Total: R$ {valor_pago:.2f} ({num_parcelas}x de R$ {valor_parcela:.2f})")
        else:
            print(f"Valor Pago: R$ {valor_pago:.2f}")
        print(f"-------------------------------")
        return id_transacao

    def configurar_taxas(self, taxa_juros: float | None = None, desconto_pix: float | None = None): 
        if taxa_juros is not None: # Atualiza a taxa de juros do parcelamento.
            if not 0 <= taxa_juros <= 100: # Verifica se a taxa de juros está entre 0 e 100
                raise ValueError("A taxa de juros deve estar entre 0 e 100.") # Lança um erro se a taxa for inválida
            self.taxa_juros_parcelamento = Decimal(str(taxa_juros)) / Decimal('100.0')
            print(f"Taxa de juros atualizada para {taxa_juros:.2f}%.")

        if desconto_pix is not None:
            if not 0 <= desconto_pix <= 100:
                raise ValueError("O percentual de desconto PIX deve estar entre 0 e 100.")
            self.percentual_desconto_pix = Decimal(str(desconto_pix)) / Decimal('100.0')
            print(f"Desconto PIX atualizado para {desconto_pix:.1f}%.")

if __name__ == '__main__':
    sistema_pag = SistemaPagamento(taxa_juros_parcelamento=3.5, percentual_desconto_pix=10.0)

    print("\n--- Teste Cartão de Crédito (À Vista) ---")
    sucesso_cc_avista, msg_cc_avista, valor_pago_cc_avista, _ = sistema_pag.processar_cartao_credito(100.0, 1, {"numero": "**** **** **** 1234"})
    print(f"Resultado: {sucesso_cc_avista} - {msg_cc_avista} - Valor Pago: {valor_pago_cc_avista:.2f}")

    print("\n--- Teste Cartão de Crédito (Parcelado 3x) ---")
    sucesso_cc_parc, msg_cc_parc, valor_pago_cc_parc, valor_parc = sistema_pag.processar_cartao_credito(500.0, 3, {"numero": "**** **** **** 5678"})
    print(f"Resultado: {sucesso_cc_parc} - {msg_cc_parc} - Valor Total Pago: {valor_pago_cc_parc:.2f} - Parcela: {valor_parc:.2f}")

    print("\n--- Teste PIX ---")
    sucesso_pix, msg_pix, valor_pago_pix = sistema_pag.processar_pix(250.0)
    print(f"Resultado: {sucesso_pix} - {msg_pix} - Valor Pago: {valor_pago_pix:.2f}")

    print("\n--- Teste Reembolso ---")
    sucesso_reembolso = sistema_pag.processar_reembolso("some-transaction-id", 50.0)
    print(f"Resultado Reembolso: {sucesso_reembolso}")

    print("\n--- Teste Cálculo Parcelas  ---")
    valor_teste = Decimal('1000.00')
    for n_parc in [1, 3, 6, 12]:
        parcela = sistema_pag.calcular_valor_parcela(valor_teste, n_parc)
        total_pago = (parcela * Decimal(n_parc)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        print(f"{n_parc}x de R$ {parcela:.2f} = Total R$ {total_pago:.2f}")

    print("\n--- Configurando novas taxas ---")
    sistema_pag.configurar_taxas(taxa_juros=1.99, desconto_pix=7.5)
    print(f"Nova taxa juros: {sistema_pag.taxa_juros_parcelamento * 100:.2f}% - Novo desconto PIX: {sistema_pag.percentual_desconto_pix * 100:.1f}% ")

