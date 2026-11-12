"""Endpoint público /mapa-rapido (formulário do site)."""
from starlette.testclient import TestClient

from app.config import Settings
from app.server import MAPA_RAPIDO_BODY_MAX, create_app

SITE = "https://mistico.exemplo.com"


def _app(monkeypatch, api_key="", por_ip=6):
    app = create_app(Settings(
        api_key=api_key, public_site_url=SITE, rate_limit_mapa_rapido_ip_per_min=por_ip,
    ))
    ceu = app.state.ceu
    chamadas = []

    def falso(nome, argumentos):
        chamadas.append((nome, argumentos))
        if argumentos.get("data") == "99/99/9999":
            raise ValueError("Data inválida.")
        return {"nascimento": argumentos, "planetas": {}}

    monkeypatch.setattr(ceu, "dispatch", falso)
    return ceu, TestClient(app), chamadas


def test_calcula_sem_chave_mesmo_com_api_key(monkeypatch):
    _, client, chamadas = _app(monkeypatch, api_key="segredo")
    r = client.post("/mapa-rapido", json={"data": "15/05/1990", "hora": "14:30", "local": "Belo Horizonte, MG"},
                    headers={"Origin": SITE})
    assert r.status_code == 200
    assert r.headers["access-control-allow-origin"] == SITE
    assert chamadas == [("calcular_mapa_natal", {"data": "15/05/1990", "hora": "14:30", "local": "Belo Horizonte, MG"})]


def test_campos_vazios_sao_omitidos_e_extras_ignorados(monkeypatch):
    _, client, chamadas = _app(monkeypatch)
    r = client.post("/mapa-rapido", json={"data": "15/05/1990", "hora": "", "local": None, "nome": "x"})
    assert r.status_code == 200
    assert chamadas[0][1] == {"data": "15/05/1990"}


def test_preflight_so_para_o_site(monkeypatch):
    _, client, _ = _app(monkeypatch)
    ok = client.options("/mapa-rapido", headers={"Origin": SITE, "Access-Control-Request-Method": "POST"})
    assert ok.status_code == 204
    assert ok.headers["access-control-allow-origin"] == SITE
    fora = client.options("/mapa-rapido", headers={"Origin": "https://malicioso.com"})
    assert "access-control-allow-origin" not in fora.headers


def test_cors_origins_configuradas_substituem_o_site(monkeypatch):
    app = create_app(Settings(public_site_url=SITE, cors_origins=("https://outro.exemplo.com/",)))
    client = TestClient(app)
    ok = client.options("/mapa-rapido", headers={"Origin": "https://outro.exemplo.com"})
    assert ok.headers["access-control-allow-origin"] == "https://outro.exemplo.com"
    assert "access-control-allow-origin" not in client.options("/mapa-rapido", headers={"Origin": SITE}).headers


def test_erros_de_entrada(monkeypatch):
    _, client, _ = _app(monkeypatch)
    assert client.post("/mapa-rapido", content=b"nao-json").status_code == 400
    assert client.post("/mapa-rapido", json={"hora": "10:00"}).status_code == 400
    assert client.post("/mapa-rapido", json={"data": "15/05/1990", "local": "x" * 121}).status_code == 400
    r = client.post("/mapa-rapido", json={"data": "99/99/9999"})
    assert r.status_code == 400 and r.json()["erro"] == "Data inválida."


def test_limite_por_ip(monkeypatch):
    _, client, _ = _app(monkeypatch, por_ip=2)
    h = {"X-Forwarded-For": "203.0.113.7, 10.0.0.1"}
    assert client.post("/mapa-rapido", json={"data": "15/05/1990"}, headers=h).status_code == 200
    assert client.post("/mapa-rapido", json={"data": "15/05/1990"}, headers=h).status_code == 200
    bloqueado = client.post("/mapa-rapido", json={"data": "15/05/1990"}, headers=h)
    assert bloqueado.status_code == 429 and "retry-after" in bloqueado.headers
    outro = client.post("/mapa-rapido", json={"data": "15/05/1990"}, headers={"X-Forwarded-For": "198.51.100.2"})
    assert outro.status_code == 200


def test_xff_forjado_nao_escapa_do_limite(monkeypatch):
    """O cliente controla o início do X-Forwarded-For; vale o último item (o que o proxy viu)."""
    _, client, _ = _app(monkeypatch, por_ip=2)
    corpo = {"data": "15/05/1990"}
    assert client.post("/mapa-rapido", json=corpo, headers={"X-Forwarded-For": "1.1.1.1, 9.9.9.9"}).status_code == 200
    assert client.post("/mapa-rapido", json=corpo, headers={"X-Forwarded-For": "2.2.2.2, 9.9.9.9"}).status_code == 200
    bloqueado = client.post("/mapa-rapido", json=corpo, headers={"X-Forwarded-For": "3.3.3.3, 9.9.9.9"})
    assert bloqueado.status_code == 429


