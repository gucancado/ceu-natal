from datetime import datetime

import pytest

from app.tools.progressoes import (
    _flags_signo,
    calcular_progressoes,
    computar_data_progredida,
)
from tests.conftest import BH


GUSTAVO = {
    "data": "24/07/1989", "hora": "09:20", "local": "Belo Horizonte, MG", "nome": "Gustavo",
    "lat": BH["lat"], "lng": BH["lng"], "tz_str": BH["tz_str"],
}


# ─────────────────────────────────────────────────────────────
# Pure helpers
# ─────────────────────────────────────────────────────────────
class TestComputarDataProgredida:
    def test_data_alvo_igual_natal_offset_zero(self):
        natal = datetime(1989, 7, 24, 9, 20)
        prog = computar_data_progredida(natal, natal)
        assert prog == natal

    def test_36_anos_depois_avanca_36_dias(self):
        natal = datetime(1989, 7, 24)
        alvo = datetime(2025, 7, 24)  # exatamente 36 anos
        prog = computar_data_progredida(natal, alvo)
        # Tolerância de 1 dia (365.25 vs 365): 36 * 0.25 = 9 dias podem se acumular
        delta_dias = (prog - natal).total_seconds() / 86400.0
        assert 35 <= delta_dias <= 37


class TestFlagsSigno:
    def test_grau_baixo_marca_ingresso_recente(self):
        assert _flags_signo(0.3)["ingresso_recente"] is True
        assert _flags_signo(0.3)["mudanca_iminente"] is False

    def test_grau_alto_marca_mudanca_iminente(self):
        assert _flags_signo(29.5)["mudanca_iminente"] is True
        assert _flags_signo(29.5)["ingresso_recente"] is False

    def test_grau_meio_signo_sem_flags(self):
        flags = _flags_signo(15.0)
        assert flags["ingresso_recente"] is False
        assert flags["mudanca_iminente"] is False


# ─────────────────────────────────────────────────────────────
# Shape do retorno
# ─────────────────────────────────────────────────────────────
def test_estrutura_completa_para_alvo_2026():
    res = calcular_progressoes(natal=GUSTAVO, data_alvo="30/04/2026")
    assert res["natal"]["nome"] == "Gustavo"
    assert res["data_alvo"] == "30/04/2026"
    # 24/07/1989 → 30/04/2026 ≈ 36.77 anos
    assert res["idade_aproximada"] == 36
    assert "planetas_progredidos" in res
    assert "aspectos_progredido_natal" in res
    assert "destaques" in res
    assert "metodo" in res


def test_campo_metodo_explicita_progressao_e_mc():
    """Agentes interpretadores precisam saber qual técnica foi usada,
    sobretudo pra ponderar a precisão do MC progredido."""
    res = calcular_progressoes(natal=GUSTAVO, data_alvo="30/04/2026")
    metodo = res["metodo"]
    assert metodo["progressao"] == "secundaria"
    assert "regra" in metodo
    assert "mc" in metodo
    assert "nota" in metodo
    # Sanity: nota não-vazia e descritiva
    assert len(metodo["nota"]) > 30


def test_planetas_progredidos_tem_lua_e_sol():
    res = calcular_progressoes(natal=GUSTAVO, data_alvo="30/04/2026")
    pp = res["planetas_progredidos"]
    for nome in ("sol", "lua", "mercurio", "venus", "marte"):
        assert nome in pp
        assert "casa_natal" in pp[nome]
        assert "ingresso_recente" in pp[nome]
        assert "mudanca_iminente" in pp[nome]


def test_destaques_sempre_tem_lua_progredida():
    res = calcular_progressoes(natal=GUSTAVO, data_alvo="30/04/2026")
    destaques = res["destaques"]
    assert "lua_progredida" in destaques
    assert "sol_progredido_signo" in destaques
    assert "mudancas_iminentes" in destaques
    lua = destaques["lua_progredida"]
    assert "signo" in lua
    assert "casa_natal" in lua
    assert "ingresso_recente" in lua


def test_data_alvo_igual_nascimento_idade_zero():
    res = calcular_progressoes(natal=GUSTAVO, data_alvo="24/07/1989")
    assert res["idade_aproximada"] == 0


def test_data_alvo_anterior_ao_nascimento_falha():
    with pytest.raises(ValueError):
        calcular_progressoes(natal=GUSTAVO, data_alvo="01/01/1980")


def test_natal_sem_hora_falha():
    natal = {**GUSTAVO}
    natal.pop("hora")
    with pytest.raises(ValueError):
        calcular_progressoes(natal=natal, data_alvo="30/04/2026")
