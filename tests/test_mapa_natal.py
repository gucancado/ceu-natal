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


def test_outra_kerykeion_exception_nao_vira_erro_de_horario_de_verao(monkeypatch):
    """Só o erro de hora ambígua/inexistente (pytz) vira a mensagem do `is_dst`."""
    from kerykeion import AstrologicalSubjectFactory
    from kerykeion.schemas import KerykeionException

    def falha(*args, **kwargs):
        raise KerykeionException("x")

    monkeypatch.setattr(AstrologicalSubjectFactory, "from_birth_data", falha)
    with pytest.raises(KerykeionException, match="^x$"):
        calcular_mapa_natal(data="12/03/1990", hora="14:30", local="Belo Horizonte, MG", **BH)


def test_hora_ambigua_resolvida_com_is_dst():
    m = calcular_mapa_natal(data="16/02/2019", hora="23:30", local="Belo Horizonte, MG", is_dst=False, **BH)
    assert m["angulos"]["ascendente"]


# ─────────────────────────────────────────────────────────────
# Latitude polar: acima de 66° o Kerykeion corta a latitude das casas
# ─────────────────────────────────────────────────────────────
TROMSO = {"lat": 69.65, "lng": 18.96, "tz_str": "Europe/Oslo"}


def test_latitude_polar_omite_casas_com_aviso():
    mapa = calcular_mapa_natal(data="01/06/1990", hora="12:00", **TROMSO)
    assert mapa["casas"] is None
    assert mapa["angulos"] == {}
    assert "casa" not in mapa["planetas"]["sol"]
    assert "66°" in mapa["aviso"]
    assert mapa["sintese"]["hemisferio_vertical"] is None


def test_latitude_suporta_casas_no_limite():
    from app.core.kerykeion import LATITUDE_MAX_CASAS, latitude_suporta_casas

    assert LATITUDE_MAX_CASAS == 66.0
    assert latitude_suporta_casas(66.0) is True
    assert latitude_suporta_casas(-66.0) is True
    assert latitude_suporta_casas(66.01) is False
    assert latitude_suporta_casas(-69.65) is False


# ─────────────────────────────────────────────────────────────
# Sem hora: ao meio-dia a Lua pode estar até metade do movimento diário dela fora
# (a velocidade vai de ~12° a ~15°/dia, então a margem vai de ~6° a ~7,6°)
# ─────────────────────────────────────────────────────────────
def test_sem_hora_lua_perto_da_borda_pode_mudar_de_signo():
    # Data escolhida por cálculo: em 07/03/1990 ao meio-dia (sem local → UTC)
    # a Lua está a 29,7753° de Câncer, velocidade 13,2443°/dia → margem 6,62°.
    mapa = calcular_mapa_natal(data="07/03/1990")
    lua = mapa["planetas"]["lua"]
    assert lua["posicao_incerta"] is True
    assert lua["signo_pode_mudar"] is True
    assert lua["margem_graus"] == 6.62
    assert "sem a hora, a Lua pode variar até 6,6°" in mapa["aviso"]


@pytest.mark.parametrize(
    "data",
    [
        # Datas escolhidas por cálculo (sem local → 12:00 UTC). Nas três o signo da
        # Lua muda dentro do mesmo dia, mas ela fica entre 6,5° e metade do seu
        # movimento diário da borda (a margem fixa de 6,5° dava falso negativo).
        "27/02/1990",  # Áries 7,0978°, 14,549°/dia → margem 7,27°; 00:00 em Peixes
        "01/05/1990",  # Leão 6,6199°, 13,292°/dia → margem 6,65°; 00:00 em Câncer
        "15/07/1990",  # Áries 23,2569°, 14,040°/dia → margem 7,02°; 23:59 em Touro
    ],
)
def test_sem_hora_margem_da_lua_usa_a_velocidade_do_dia(data):
    lua = calcular_mapa_natal(data=data)["planetas"]["lua"]
    assert lua["margem_graus"] == round(abs(lua["velocidade"]) / 2, 2)
    assert lua["margem_graus"] > 6.5
    assert lua["signo_pode_mudar"] is True