def test_corpo_grande_demais(monkeypatch):
    _, client, chamadas = _app(monkeypatch)
    r = client.post("/mapa-rapido", content=b"x" * 5000,
                    headers={"Content-Length": "5000", "Content-Type": "application/json", "Origin": SITE})
    assert r.status_code == 413
    assert r.json() == {"erro": "Corpo grande demais."}
    assert r.headers["access-control-allow-origin"] == SITE
    assert chamadas == []


def test_corpo_grande_demais_sem_content_length(monkeypatch):
    """Upload chunked (gerador): sem Content-Length, o teto vale no corpo lido."""
    _, client, chamadas = _app(monkeypatch)
    enviados = []

    def pedacos():
        for _ in range(5):
            enviados.append(1)
            yield b"x" * 1000

    r = client.post("/mapa-rapido", content=pedacos(),
                    headers={"Content-Type": "application/json", "Origin": SITE})
    assert "content-length" not in r.request.headers
    assert enviados, "o gerador devia ter sido consumido"
    assert 5 * 1000 > MAPA_RAPIDO_BODY_MAX
    assert r.status_code == 413
    assert r.json() == {"erro": "Corpo grande demais."}
    assert chamadas == []


def test_transitos_usa_o_nascimento_e_a_data_do_transito(monkeypatch):
    _, client, chamadas = _app(monkeypatch)
    r = client.post("/mapa-rapido", json={
        "tecnica": "transitos", "data": "15/05/1990", "hora": "14:30", "local": "Belo Horizonte, MG",
        "data_transito": "12/11/2026",
    })
    assert r.status_code == 200
    assert chamadas == [("calcular_transitos", {
        "natal": {"data": "15/05/1990", "hora": "14:30", "local": "Belo Horizonte, MG"},
        "data_transito": "12/11/2026",
    })]
    assert client.post("/mapa-rapido", json={"tecnica": "transitos", "data": "15/05/1990"}).status_code == 400


def test_sinastria_guarda_so_quem_preenche(monkeypatch):
    ceu, client, chamadas = _app(monkeypatch)
    guardados = []
    monkeypatch.setattr(ceu, "guardar_mapa_site", lambda corpo, natal, resultado: guardados.append(natal))
    r = client.post("/mapa-rapido", json={
        "tecnica": "sinastria", "data": "15/05/1990",
        "outra": {"data": "25/07/1992", "hora": "09:15", "local": "São Paulo, SP"},
    })
    assert r.status_code == 200
    assert chamadas == [("calcular_sinastria", {
        "pessoa_a": {"data": "15/05/1990", "nome": "pessoa 1"},
        "pessoa_b": {"data": "25/07/1992", "hora": "09:15", "local": "São Paulo, SP", "nome": "pessoa 2"},
    })]
    assert guardados == [{"data": "15/05/1990"}]
    assert client.post("/mapa-rapido", json={"tecnica": "sinastria", "data": "15/05/1990"}).status_code == 400


def test_revolucao_solar_exige_hora_e_local_e_usa_a_cidade_natal_por_padrao(monkeypatch):
    _, client, chamadas = _app(monkeypatch)
    natal = {"data": "15/05/1990", "hora": "14:30", "local": "Belo Horizonte, MG"}
    r = client.post("/mapa-rapido", json={"tecnica": "revolucao_solar", **natal, "ano": "2026"})
    assert r.status_code == 200
    esperado = {"natal": natal, "ano": 2026, "local_revolucao": "Belo Horizonte, MG"}
    assert chamadas == [("calcular_revolucao_solar", esperado)]
    sem_hora = {"tecnica": "revolucao_solar", "data": "15/05/1990", "local": "Belo Horizonte, MG", "ano": 2026}
    assert client.post("/mapa-rapido", json=sem_hora).status_code == 400
    assert client.post("/mapa-rapido", json={"tecnica": "revolucao_solar", **natal, "ano": "x"}).status_code == 400


def test_tecnica_desconhecida(monkeypatch):
    _, client, _ = _app(monkeypatch)
    r = client.post("/mapa-rapido", json={"tecnica": "tarot", "data": "15/05/1990"})
    assert r.status_code == 400 and r.json()["erro"] == "Técnica inválida."
