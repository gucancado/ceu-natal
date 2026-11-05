import pytest

from app.tools.composto import calcular_mapa_composto, midpoint_longitude
from tests.conftest import ANA, BH, BRUNO


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
        a implementação ordena os argumentos e fica com (menor + 90) % 360,
        então a ordem não importa: midpoint(90, 270) = midpoint(270, 90) = 180."""
        assert midpoint_longitude(90, 270) == pytest.approx(180.0)
        assert midpoint_longitude(270, 90) == pytest.approx(180.0)

    def test_comutativo(self):
        assert midpoint_longitude(10, 190) == midpoint_longitude(190, 10)
        for a, b in ((350, 10), (0, 60), (123.4, 301.2), (720, 60)):
            assert midpoint_longitude(a, b) == midpoint_longitude(b, a)

    def test_normaliza_input_acima_de_360(self):
        # 720° e 60° → equivale a 0° e 60° → 30°
        assert midpoint_longitude(720, 60) == pytest.approx(30.0)


# ─────────────────────────────────────────────────────────────
# Mapa composto — shape e propriedades
# ─────────────────────────────────────────────────────────────
def test_estrutura_completa():
    res = calcular_mapa_composto(pessoa_a=ANA, pessoa_b=BRUNO)
    assert res["tipo_composto"] == "midpoint"
    assert res["pessoa_a"]["nome"] == "Ana"
    assert res["pessoa_b"]["nome"] == "Bruno"

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
    res = calcular_mapa_composto(pessoa_a=ANA, pessoa_b=BRUNO)
    assert res["casas"] is None


def test_angulos_compostos_quando_ambos_tem_local():
    res = calcular_mapa_composto(pessoa_a=ANA, pessoa_b=BRUNO)
    angulos = res["angulos_compostos"]
    assert "ascendente" in angulos
    assert "meio_do_ceu" in angulos
    for ang in angulos.values():
        assert "signo" in ang
        assert "grau" in ang


def test_aspectos_compostos_calculados():
    res = calcular_mapa_composto(pessoa_a=ANA, pessoa_b=BRUNO)
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
    res = calcular_mapa_composto(pessoa_a=ANA, pessoa_b=ANA)

    from app.tools.mapa_natal import calcular_mapa_natal
    natal = calcular_mapa_natal(
        data="12/03/1990", hora="14:30", local="Belo Horizonte, MG", nome="Ana",
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
    res = calcular_mapa_composto(pessoa_a=ANA, pessoa_b=BRUNO)
    sintese = res["sintese"]
    elementos = sintese["distribuicao_elementos"]
    # 10 planetas no composto → soma dos elementos = 10
    assert sum(elementos.values()) == 10
    assert "stelliums_compostos" in sintese


def test_pessoa_sem_data_falha():
    with pytest.raises(ValueError, match="Campo 'data' obrigatório em pessoa_a."):
        calcular_mapa_composto(pessoa_a={}, pessoa_b=BRUNO)


def test_angulos_omitidos_quando_pessoa_sem_hora():
    sem_hora = {"data": "25/07/1992", "nome": "Bruno", "lat": BH["lat"], "lng": BH["lng"], "tz_str": BH["tz_str"]}
    c = calcular_mapa_composto(pessoa_a=ANA, pessoa_b=sem_hora)
    assert c["angulos_compostos"] == {}
    assert c["aviso"] == (
        "Ângulos compostos omitidos: hora ou local de nascimento ausente em Bruno."
    )


def test_sem_aviso_quando_ambos_completos():
    c = calcular_mapa_composto(pessoa_a=ANA, pessoa_b=BRUNO)
    assert "aviso" not in c
    assert set(c["angulos_compostos"]) == {"ascendente", "meio_do_ceu"}


def test_hora_presente_sem_local_omite_angulos():
    sem_local = {"nome": "Bruno", "data": "25/07/1992", "hora": "09:15"}
    c = calcular_mapa_composto(pessoa_a=ANA, pessoa_b=sem_local)
    assert c["angulos_compostos"] == {}
    assert c["aviso"] == (
        "Ângulos compostos omitidos: hora ou local de nascimento ausente em Bruno."
    )


def test_aviso_nomeia_as_duas_pessoas_e_anonimo():
    a = {"nome": "Ana", "data": "12/03/1990"}
    b = {"data": "25/07/1992", "hora": "09:15"}
    c = calcular_mapa_composto(pessoa_a=a, pessoa_b=b)
    assert c["aviso"] == (
        "Ângulos compostos omitidos: hora ou local de nascimento ausente em Ana e Anônimo."
    )


def test_composto_omite_quiron_sem_efemeride():
    # 01/01/1800 00:30 em Tóquio ainda é 31/12/1799 em UT: sem efeméride de Quíron.
    tokyo = {
        "nome": "Limite", "data": "01/01/1800", "hora": "00:30", "local": "Tóquio, Japão",
        "lat": 35.6895, "lng": 139.6917, "tz_str": "Asia/Tokyo",
    }
    composto = calcular_mapa_composto(pessoa_a=tokyo, pessoa_b=ANA)
    assert "chiron" not in composto["pontos_sensiveis_compostos"]
    assert "nodo_norte_verdadeiro" in composto["pontos_sensiveis_compostos"]
