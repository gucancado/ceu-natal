"""Endpoint público /mapa-rapido (formulário do site)."""
import importlib

from starlette.testclient import TestClient

SITE = "https://mistico.exemplo.com"


def _app(monkeypatch, api_key="", por_ip="6"):
    monkeypatch.setenv("MCP_API_KEY", api_key)
    monkeypatch.setenv("PUBLIC_SITE_URL", SITE)
    monkeypatch.delenv("CORS_ORIGINS", raising=False)
    monkeypatch.setenv("RATE_LIMIT_MAPA_RAPIDO_IP_PER_MIN", por_ip)
    from app import server as mod
    importlib.reload(mod)
    chamadas = []

    def falso(nome, argumentos):
        chamadas.append((nome, argumentos))
        if argumentos.get("data") == "99/99/9999":
            raise ValueError("Data inválida.")
        return {"nascimento": argumentos, "planetas": {}}

    monkeypatch.setattr(mod, "_dispatch", falso)
    return mod, TestClient(mod.app), chamadas


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


def test_erros_de_entrada(monkeypatch):
    _, client, _ = _app(monkeypatch)
    assert client.post("/mapa-rapido", content=b"nao-json").status_code == 400
    assert client.post("/mapa-rapido", json={"hora": "10:00"}).status_code == 400
    assert client.post("/mapa-rapido", json={"data": "15/05/1990", "local": "x" * 121}).status_code == 400
    r = client.post("/mapa-rapido", json={"data": "99/99/9999"})
    assert r.status_code == 400 and r.json()["erro"] == "Data inválida."


def test_limite_por_ip(monkeypatch):
    _, client, _ = _app(monkeypatch, por_ip="2")
    h = {"X-Forwarded-For": "203.0.113.7, 10.0.0.1"}
    assert client.post("/mapa-rapido", json={"data": "15/05/1990"}, headers=h).status_code == 200
    assert client.post("/mapa-rapido", json={"data": "15/05/1990"}, headers=h).status_code == 200
    bloqueado = client.post("/mapa-rapido", json={"data": "15/05/1990"}, headers=h)
    assert bloqueado.status_code == 429 and "retry-after" in bloqueado.headers
    outro = client.post("/mapa-rapido", json={"data": "15/05/1990"}, headers={"X-Forwarded-For": "198.51.100.2"})
    assert outro.status_code == 200