def test_sem_hora_lua_no_meio_do_signo_nao_muda():
    # Data escolhida por cálculo: em 13/03/1990 ao meio-dia a Lua está a 15,7275° de
    # Libra (margem 6,07°); de 00:00 a 23:59 UTC ela vai de 9,64° a 21,77° de Libra.
    mapa = calcular_mapa_natal(data="13/03/1990")
    lua = mapa["planetas"]["lua"]
    assert lua["posicao_incerta"] is True
    assert lua["signo_pode_mudar"] is False


def test_sem_hora_aspectos_da_lua_marcados_incertos():
    mapa = calcular_mapa_natal(data="07/03/1990")
    com_lua = [a for a in mapa["aspectos"] if "lua" in (a["planeta_a"], a["planeta_b"])]
    sem_lua = [a for a in mapa["aspectos"] if "lua" not in (a["planeta_a"], a["planeta_b"])]
    assert com_lua and sem_lua
    assert all(a["incerto"] is True for a in com_lua)
    assert all("incerto" not in a for a in sem_lua)


def test_com_hora_lua_sem_marcas_de_incerteza():
    mapa = _ana()
    assert "posicao_incerta" not in mapa["planetas"]["lua"]
    assert "signo_pode_mudar" not in mapa["planetas"]["lua"]
    assert "margem_graus" not in mapa["planetas"]["lua"]
    assert all("incerto" not in a for a in mapa["aspectos"])


def test_local_resolvido_presente_com_local():
    mapa = calcular_mapa_natal(data="12/03/1990", hora="14:30", local="Belo Horizonte, MG", **BH)
    assert mapa["local_resolvido"] == {
        "lat": BH["lat"], "lng": BH["lng"], "fuso": BH["tz_str"],
    }


def test_local_resolvido_ausente_sem_local():
    mapa = calcular_mapa_natal(data="12/03/1990", hora="14:30")
    assert "local_resolvido" not in mapa


# ─────────────────────────────────────────────────────────────
# Ponto sem efeméride (Quíron fora de 1800–2399 em tempo universal)
# ─────────────────────────────────────────────────────────────
def _ponto_falso(nome: str, abs_pos: float):
    from types import SimpleNamespace

    return SimpleNamespace(name=nome, abs_pos=abs_pos, speed=1.0)


def test_iteradores_pulam_ponto_none():
    from types import SimpleNamespace

    from app.core.kerykeion import PLANETAS_PRINCIPAIS, coletar_pontos, pontos_sensiveis_iter

    planetas = {attr: _ponto_falso(attr.capitalize(), 10.0 * i)
                for i, attr in enumerate(PLANETAS_PRINCIPAIS)}
    subject = SimpleNamespace(
        **planetas,
        true_north_lunar_node=_ponto_falso("True_North_Lunar_Node", 200.0),
        true_south_lunar_node=_ponto_falso("True_South_Lunar_Node", 20.0),
        chiron=None,
    )
    nomes_sensiveis = [nome for nome, _ in pontos_sensiveis_iter(subject)]
    assert nomes_sensiveis == ["nodo_norte_verdadeiro", "nodo_sul_verdadeiro"]
    nomes = [p["nome"] for p in coletar_pontos(subject)]
    assert len(nomes) == 12
    assert "chiron" not in nomes


def test_mapa_no_limite_da_efemeride_omite_quiron():
    # 01/01/1800 00:30 em Tóquio ainda é 31/12/1799 em UT: sem efeméride de Quíron.
    mapa = calcular_mapa_natal(
        data="01/01/1800", hora="00:30", local="Tóquio, Japão",
        lat=35.6895, lng=139.6917, tz_str="Asia/Tokyo",
    )
    assert "chiron" not in mapa["pontos_sensiveis"]
    assert "nodo_norte_verdadeiro" in mapa["pontos_sensiveis"]
    assert all("chiron" not in (a["planeta_a"], a["planeta_b"]) for a in mapa["aspectos"])
