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
    assert body["transporte"] == "streamable-http+sse"
    assert body["auth_required"] is True


def test_health_sem_auth_quando_key_vazia(monkeypatch):
    mod = _carregar_app(monkeypatch, api_key="")
    client = TestClient(mod.app)
    body = client.get("/health").json()
    assert body["auth_required"] is False


def test_mcp_rota_registrada(monkeypatch):
    """Rota /mcp (Streamable HTTP) deve estar presente nas rotas da app."""
    mod = _carregar_app(monkeypatch, api_key="")
    caminhos = [getattr(r, "path", None) for r in mod.app.routes]
    assert "/mcp" in caminhos, f"Rota /mcp não encontrada; rotas: {caminhos}"


# ─────────────────────────────────────────────────────────────
# /tools (protegido pelo middleware)
# ─────────────────────────────────────────────────────────────
def test_tools_lista_as_sete_tools(monkeypatch):
    mod = _carregar_app(monkeypatch, api_key="")
    client = TestClient(mod.app)
    resp = client.get("/tools")
    assert resp.status_code == 200
    body = resp.json()
    assert body["count"] == 7
    nomes = {t["name"] for t in body["tools"]}
    assert nomes == {
        "calcular_mapa_natal", "calcular_sinastria",
        "calcular_transitos", "calcular_progressoes", "calcular_mapa_composto",
        "listar_aspectos_tipos", "healthcheck",
    }


def test_tools_traz_required_e_properties(monkeypatch):
    mod = _carregar_app(monkeypatch, api_key="")
    body = TestClient(mod.app).get("/tools").json()
    mapa_natal = next(t for t in body["tools"] if t["name"] == "calcular_mapa_natal")
    assert "data" in mapa_natal["required"]
    assert set(mapa_natal["properties"]) == {"data", "hora", "local", "nome", "sistema_casas"}


def test_tools_tem_annotations_read_only(monkeypatch):
    _carregar_app(monkeypatch, api_key="")
    import importlib
    import app.server as s
    importlib.reload(s)
    for tool in s.TOOLS:
        assert tool.annotations is not None, f"Tool '{tool.name}' sem annotations"
        assert tool.annotations.readOnlyHint is True, f"Tool '{tool.name}': readOnlyHint != True"
        assert tool.annotations.destructiveHint is False, f"Tool '{tool.name}': destructiveHint != False"


def test_tools_tem_output_schema(monkeypatch):
    _carregar_app(monkeypatch, api_key="")
    import importlib
    import app.server as s
    importlib.reload(s)
    for tool in s.TOOLS:
        assert tool.outputSchema is not None, f"Tool '{tool.name}' sem outputSchema"
        assert tool.outputSchema.get("type") == "object", (
            f"Tool '{tool.name}': outputSchema.type != 'object'"
        )


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


import asyncio
import json as _json


def test_dispatch_tool_desconhecida_levanta(monkeypatch):
    mod = _carregar_app(monkeypatch, api_key="")
    with pytest.raises(ValueError, match="Tool desconhecida"):
        mod._dispatch("nao_existe", {})


def test_call_tool_healthcheck_retorna_tupla_estruturada(monkeypatch):
    mod = _carregar_app(monkeypatch, api_key="")
    conteudo, estruturado = asyncio.run(mod._call_tool("healthcheck", {}))
    assert estruturado["status"] == "ok"
    # texto preserva acentos (ensure_ascii=False), não \uXXXX
    assert conteudo[0].text == _json.dumps(estruturado, ensure_ascii=False)


def test_call_tool_erro_marca_iserror_sem_vazar_detalhe(monkeypatch):
    mod = _carregar_app(monkeypatch, api_key="")

    def explode(name, arguments):
        raise RuntimeError("segredo interno: /etc/coisa")
    monkeypatch.setattr(mod, "_dispatch", explode)

    resultado = asyncio.run(mod._call_tool("calcular_mapa_natal", {"data": "01/01/2000"}))
    assert resultado.isError is True
    corpo = _json.loads(resultado.content[0].text)
    assert corpo["erro"] == "Erro interno do servidor."
    assert "detalhe" not in corpo
    assert "segredo interno" not in resultado.content[0].text


def test_call_tool_value_error_marca_iserror(monkeypatch):
    mod = _carregar_app(monkeypatch, api_key="")

    def explode(name, arguments):
        raise ValueError("data inválida")
    monkeypatch.setattr(mod, "_dispatch", explode)

    resultado = asyncio.run(mod._call_tool("calcular_mapa_natal", {"data": "x"}))
    assert resultado.isError is True
    assert _json.loads(resultado.content[0].text)["erro"] == "data inválida"


def test_call_tool_emite_telemetria(monkeypatch, caplog):
    mod = _carregar_app(monkeypatch, api_key="")
    with caplog.at_level("INFO", logger="ceu-natal"):
        asyncio.run(mod._call_tool("healthcheck", {}))
    eventos = []
    for rec in caplog.records:
        try:
            obj = _json.loads(rec.getMessage())
        except (ValueError, TypeError):
            continue
        if obj.get("event") == "tool_call":
            eventos.append(obj)
    assert eventos
    ev = eventos[-1]
    assert ev["tool"] == "healthcheck"
    assert ev["status"] == "ok"
    assert isinstance(ev["duration_ms"], (int, float))
