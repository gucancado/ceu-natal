import pytest

from app.tools.mapa_natal import calcular_mapa_natal
from tests.conftest import ANA, BH


def _ana() -> dict:
    return calcular_mapa_natal(**ANA)


def test_mapa_completo_tem_todas_secoes():
    mapa = _ana()
    assert mapa["nome"] == "Ana"
    assert mapa["sistema_casas"] == "Placidus"
    assert set(mapa["planetas"].keys()) == {
        "sol", "lua", "mercurio", "venus", "marte",
        "jupiter", "saturno", "urano", "netuno", "plutao",
    }
    assert set(mapa["pontos_sensiveis"].keys()) == {
        "nodo_norte_verdadeiro", "nodo_sul_verdadeiro", "chiron",
    }
    assert set(mapa["angulos"].keys()) == {
        "ascendente", "meio_do_ceu", "descendente", "fundo_do_ceu",
    }
    assert set(mapa["casas"].keys()) == {f"casa_{i}" for i in range(1, 13)}
    assert isinstance(mapa["aspectos"], list) and len(mapa["aspectos"]) > 0
    assert "sintese" in mapa


def test_mapa_parcial_sem_hora():
    mapa = calcular_mapa_natal(data="12/03/1990", nome="Ana")
    assert mapa["casas"] is None
    assert mapa["angulos"] == {}
    # planetas presentes, mas sem casa
    assert "casa" not in mapa["planetas"]["sol"]
    assert "aviso" in mapa


def test_stellium_por_signo_detectado():
    """Teste de detecção, não de referência: o mapa fictício de Ana tem Saturno,
    Urano e Netuno em Capricórnio, e a síntese deve acusar o stellium."""
    mapa = _ana()
    stelliums = mapa["sintese"]["stelliums"]
    em_capricornio = [s for s in stelliums if s["tipo"] == "signo" and s["valor"] == "Capricornio"]
    assert em_capricornio, f"Esperava stellium em Capricórnio; stelliums={stelliums}"
    planetas = set(em_capricornio[0]["planetas"])
    assert {"saturno", "urano", "netuno"}.issubset(planetas)


def test_aspectos_exatos_marcados():
    mapa = _ana()
    aspectos_exatos = [a for a in mapa["aspectos"] if a["exato"]]
    for a in aspectos_exatos:
        assert a["orbe"] < 0.5


def test_orbe_dentro_dos_limites():
    """Aspectos não devem exceder os orbes do spec (8 luminares, 6 outros, 4 trig/sext)."""
    mapa = _ana()
    luminares = {"sol", "lua"}
    for a in mapa["aspectos"]:
        tem_lum = a["planeta_a"] in luminares or a["planeta_b"] in luminares
        if a["tipo"] in ("conjuncao", "oposicao"):
            limite = 8.0 if tem_lum else 6.0
        elif a["tipo"] == "quadratura":
            limite = 6.0
        elif a["tipo"] in ("trigono", "sextil"):
            limite = 4.0
        else:
            limite = 2.0
        assert a["orbe"] <= limite + 1e-6, f"{a} excede limite {limite}"


def test_sintese_distribuicoes_somam_dez():
    mapa = _ana()
    elementos = mapa["sintese"]["distribuicao_elementos"]
    qualidades = mapa["sintese"]["distribuicao_qualidades"]
    assert sum(elementos.values()) == 10
    assert sum(qualidades.values()) == 10


def test_planetas_tem_campos_enriquecidos():
    sol = _ana()["planetas"]["sol"]
    for campo in ("signo", "casa", "grau", "grau_decimal", "posicao_absoluta",
                  "retrogrado", "velocidade", "declinacao", "elemento", "qualidade"):
        assert campo in sol, f"Campo '{campo}' ausente em planetas.sol"


def test_sistema_casas_default_placidus():
    mapa = _ana()
    assert mapa["sistema_casas"] == "Placidus"


def test_sistema_casas_whole_sign_casa_1_em_zero_grau():
    """Whole Sign: cúspide da casa 1 sempre em 0° do signo do ASC."""
    mapa = calcular_mapa_natal(
        data="12/03/1990", hora="14:30", local="Belo Horizonte, MG", nome="Ana",
        sistema_casas="W",
        lat=BH["lat"], lng=BH["lng"], tz_str=BH["tz_str"],
    )
    assert mapa["sistema_casas"] == "Whole Sign"
    casa_1 = mapa["casas"]["casa_1"]
    # No Whole Sign, casa_1 começa em 0° do signo do ASC — grau_decimal == 0.0
    assert casa_1["grau_decimal"] == pytest.approx(0.0, abs=1e-3)
    # E o signo da casa 1 == signo do ASC
    assert casa_1["signo"] == mapa["angulos"]["ascendente"]["signo"]


def test_sistema_casas_invalido_levanta_value_error():
    with pytest.raises(ValueError):
        calcular_mapa_natal(
            data="12/03/1990", hora="14:30", local="Belo Horizonte, MG",
            sistema_casas="Z",
            lat=BH["lat"], lng=BH["lng"], tz_str=BH["tz_str"],
        )


def test_hora_inexistente_no_horario_de_verao_vira_value_error():
    with pytest.raises(ValueError, match="is_dst"):
        calcular_mapa_natal(data="04/11/2018", hora="00:30", local="Belo Horizonte, MG", **BH)


def test_hora_ambigua_resolvida_com_is_dst():
    m = calcular_mapa_natal(data="16/02/2019", hora="23:30", local="Belo Horizonte, MG", is_dst=False, **BH)
    assert m["angulos"]["ascendente"]
