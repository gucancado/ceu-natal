import pytest

from app.tools.composto import calcular_mapa_composto, midpoint_longitude
from tests.conftest import BH


GUSTAVO = {
    "data": "24/07/1989", "hora": "09:20", "local": "Belo Horizonte, MG", "nome": "Gustavo",
    "lat": BH["lat"], "lng": BH["lng"], "tz_str": BH["tz_str"],
}
NAIARA = {
    "data": "09/06/1989", "hora": "14:05", "local": "Belo Horizonte, MG", "nome": "Naiara",
    "lat": BH["lat"], "lng": BH["lng"], "tz_str": BH["tz_str"],
}


# ─────────────────────────────────────────────────────────────
# Midpoint matemático — função pura
# ─────────────────────────────────────────────────────────────
class TestMidpointLongitude:
    def test_simples_sem_wrap(self):
        assert midpoint_longitude(0, 60) == pytest.approx(30.0)
        assert midpoint_longitude(100, 200) == pytest.approx(150.0)

    def test_cruzamento_de_360(self):
        """350° e 10° → 0° (caminho mais curto), não 180°."""
        assert midpoint_longitude(350, 10) == pytest.approx(0.0, abs=1e-6)
        assert midpoint_longitude(10, 350) == pytest.approx(0.0, abs=1e-6)

    def test_outro_wrap_caso(self):
        """340° e 20° → 0° também (diferença de 40° pelo lado curto)."""
        assert midpoint_longitude(340, 20) == pytest.approx(0.0, abs=1e-6)

    def test_pontos_antipodas_documentado(self):
        """Antípodas (90° e 270°) têm dois midpoints possíveis (0 ou 180);
        nossa implementação escolhe determinísticamente um por ordem dos args:
        midpoint(90, 270) = 180, midpoint(270, 90) = 0."""
        assert midpoint_longitude(90, 270) == pytest.approx(180.0)
        assert midpoint_longitude(270, 90) == pytest.approx(0.0, abs=1e-6)
        # Em ambos os casos o resultado é um dos dois antípodas (0 ou 180)
        for r in (midpoint_longitude(90, 270), midpoint_longitude(270, 90)):
            assert r == pytest.approx(0.0, abs=1e-6) or r == pytest.approx(180.0)

    def test_normaliza_input_acima_de_360(self):
        # 720° e 60° → equivale a 0° e 60° → 30°
        assert midpoint_longitude(720, 60) == pytest.approx(30.0)


# ─────────────────────────────────────────────────────────────
# Mapa composto — shape e propriedades
# ─────────────────────────────────────────────────────────────
def test_estrutura_completa():
    res = calcular_mapa_composto(pessoa_a=GUSTAVO, pessoa_b=NAIARA)
    assert res["tipo_composto"] == "midpoint"
    assert res["pessoa_a"]["nome"] == "Gustavo"
    assert res["pessoa_b"]["nome"] == "Naiara"

    # 10 planetas + 3 pontos sensíveis
    assert set(res["planetas_compostos"].keys()) == {
        "sol", "lua", "mercurio", "venus", "marte",
        "jupiter", "saturno", "urano", "netuno", "plutao",
    }
    assert set(res["pontos_sensiveis_compostos"].keys()) == {
        "nodo_norte_verdadeiro", "nodo_sul_verdadeiro", "chiron",
    }


def test_casas_ausentes_no_composto():
    """Composto midpoint não tem casas — campo deve ser None."""
    res = calcular_mapa_composto(pessoa_a=GUSTAVO, pessoa_b=NAIARA)
    assert res["casas"] is None


def test_angulos_compostos_quando_ambos_tem_local():
    res = calcular_mapa_composto(pessoa_a=GUSTAVO, pessoa_b=NAIARA)
    angulos = res["angulos_compostos"]
    assert "ascendente" in angulos
    assert "meio_do_ceu" in angulos
    for ang in angulos.values():
        assert "signo" in ang
        assert "grau" in ang


def test_aspectos_compostos_calculados():
    res = calcular_mapa_composto(pessoa_a=GUSTAVO, pessoa_b=NAIARA)
    aspectos = res["aspectos_compostos"]
    assert isinstance(aspectos, list)
    # Ordenados por orbe crescente
    orbes = [a["orbe"] for a in aspectos]
    assert orbes == sorted(orbes)
    # No composto não temos velocidades → aplicando=None em todos
    for a in aspectos:
        assert a["aplicando"] is None


def test_composto_mesma_pessoa_consigo_iguala_natal():
    """Composto de A com A: midpoint(x, x) = x → posições iguais às do natal."""
    res = calcular_mapa_composto(pessoa_a=GUSTAVO, pessoa_b=GUSTAVO)

    from app.tools.mapa_natal import calcular_mapa_natal
    natal = calcular_mapa_natal(
        data="24/07/1989", hora="09:20", local="Belo Horizonte, MG", nome="Gustavo",
        lat=BH["lat"], lng=BH["lng"], tz_str=BH["tz_str"],
    )

    # Posição absoluta de cada planeta no composto deve igualar a do natal
    for nome in ("sol", "lua", "mercurio", "venus", "marte",
                 "jupiter", "saturno", "urano", "netuno", "plutao"):
        comp = res["planetas_compostos"][nome]["posicao_absoluta"]
        nat = natal["planetas"][nome]["posicao_absoluta"]
        assert comp == pytest.approx(nat, abs=0.01), \
            f"{nome}: composto {comp} != natal {nat}"


def test_sintese_distribuicao_elementos():
    res = calcular_mapa_composto(pessoa_a=GUSTAVO, pessoa_b=NAIARA)
    sintese = res["sintese"]
    elementos = sintese["distribuicao_elementos"]
    # 10 planetas no composto → soma dos elementos = 10
    assert sum(elementos.values()) == 10
    assert "stelliums_compostos" in sintese


def test_pessoa_sem_data_falha():
    with pytest.raises(ValueError):
        calcular_mapa_composto(pessoa_a={}, pessoa_b=NAIARA)
