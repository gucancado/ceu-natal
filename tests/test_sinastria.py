from app.tools.sinastria import calcular_sinastria
from tests.conftest import BH


GUSTAVO = {
    "data": "24/07/1989", "hora": "09:20", "local": "Belo Horizonte, MG", "nome": "Gustavo",
    "lat": BH["lat"], "lng": BH["lng"], "tz_str": BH["tz_str"],
}
NAIARA = {
    "data": "09/06/1989", "hora": "14:05", "local": "Belo Horizonte, MG", "nome": "Naiara",
    "lat": BH["lat"], "lng": BH["lng"], "tz_str": BH["tz_str"],
}


def test_sinastria_retorna_estrutura_completa():
    s = calcular_sinastria(GUSTAVO, NAIARA)
    assert s["pessoa_a"]["nome"] == "Gustavo"
    assert s["pessoa_b"]["nome"] == "Naiara"
    assert isinstance(s["aspectos_sinastria"], list) and len(s["aspectos_sinastria"]) > 0
    assert isinstance(s["ativacoes_de_casas"], list) and len(s["ativacoes_de_casas"]) > 0
    assert "sintese_sinastria" in s


def test_aspectos_bidirecionais_planeta_de_a_vs_b():
    s = calcular_sinastria(GUSTAVO, NAIARA)
    # Cada aspecto deve ter pessoa_a e pessoa_b distintos
    for a in s["aspectos_sinastria"]:
        assert a["pessoa_a"] == "Gustavo"
        assert a["pessoa_b"] == "Naiara"
        assert a["natureza"] in ("harmonico", "tensao", "neutro")


def test_ativacoes_bidirecionais():
    """Planetas de A caem em casas de B e planetas de B caem em casas de A."""
    s = calcular_sinastria(GUSTAVO, NAIARA)
    pessoas_origem = {a["pessoa"] for a in s["ativacoes_de_casas"]}
    assert pessoas_origem == {"Gustavo", "Naiara"}
    for at in s["ativacoes_de_casas"]:
        assert 1 <= at["cai_na_casa"] <= 12


def test_sintese_sinastria_conta_naturezas():
    s = calcular_sinastria(GUSTAVO, NAIARA)
    sintese = s["sintese_sinastria"]
    total = (
        sintese["aspectos_harmonicos"]
        + sintese["aspectos_tensao"]
        + sintese["aspectos_neutros"]
    )
    assert total == len(s["aspectos_sinastria"])


def test_sinastria_sem_horario_ainda_calcula_aspectos():
    sem_hora_a = {"data": "24/07/1989", "nome": "G", "lat": BH["lat"], "lng": BH["lng"], "tz_str": BH["tz_str"]}
    sem_hora_b = {"data": "09/06/1989", "nome": "N", "lat": BH["lat"], "lng": BH["lng"], "tz_str": BH["tz_str"]}
    s = calcular_sinastria(sem_hora_a, sem_hora_b)
    assert len(s["aspectos_sinastria"]) > 0
    assert "ativacoes_de_casas" in s


def test_asc_omitido_quando_nao_ha_hora():
    """Sem hora, o cálculo cai num default de 12:00 que produz Asc arbitrário —
    o resumo deve omitir o asc (None) para sinalizar isso ao agente."""
    com_hora = {**GUSTAVO}
    sem_hora = {"data": "09/06/1989", "nome": "Nai", "lat": BH["lat"], "lng": BH["lng"], "tz_str": BH["tz_str"]}
    s = calcular_sinastria(com_hora, sem_hora)
    assert s["pessoa_a"]["asc"] is not None  # Gustavo tem hora → asc presente
    assert s["pessoa_b"]["asc"] is None      # Nai sem hora → asc omitido


def test_asc_presente_quando_ambos_tem_hora_e_local():
    s = calcular_sinastria(GUSTAVO, NAIARA)
    assert s["pessoa_a"]["asc"] is not None
    assert s["pessoa_b"]["asc"] is not None
