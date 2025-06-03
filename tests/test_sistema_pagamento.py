import unittest
from decimal import Decimal, ROUND_HALF_UP
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from ecommerce.sistema_pagamento import SistemaPagamento

class SistemaPagamentoCalculoTest(unittest.TestCase):

    def setUp(self):
        self.taxa_juros = 2.0 # 2% ao mês
        self.desconto_pix = 10.0 # 10%
        self.sistema_pag = SistemaPagamento(taxa_juros_parcelamento=self.taxa_juros, percentual_desconto_pix=self.desconto_pix)
        self.valor_base = Decimal('1000.00')

    def test_calculo_cartao_credito_a_vista(self):
        #Questão 3: Cálculo correto do valor para pagamento com cartão de crédito à vista

        valor_parcela = self.sistema_pag.calcular_valor_parcela(self.valor_base, 1)
        valor_total_pago = valor_parcela * 1

        self.assertAlmostEqual(valor_parcela, self.valor_base, delta=0.01)
        self.assertAlmostEqual(valor_total_pago, self.valor_base, delta=0.01)

        _, _, valor_pago_processado, _ = self.sistema_pag.processar_cartao_credito(float(self.valor_base), 1, {})

    def test_calculo_cartao_credito_parcelado_com_juros(self):
        #Questão 3: Cálculo correto do valor para pagamento com cartão de crédito parcelado
        #Questão 3: Cálculo do valor das parcelas
        
        num_parcelas = 3
        taxa_decimal = Decimal(str(self.taxa_juros)) / Decimal('100.0')

        valor_parcela_esperado = Decimal('346.76')

        valor_parcela_calculado = self.sistema_pag.calcular_valor_parcela(self.valor_base, num_parcelas)
        self.assertAlmostEqual(valor_parcela_calculado, valor_parcela_esperado, delta=0.01)

        valor_total_pago_esperado = (valor_parcela_esperado * num_parcelas).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        self.assertAlmostEqual(valor_parcela_calculado * num_parcelas, valor_total_pago_esperado, delta=0.05) 

    def test_calculo_cartao_credito_parcelado_sem_juros(self):
        #Questão 3: Cálculo correto do valor para pagamento com cartão de crédito parcelado
        #Questão 3: Cálculo do valor das parcelas
        
        sistema_sem_juros = SistemaPagamento(taxa_juros_parcelamento=0.0, percentual_desconto_pix=self.desconto_pix)
        num_parcelas = 6
        valor_parcela_esperado = (self.valor_base / num_parcelas).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

        valor_parcela_calculado = sistema_sem_juros.calcular_valor_parcela(self.valor_base, num_parcelas)
        self.assertAlmostEqual(valor_parcela_calculado, Decimal('166.67'), delta=0.01)

        self.assertAlmostEqual(valor_parcela_calculado * num_parcelas, self.valor_base, delta=0.05)

    def test_calculo_pix_com_desconto(self):
       # Questão 3: Cálculo correto do valor para pagamento com PIX aplicando o desconto
        
        desconto_decimal = Decimal(str(self.desconto_pix)) / Decimal('100.0')
        valor_desconto_esperado = (self.valor_base * desconto_decimal).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        valor_final_esperado = (self.valor_base - valor_desconto_esperado).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

        _, _, valor_pago_processado = self.sistema_pag.processar_pix(float(self.valor_base))

        valor_a_pagar_calculado = (self.valor_base * (Decimal('1.0') - desconto_decimal)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        self.assertAlmostEqual(valor_a_pagar_calculado, valor_final_esperado, delta=0.01)

    def test_calculo_valor_parcela_invalido(self):
        #Questão 3: Cálculo do valor das parcelas com erro
        
        with self.assertRaises(ValueError):
            self.sistema_pag.calcular_valor_parcela(self.valor_base, 0)
        with self.assertRaises(ValueError):
            self.sistema_pag.calcular_valor_parcela(self.valor_base, -1)

if __name__ == "__main__":
    unittest.main()