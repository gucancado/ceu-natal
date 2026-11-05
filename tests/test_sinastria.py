from app.tools.sinastria import calcular_sinastria
from tests.conftest import ANA, BH, BRUNO


def test_sinastria_retorna_estrutura_completa():
    s = calcular_sinastria(ANA, BRUNO)
    assert s["pessoa_a"]["nome"] == "Ana"
    assert s["pessoa_b"]["nome"] == "Bruno"
    assert isinstance(s["aspectos_sinastria"], list) and len(s["aspectos_sinastria"]) > 0
    assert isinstance(s["ativacoes_de_casas"], list) and len(s["ativacoes_de_casas"]) > 0
    assert "sintese_sinastria" in s


def test_aspectos_bidirecionais_planeta_de_a_vs_b():
    s = calcular_sinastria(ANA, BRUNO)
    # Cada aspecto deve ter pessoa_a e pessoa_b distintos
    for a in s["aspectos_sinastria"]:
        assert a["pessoa_a"] == "Ana"
        assert a["pessoa_b"] == "Bruno"
        assert a["natureza"] in ("harmonico", "tensao", "neutro")


def test_ativacoes_bidirecionais():
    """Planetas de A caem em casas de B e planetas de B caem em casas de A."""
    s = calcular_sinastria(ANA, BRUNO)
    pessoas_origem = {a["pessoa"] for a in s["ativacoes_de_casas"]}
    assert pessoas_origem == {"Ana", "Bruno"}
    for at in s["ativacoes_de_casas"]:
        assert 1 <= at["cai_na_casa"] <= 12


def test_sintese_sinastria_conta_naturezas():
    s = calcular_sinastria(ANA, BRUNO)
    sintese = s["sintese_sinastria"]
    total = (
        sintese["aspectos_harmonicos"]
        + sintese["aspectos_tensao"]
        + sintese["aspectos_neutros"]
    )
    assert total == len(s["aspectos_sinastria"])


def test_sinastria_sem_horario_ainda_calcula_aspectos():
    sem_hora_a = {"data": "12/03/1990", "nome": "Ana", "lat": BH["lat"], "lng": BH["lng"], "tz_str": BH["tz_str"]}
    sem_hora_b = {"data": "25/07/1992", "nome": "Bruno", "lat": BH["lat"], "lng": BH["lng"], "tz_str": BH["tz_str"]}
    s = calcular_sinastria(sem_hora_a, sem_hora_b)
    assert len(s["aspectos_sinastria"]) > 0
    assert "ativacoes_de_casas" in s


def test_asc_omitido_quando_nao_ha_hora():
    """Sem hora, o cálculo cai num default de 12:00 que produz Asc arbitrário —
    o resumo deve omitir o asc (None) para sinalizar isso ao agente."""
    com_hora = {**ANA}
    sem_hora = {"data": "25/07/1992", "nome": "Bruno", "lat": BH["lat"], "lng": BH["lng"], "tz_str": BH["tz_str"]}
    s = calcular_sinastria(com_hora, sem_hora)
    assert s["pessoa_a"]["asc"] is not None  # Ana tem hora → asc presente
    assert s["pessoa_b"]["asc"] is None      # Bruno sem hora → asc omitido


def test_asc_presente_quando_ambos_tem_hora_e_local():
    s = calcular_sinastria(ANA, BRUNO)
    assert s["pessoa_a"]["asc"] is not None
    assert s["pessoa_b"]["asc"] is not None
