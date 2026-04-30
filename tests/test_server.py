"""
Testes do app Starlette: rotas HTTP públicas e middleware de auth.
Não exercita o handshake MCP (SSE) — isso requer cliente MCP de verdade.
"""
import importlib

import pytest
from starlette.testclient import TestClient


def _carregar_app(monkeypatch, api_key: str = ""):
    """Recarrega app.server com a env MCP_API_KEY desejada."""
    monkeypatch.setenv("MCP_API_KEY", api_key)
    from app import server as mod
    importlib.reload(mod)
    return mod


# ─────────────────────────────────────────────────────────────
# /health (público)
# ─────────────────────────────────────────────────────────────
def test_health_publico_sem_auth(monkeypatch):
    mod = _carregar_app(monkeypatch, api_key="segredo")
    client = TestClient(mod.app)
    resp = client.get("/health")
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "ok"
    assert body["service"] == "ceu-natal"
    assert body["transporte"] == "sse"
    assert body["auth_required"] is True


def test_health_sem_auth_quando_key_vazia(monkeypatch):
    mod = _carregar_app(monkeypatch, api_key="")
    client = TestClient(mod.app)
    body = client.get("/health").json()
    assert body["auth_required"] is False


# ─────────────────────────────────────────────────────────────
# /tools (protegido pelo middleware)
# ─────────────────────────────────────────────────────────────
def test_tools_lista_as_quatro_tools(monkeypatch):
    mod = _carregar_app(monkeypatch, api_key="")
    client = TestClient(mod.app)
    resp = client.get("/tools")
    assert resp.status_code == 200
    body = resp.json()
    assert body["count"] == 4
    nomes = {t["name"] for t in body["tools"]}
    assert nomes == {
        "calcular_mapa_natal", "calcular_sinastria",
        "listar_aspectos_tipos", "healthcheck",
    }


def test_tools_traz_required_e_properties(monkeypatch):
    mod = _carregar_app(monkeypatch, api_key="")
    body = TestClient(mod.app).get("/tools").json()
    mapa_natal = next(t for t in body["tools"] if t["name"] == "calcular_mapa_natal")
    assert "data" in mapa_natal["required"]
    assert set(mapa_natal["properties"]) == {"data", "hora", "local", "nome"}


def test_tools_exige_auth_quando_key_configurada(monkeypatch):
    mod = _carregar_app(monkeypatch, api_key="segredo")
    client = TestClient(mod.app)

    # Sem auth → 401
    assert client.get("/tools").status_code == 401

    # Com Bearer correto → 200
    resp = client.get("/tools", headers={"Authorization": "Bearer segredo"})
    assert resp.status_code == 200

    # Com query param correto → 200
    resp = client.get("/tools?api_key=segredo")
    assert resp.status_code == 200

    # Com Bearer errado → 401
    resp = client.get("/tools", headers={"Authorization": "Bearer outro"})
    assert resp.status_code == 401
