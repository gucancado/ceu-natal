"""
Testes da lógica temporal das revoluções. Não importam Kerykeion — rodam em
qualquer ambiente, inclusive Windows.
"""
from datetime import datetime, timezone

import pytest

from app.core.periodos import (
    ANO_TROPICO_DIAS,
    MES_SIDERAL_DIAS,
    ancora_revolucao_solar,
    aniversario_no_ano,
    ciclo_anterior,
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

    def test_ano_anterior_ao_nascimento_rejeitado(self):
        with pytest.raises(ValueError, match="anterior ao nascimento"):
            validar_ano_revolucao(1850, ano_nascimento=1989)

    def test_ano_do_proprio_nascimento_aceito(self):
        # A primeira revolução solar de alguém é a do ano em que nasceu.
        assert validar_ano_revolucao(1989, ano_nascimento=1989) == 1989

    def test_ano_posterior_ao_nascimento_aceito(self):
        assert validar_ano_revolucao(2026, ano_nascimento=1989) == 2026


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
    # Tolerância de 1 segundo: a saída trunca microssegundos de propósito.
    def test_solar_cobre_um_ano_tropico(self):
        inicio = datetime(2026, 7, 24, 15, 30)
        v = vigencia_solar(inicio)
        ini = datetime.fromisoformat(v["inicio_utc"])
        fim = datetime.fromisoformat(v["fim_aproximado_utc"])
        assert abs((fim - ini).total_seconds() - ANO_TROPICO_DIAS * 86400.0) <= 1.0
        assert v["duracao_dias"] == pytest.approx(ANO_TROPICO_DIAS)

    def test_lunar_cobre_um_mes_sideral(self):
        inicio = datetime(2026, 7, 24, 15, 30)
        v = vigencia_lunar(inicio)
        ini = datetime.fromisoformat(v["inicio_utc"])
        fim = datetime.fromisoformat(v["fim_aproximado_utc"])
        assert abs((fim - ini).total_seconds() - MES_SIDERAL_DIAS * 86400.0) <= 1.0

    def test_saida_sem_microssegundos(self):
        inicio = datetime(2026, 7, 24, 15, 30, 12, 345678)
        v = vigencia_solar(inicio)
        assert "." not in v["inicio_utc"]
        assert "." not in v["fim_aproximado_utc"]

    def test_saida_declara_o_fuso(self):
        # Sem offset explícito um consumidor pode tratar como hora local.
        v = vigencia_solar(datetime(2026, 7, 24, 15, 30))
        assert v["inicio_utc"].endswith("+00:00")
        assert v["fim_aproximado_utc"].endswith("+00:00")

    def test_entrada_com_fuso_e_convertida_para_utc(self):
        inicio = datetime(2026, 7, 24, 15, 30, tzinfo=timezone.utc)
        assert vigencia_solar(inicio)["inicio_utc"] == "2026-07-24T15:30:00+00:00"

    def test_nota_explica_a_aproximacao(self):
        assert "duração média" in vigencia_solar(datetime(2026, 1, 1))["nota"]


class TestCicloAnterior:
    def test_retorno_no_mesmo_dia_nao_tem_ciclo_anterior(self):
        # A data pedida é o próprio dia do retorno: nada em curso antes dele.
        assert ciclo_anterior(
            datetime(2026, 8, 4, 4, 39), datetime(2026, 8, 4), MES_SIDERAL_DIAS
        ) is None

    def test_retorno_futuro_reporta_o_ciclo_em_curso(self):
        c = ciclo_anterior(
            datetime(2026, 8, 4, 4, 39), datetime(2026, 7, 29), MES_SIDERAL_DIAS
        )
        assert c is not None
        inicio = datetime.fromisoformat(c["inicio_aproximado_utc"])
        # ~27,3 dias antes do retorno, portanto no começo de julho
        assert inicio.month == 7 and inicio.day == 7
        assert "ciclo SEGUINTE" in c["nota"]

    def test_inicio_do_ciclo_anterior_precede_a_referencia(self):
        c = ciclo_anterior(
            datetime(2026, 8, 4), datetime(2026, 7, 29), MES_SIDERAL_DIAS
        )
        assert datetime.fromisoformat(c["inicio_aproximado_utc"]) < datetime(
            2026, 7, 29, tzinfo=timezone.utc
        )

    def test_fim_sempre_posterior_ao_inicio(self):
        inicio = datetime(2026, 1, 1)
        for v in (vigencia_solar(inicio), vigencia_lunar(inicio)):
            assert v["fim_aproximado_utc"] > v["inicio_utc"]
