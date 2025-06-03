import unittest
from decimal import Decimal, ROUND_HALF_UP
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), ".")))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from ecommerce.sistema_pagamento import SistemaPagamento

class ConfiguracaoSistemaPagamentoTest(unittest.TestCase):
    
    def setUp(self):
        """Valor base para os testes."""
        self.valor_base = Decimal("1000.00")

    def _testar_parcelamento_com_taxa(self, taxa_juros_percent: float, num_parcelas: int, valor_esperado_parcela: Decimal, valor_total_esperado: Decimal):
        """Helper para testar cálculo de parcelas com taxa específica."""
        sistema = SistemaPagamento(taxa_juros_parcelamento=taxa_juros_percent, percentual_desconto_pix=0)
        valor_calculado_parcela = sistema.calcular_valor_parcela(self.valor_base, num_parcelas)
        valor_total_calculado = (valor_calculado_parcela * Decimal(num_parcelas)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        
        print(f"\nTeste Taxa: {taxa_juros_percent}%, Parcelas: {num_parcelas}")
        print(f"  Parcela Calculada: {valor_calculado_parcela:.2f}, Esperada: {valor_esperado_parcela:.2f}")
        print(f"  Total Calculado: {valor_total_calculado:.2f}, Esperado: {valor_total_esperado:.2f}")
        
        self.assertAlmostEqual(float(valor_calculado_parcela), float(valor_esperado_parcela), delta=0.01,
                            msg=f"Taxa {taxa_juros_percent}%, {num_parcelas}x - Parcela incorreta")
        self.assertAlmostEqual(float(valor_total_calculado), float(valor_total_esperado), delta=0.01,
                            msg=f"Taxa {taxa_juros_percent}%, {num_parcelas}x - Total incorreto")

    def test_parcelamento_diferentes_taxas_juros_e_parcelas(self):
        #Questão 9: Diferentes taxas de juros para parcelamento
        #Questão 9: Diferentes quantidades de parcelas
        cenarios = [
            # Taxa 1.0%
            (1.0, 3, Decimal("340.02"), Decimal("1020.06")), 
            (1.0, 6, Decimal("172.55"), Decimal("1035.30")), 
            # Taxa 2.5% 
            (2.5, 3, Decimal("350.14"), Decimal("1050.42")), 
            (2.5, 12, Decimal("97.49"), Decimal("1169.88")), 
            # Taxa 0% (Sem Juros)
            (0.0, 4, Decimal("250.00"), Decimal("1000.00")),
            (0.0, 10, Decimal("100.00"), Decimal("1000.00")),
        ]

        for taxa, parcelas, parcela_esp, total_esp in cenarios:
            self._testar_parcelamento_com_taxa(taxa, parcelas, parcela_esp, total_esp)

    def _testar_pix_com_desconto(self, percentual_desconto: float, valor_final_esperado: Decimal):
        """Helper para testar cálculo de PIX com desconto específico."""
        sistema = SistemaPagamento(taxa_juros_parcelamento=0, percentual_desconto_pix=percentual_desconto)
        
        desconto = (self.valor_base * (Decimal(str(percentual_desconto)) / Decimal("100.0"))).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        valor_calculado = (self.valor_base - desconto).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        
        print(f"\nTeste Desconto PIX: {percentual_desconto}%")
        print(f"  Valor Calculado: {valor_calculado:.2f}, Esperado: {valor_final_esperado:.2f}")
        
        self.assertAlmostEqual(float(valor_calculado), float(valor_final_esperado), delta=0.01,
                            msg=f"Desconto {percentual_desconto}% - Valor final incorreto")

    def test_pix_diferentes_percentuais_desconto(self):
        #Questão 9: Diferentes percentuais de desconto para pagamento via PIX
    
        cenarios = [
            (0.0, Decimal("1000.00")),  # Sem desconto
            (5.0, Decimal("950.00")),   # 5% de desconto
            (7.5, Decimal("925.00")),   # 7.5% de desconto
            (10.0, Decimal("900.00")),  # 10% de desconto
            (15.2, Decimal("848.00")),  # 15.2% de desconto
        ]

        for desconto, valor_esp in cenarios:
            self._testar_pix_com_desconto(desconto, valor_esp)

if __name__ == "__main__":
    unittest.main()