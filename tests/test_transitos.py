import pytest

from app.tools.transitos import (
    PLANETAS_LENTOS,
    calcular_transitos,
    destacar_transitos_lentos,
)
from tests.conftest import BH


GUSTAVO = {
    "data": "24/07/1989", "hora": "09:20", "local": "Belo Horizonte, MG", "nome": "Gustavo",
    "lat": BH["lat"], "lng": BH["lng"], "tz_str": BH["tz_str"],
}


# ─────────────────────────────────────────────────────────────
# Curadoria de trânsitos lentos — função pura, testável isolada
# ─────────────────────────────────────────────────────────────
def test_destacar_lentos_filtra_por_planeta_e_orbe():
    aspectos = [
        {"planeta_a": "saturno", "planeta_b": "sol", "tipo": "quadratura", "orbe": 0.5},
        {"planeta_a": "mercurio", "planeta_b": "sol", "tipo": "sextil", "orbe": 0.3},
        {"planeta_a": "plutao", "planeta_b": "lua", "tipo": "trigono", "orbe": 1.8},
        {"planeta_a": "saturno", "planeta_b": "marte", "tipo": "oposicao", "orbe": 3.0},
        {"planeta_a": "chiron", "planeta_b": "venus", "tipo": "conjuncao", "orbe": 0.9},
    ]
    destaques = destacar_transitos_lentos(aspectos)
    nomes = {(d["planeta_transito"], d["planeta_natal"]) for d in destaques}
    # Saturno ⨯ Sol (0.5°) entra, Plutão ⨯ Lua (1.8°) entra, Chiron ⨯ Vênus entra
    assert ("saturno", "sol") in nomes
    assert ("plutao", "lua") in nomes
    assert ("chiron", "venus") in nomes
    # Mercúrio é pessoal, não entra
    assert ("mercurio", "sol") not in nomes
    # Saturno ⨯ Marte com orbe 3° não entra (>2°)
    assert ("saturno", "marte") not in nomes


def test_lista_de_planetas_lentos_corresponde_ao_spec():
    assert PLANETAS_LENTOS == {"saturno", "urano", "netuno", "plutao", "chiron"}


# ─────────────────────────────────────────────────────────────
# Shape do retorno (smoke tests com Kerykeion real)
# ─────────────────────────────────────────────────────────────
def test_estrutura_completa_do_retorno():
    res = calcular_transitos(natal=GUSTAVO, data_transito="30/04/2026")
    assert "natal" in res
    assert "transito" in res
    assert "planetas_em_transito" in res
    assert "aspectos_transito_natal" in res
    assert "sintese" in res

    # 10 planetas em trânsito
    assert set(res["planetas_em_transito"].keys()) == {
        "sol", "lua", "mercurio", "venus", "marte",
        "jupiter", "saturno", "urano", "netuno", "plutao",
    }
    # cada um tem casa_natal preenchida
    for p in res["planetas_em_transito"].values():
        assert 1 <= p["casa_natal"] <= 12


def test_sem_hora_transito_usa_default():
    """hora_transito omitida não deve falhar — usa 12:00 UTC."""
    res = calcular_transitos(natal=GUSTAVO, data_transito="30/04/2026")
    assert res["transito"]["hora"] is None
    # Resultado tem que sair sem erro
    assert isinstance(res["aspectos_transito_natal"], list)


def test_campo_retrogrado_e_booleano():
    """Cada planeta em trânsito tem flag retrogrado bool (True ou False)."""
    res = calcular_transitos(natal=GUSTAVO, data_transito="30/04/2026")
    for p in res["planetas_em_transito"].values():
        assert isinstance(p["retrogrado"], bool)


def test_aspecto_exato_marca_exato_true():
    """Se houver aspecto com orbe < 0.5°, deve ter exato=True."""
    res = calcular_transitos(natal=GUSTAVO, data_transito="30/04/2026")
    for a in res["aspectos_transito_natal"]:
        if a["orbe"] < 0.5:
            assert a["exato"] is True


def test_sintese_conta_aplicando_e_separando():
    res = calcular_transitos(natal=GUSTAVO, data_transito="30/04/2026")
    sintese = res["sintese"]
    assert "aspectos_aplicando" in sintese
    assert "aspectos_separando" in sintese
    assert "transitos_para_luminares" in sintese
    assert "transitos_para_pessoais" in sintese
    assert "transitos_lentos_destacados" in sintese
    # Os 3 contadores são inteiros não-negativos
    for k in ("aspectos_aplicando", "aspectos_separando",
              "transitos_para_luminares", "transitos_para_pessoais"):
        assert isinstance(sintese[k], int)
        assert sintese[k] >= 0


def test_natal_sem_hora_levanta_value_error():
    natal_incompleto = {**GUSTAVO}
    natal_incompleto.pop("hora")
    with pytest.raises(ValueError):
        calcular_transitos(natal=natal_incompleto, data_transito="30/04/2026")
