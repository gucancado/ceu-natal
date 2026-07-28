"""
Testes da lógica temporal das revoluções. Não importam Kerykeion — rodam em
qualquer ambiente, inclusive Windows.
"""
from datetime import datetime

import pytest

from app.core.periodos import (
    ANO_TROPICO_DIAS,
    MES_SIDERAL_DIAS,
    ancora_revolucao_solar,
    aniversario_no_ano,
    validar_ano_revolucao,
    vigencia_lunar,
    vigencia_solar,
)


class TestValidarAnoRevolucao:
    def test_ano_comum_passa(self):
        assert validar_ano_revolucao(2026) == 2026

    def test_limites_inclusivos(self):
        assert validar_ano_revolucao(1800) == 1800
        assert validar_ano_revolucao(2200) == 2200

    def test_abaixo_do_minimo(self):
        with pytest.raises(ValueError, match="fora da faixa"):
            validar_ano_revolucao(1799)

    def test_acima_do_maximo(self):
        with pytest.raises(ValueError, match="fora da faixa"):
            validar_ano_revolucao(2201)

    def test_string_rejeitada(self):
        with pytest.raises(ValueError, match="inteiro"):
            validar_ano_revolucao("2026")

    def test_bool_rejeitado(self):
        # bool é subclasse de int em Python — precisa ser barrado explicitamente
        with pytest.raises(ValueError, match="inteiro"):
            validar_ano_revolucao(True)


class TestAniversarioNoAno:
    def test_data_comum(self):
        assert aniversario_no_ano(24, 7, 2026) == datetime(2026, 7, 24)

    def test_29_fev_em_ano_bissexto_preserva_o_dia(self):
        assert aniversario_no_ano(29, 2, 2028) == datetime(2028, 2, 29)

    def test_29_fev_em_ano_comum_cai_para_28(self):
        assert aniversario_no_ano(29, 2, 2026) == datetime(2026, 2, 28)

    def test_ano_secular_nao_bissexto(self):
        # 1900 não é bissexto (divisível por 100 e não por 400)
        assert aniversario_no_ano(29, 2, 1900) == datetime(1900, 2, 28)


class TestAncoraRevolucaoSolar:
    def test_recua_tres_dias(self):
        assert ancora_revolucao_solar(24, 7, 2026) == datetime(2026, 7, 21)

    def test_aniversario_em_1_de_janeiro_ancora_no_ano_anterior(self):
        assert ancora_revolucao_solar(1, 1, 2026) == datetime(2025, 12, 29)

    def test_aniversario_em_3_de_janeiro_ancora_no_ano_anterior(self):
        assert ancora_revolucao_solar(3, 1, 2026) == datetime(2025, 12, 31)

    def test_aniversario_em_4_de_janeiro_ancora_no_mesmo_ano(self):
        assert ancora_revolucao_solar(4, 1, 2026) == datetime(2026, 1, 1)

    def test_aniversario_em_1_de_marco_recua_para_fevereiro(self):
        assert ancora_revolucao_solar(1, 3, 2026) == datetime(2026, 2, 26)

    def test_29_fev_em_ano_comum(self):
        assert ancora_revolucao_solar(29, 2, 2026) == datetime(2026, 2, 25)

    def test_31_de_dezembro(self):
        assert ancora_revolucao_solar(31, 12, 2026) == datetime(2026, 12, 28)


class TestVigencia:
    def test_solar_cobre_um_ano_tropico(self):
        inicio = datetime(2026, 7, 24, 15, 30)
        v = vigencia_solar(inicio)
        assert v["inicio"] == inicio.isoformat()
        fim = datetime.fromisoformat(v["fim_aproximado"])
        assert abs((fim - inicio).total_seconds() / 86400.0 - ANO_TROPICO_DIAS) < 1e-6

    def test_lunar_cobre_um_mes_sideral(self):
        inicio = datetime(2026, 7, 24, 15, 30)
        v = vigencia_lunar(inicio)
        fim = datetime.fromisoformat(v["fim_aproximado"])
        assert abs((fim - inicio).total_seconds() / 86400.0 - MES_SIDERAL_DIAS) < 1e-6

    def test_fim_sempre_posterior_ao_inicio(self):
        inicio = datetime(2026, 1, 1)
        assert vigencia_solar(inicio)["fim_aproximado"] > inicio.isoformat()
        assert vigencia_lunar(inicio)["fim_aproximado"] > inicio.isoformat()
