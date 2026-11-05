from app.core.sintese import calcular_sintese


def test_sem_casas_hemisferios_sao_none():
    s = calcular_sintese({}, [])
    assert s["hemisferio_vertical"] is None
    assert s["hemisferio_horizontal"] is None


def test_planetas_sem_casa_hemisferios_sao_none():
    s = calcular_sintese({"sol": {"signo": "Peixes"}, "lua": {"signo": "Áries"}}, [])
    assert s["hemisferio_vertical"] is None
    assert s["hemisferio_horizontal"] is None


def test_empate_vira_equilibrado():
    # casa 1: norte e leste; casa 7: sul e oeste
    s = calcular_sintese({"sol": {"casa": 1}, "lua": {"casa": 7}}, [])
    assert s["hemisferio_vertical"] == "equilibrado"
    assert s["hemisferio_horizontal"] == "equilibrado"


def test_maioria_define_hemisferio():
    s = calcular_sintese({"sol": {"casa": 1}, "lua": {"casa": 2}, "marte": {"casa": 8}}, [])
    assert s["hemisferio_vertical"] == "Norte"
    assert s["hemisferio_horizontal"] == "Leste"
    s = calcular_sintese({"sol": {"casa": 7}, "lua": {"casa": 8}, "marte": {"casa": 2}}, [])
    assert s["hemisferio_vertical"] == "Sul"
    assert s["hemisferio_horizontal"] == "Oeste"
