from datetime import datetime
from types import SimpleNamespace

import pytest

from app.tools.progressoes import (
    _destaques,
    _flags_signo,
    calcular_progressoes,
    computar_data_progredida,
)
from tests.conftest import ANA


# ─────────────────────────────────────────────────────────────
# Pure helpers
# ─────────────────────────────────────────────────────────────
class TestComputarDataProgredida:
    def test_data_alvo_igual_natal_offset_zero(self):
        natal = datetime(1990, 3, 12, 14, 30)
        prog = computar_data_progredida(natal, natal)
        assert prog == natal

    def test_36_anos_depois_avanca_36_dias(self):
        natal = datetime(1990, 3, 12)
        alvo = datetime(2026, 3, 12)  # exatamente 36 anos
        prog = computar_data_progredida(natal, alvo)
        delta_dias = (prog - natal).total_seconds() / 86400.0
        assert 35 <= delta_dias <= 37


def test_ano_da_regra_e_juliano():
    from app.tools.progressoes import SEGUNDOS_POR_ANO_JULIANO
    assert SEGUNDOS_POR_ANO_JULIANO == 365.25 * 86400.0


class TestFlagsSigno:
    def test_grau_baixo_marca_ingresso_recente(self):
        assert _flags_signo(0.3, "sol")["ingresso_recente"] is True
        assert _flags_signo(0.3, "sol")["mudanca_iminente"] is False

    def test_grau_alto_marca_mudanca_iminente(self):
        assert _flags_signo(29.5, "lua")["mudanca_iminente"] is True
        assert _flags_signo(29.5, "sol")["mudanca_iminente"] is True
        assert _flags_signo(29.5, "lua")["ingresso_recente"] is False

    def test_grau_meio_signo_sem_flags(self):
        flags = _flags_signo(15.0, "sol")
        assert flags["ingresso_recente"] is False
        assert flags["mudanca_iminente"] is False

    def test_planeta_lento_nunca_marca_mudanca_iminente(self):
        # Plutão progredido leva séculos para trocar de signo: "iminente" não se aplica.
        assert _flags_signo(29.5, "plutao")["mudanca_iminente"] is False
        assert _flags_signo(29.5, "mercurio")["mudanca_iminente"] is False


def _ponto(nome: str, sign: str, position: float):
    return SimpleNamespace(name=nome, sign=sign, position=position)


def test_mudancas_iminentes_so_lista_sol_e_lua():
    """Subject sintético: Sol, Lua e Plutão todos a 29,5° do signo."""
    nomes = {
        "sun": "Sun", "moon": "Moon", "mercury": "Mercury", "venus": "Venus",
        "mars": "Mars", "jupiter": "Jupiter", "saturn": "Saturn",
        "uranus": "Uranus", "neptune": "Neptune", "pluto": "Pluto",
    }
    graus = {"sun": 29.5, "moon": 29.5, "pluto": 29.5}
    subject = SimpleNamespace(**{
        attr: _ponto(nome, "Sco", graus.get(attr, 10.0)) for attr, nome in nomes.items()
    })
    planetas = {
        "sol": {"signo": "Escorpiao", "casa_natal": 1, "ingresso_recente": False},
        "lua": {"signo": "Escorpiao", "casa_natal": 1, "ingresso_recente": False},
    }
    destaques = _destaques(planetas, subject)
    assert sorted(m["planeta"] for m in destaques["mudancas_iminentes"]) == ["lua", "sol"]


# ─────────────────────────────────────────────────────────────
# Shape do retorno
# ─────────────────────────────────────────────────────────────
def test_estrutura_completa_para_alvo_2026():
    res = calcular_progressoes(natal=ANA, data_alvo="30/04/2026")
    assert res["natal"]["nome"] == "Ana"
    assert res["data_alvo"] == "30/04/2026"
    # 12/03/1990 → 30/04/2026 ≈ 36.13 anos
    assert res["idade_aproximada"] == 36
    assert "planetas_progredidos" in res
    assert "aspectos_progredido_natal" in res
    assert "destaques" in res
    assert "metodo" in res


def test_campo_metodo_explicita_progressao_e_mc():
    """Agentes interpretadores precisam saber qual técnica foi usada,
    sobretudo pra ponderar a precisão do MC progredido."""
    res = calcular_progressoes(natal=ANA, data_alvo="30/04/2026")
    metodo = res["metodo"]
    assert metodo["progressao"] == "secundaria"
    assert "regra" in metodo
    assert "mc" in metodo
    assert "nota" in metodo
    # Sanity: nota não-vazia e descritiva
    assert len(metodo["nota"]) > 30


def test_planetas_progredidos_tem_lua_e_sol():
    res = calcular_progressoes(natal=ANA, data_alvo="30/04/2026")
    pp = res["planetas_progredidos"]
    for nome in ("sol", "lua", "mercurio", "venus", "marte"):
        assert nome in pp
        assert "casa_natal" in pp[nome]
        assert "ingresso_recente" in pp[nome]
        assert "mudanca_iminente" in pp[nome]


def test_destaques_sempre_tem_lua_progredida():
    res = calcular_progressoes(natal=ANA, data_alvo="30/04/2026")
    destaques = res["destaques"]
    assert "lua_progredida" in destaques
    assert "sol_progredido_signo" in destaques
    assert "mudancas_iminentes" in destaques
    lua = destaques["lua_progredida"]
    assert "signo" in lua
    assert "casa_natal" in lua
    assert "ingresso_recente" in lua


def test_data_alvo_igual_nascimento_idade_zero():
    res = calcular_progressoes(natal=ANA, data_alvo="12/03/1990")
    assert res["idade_aproximada"] == 0


def test_data_alvo_anterior_ao_nascimento_falha():
    with pytest.raises(ValueError):
        calcular_progressoes(natal=ANA, data_alvo="01/01/1980")


def test_natal_sem_hora_falha():
    natal = {**ANA}
    natal.pop("hora")
    with pytest.raises(ValueError):
        calcular_progressoes(natal=natal, data_alvo="30/04/2026")
