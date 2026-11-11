"""
Testes do app Starlette: rotas HTTP públicas e middleware de auth.
Não exercita o handshake MCP — isso requer cliente MCP de verdade.

Cada teste monta a própria aplicação com `create_app(Settings(...))`; nada
depende de variáveis de ambiente nem de recarregar o módulo.
"""
import asyncio
import json as _json
import subprocess
import sys
from pathlib import Path

import pytest
from starlette.testclient import TestClient

from app.config import Settings
from app.server import CODIGO_FONTE, INSTRUCOES, PROXIMO_PASSO, TOOLS, _dispatch, create_app

RAIZ = Path(__file__).resolve().parent.parent


def _app(**campos):
    """(app Starlette, Aplicacao) com as configurações pedidas."""
    app = create_app(Settings(**campos))
    return app, app.state.ceu


# ─────────────────────────────────────────────────────────────
# Settings
# ─────────────────────────────────────────────────────────────
def test_settings_do_ambiente_le_todas_as_variaveis(monkeypatch):
    env = {
        "MCP_SERVER_NAME": "outro",
        "MCP_SERVER_VERSION": "9.9.9",
        "MCP_API_KEY": "  segredo  ",
        "MCP_ALLOWED_HOSTS": "a.test, b.test,",
        "RATE_LIMIT_SESSION_PER_MIN": "7",
        "RATE_LIMIT_GLOBAL_PER_MIN": "70",
        "PUBLIC_SITE_URL": "https://site.test/",
        "PUBLIC_MCP_URL": "https://mcp.test/",
        "RATE_LIMIT_MAPA_RAPIDO_IP_PER_MIN": "3",
        "RATE_LIMIT_MAPA_RAPIDO_GLOBAL_PER_MIN": "30",
        "CORS_ORIGINS": "https://a.test/, https://b.test",
        "CONTATOS_PATH": " /dados/contatos.jsonl ",
    }
    for nome, valor in env.items():
        monkeypatch.setenv(nome, valor)
    assert Settings.do_ambiente() == Settings(
        server_name="outro",
        server_version="9.9.9",
        api_key="segredo",
        allowed_hosts=("a.test", "b.test"),
        rate_limit_session_per_min=7,
        rate_limit_global_per_min=70,
        public_site_url="https://site.test",
        public_mcp_url="https://mcp.test",
        rate_limit_mapa_rapido_ip_per_min=3,
        rate_limit_mapa_rapido_global_per_min=30,
        cors_origins=("https://a.test", "https://b.test"),
        contatos_path="/dados/contatos.jsonl",
    )


def test_settings_do_ambiente_vazio_usa_os_defaults(monkeypatch):
    for nome in ("MCP_SERVER_NAME", "MCP_SERVER_VERSION", "MCP_API_KEY", "MCP_ALLOWED_HOSTS",
                 "RATE_LIMIT_SESSION_PER_MIN", "RATE_LIMIT_GLOBAL_PER_MIN", "PUBLIC_SITE_URL",
                 "PUBLIC_MCP_URL", "RATE_LIMIT_MAPA_RAPIDO_IP_PER_MIN",
                 "RATE_LIMIT_MAPA_RAPIDO_GLOBAL_PER_MIN", "CORS_ORIGINS"):
        monkeypatch.delenv(nome, raising=False)
    s = Settings.do_ambiente()
    assert s == Settings()
    assert (s.server_name, s.server_version, s.api_key) == ("ceu-natal", "2.2.6", "")
    assert (s.rate_limit_session_per_min, s.rate_limit_global_per_min) == (30, 600)
    assert (s.rate_limit_mapa_rapido_ip_per_min, s.rate_limit_mapa_rapido_global_per_min) == (12, 120)
    assert s.public_site_url == "https://github.com/gucancado/ceu-natal"
    assert s.public_mcp_url == "https://astrologia-mcp.gustavocancado.com.br"
    assert s.cors_efetivos == (s.public_site_url,)


def test_create_app_sem_settings_le_o_ambiente(monkeypatch):
    monkeypatch.setenv("MCP_API_KEY", "do-ambiente")
    app = create_app()
    assert app.state.ceu.settings.api_key == "do-ambiente"


# ─────────────────────────────────────────────────────────────
# /health (público)
# ─────────────────────────────────────────────────────────────
def test_health_publico_sem_auth():
    app, ceu = _app(api_key="segredo")
    resp = TestClient(app).get("/health")
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "ok"
    assert body["service"] == "ceu-natal"
    assert body["transporte"] == "streamable-http"
    assert body["auth_required"] is True
    assert body["mapa_rapido"] == {
        "por_ip_por_min": ceu.settings.rate_limit_mapa_rapido_ip_per_min,
        "global_por_min": ceu.settings.rate_limit_mapa_rapido_global_per_min,
    }


def test_health_sem_auth_quando_key_vazia():
    app, _ = _app(api_key="")
    body = TestClient(app).get("/health").json()
    assert body["auth_required"] is False


def test_mcp_rota_registrada():
    """Rota /mcp (Streamable HTTP) deve estar presente nas rotas da app."""
    app, _ = _app()
    caminhos = [getattr(r, "path", None) for r in app.routes]
    assert "/mcp" in caminhos, f"Rota /mcp não encontrada; rotas: {caminhos}"


def test_modulo_expoe_app_para_o_uvicorn():
    from starlette.applications import Starlette

    import app.server as s
    assert isinstance(s.app, Starlette)
    assert s.app.state.ceu is not None


# ─────────────────────────────────────────────────────────────
# /tools (protegido pelo middleware)
# ─────────────────────────────────────────────────────────────
def test_tools_lista_as_nove_tools():
    app, _ = _app()
    resp = TestClient(app).get("/tools")
    assert resp.status_code == 200
    body = resp.json()
    assert body["count"] == 9
    nomes = {t["name"] for t in body["tools"]}
    assert nomes == {
        "calcular_mapa_natal", "calcular_sinastria",
        "calcular_transitos", "calcular_progressoes", "calcular_mapa_composto",
        "listar_aspectos_tipos", "healthcheck",
        "calcular_revolucao_solar", "calcular_revolucao_lunar",
    }


def test_tools_traz_required_e_properties():
    app, _ = _app()
    body = TestClient(app).get("/tools").json()
    mapa_natal = next(t for t in body["tools"] if t["name"] == "calcular_mapa_natal")
    assert "data" in mapa_natal["required"]
    assert set(mapa_natal["properties"]) == {"data", "hora", "local", "nome", "sistema_casas", "is_dst"}


def test_tools_tem_annotations_read_only():
    for tool in TOOLS:
        assert tool.annotations is not None, f"Tool '{tool.name}' sem annotations"
        assert tool.annotations.readOnlyHint is True, f"Tool '{tool.name}': readOnlyHint != True"
        assert tool.annotations.destructiveHint is False, f"Tool '{tool.name}': destructiveHint != False"


def test_tools_tem_output_schema():
    # outputSchema estrito só nas tools triviais e estáveis. Os 5 cálculos
    # NÃO declaram outputSchema: o retorno é profundamente aninhado e tem
    # campos nuláveis (nome/casas=None sem hora/local) que um schema rígido
    # rejeitaria no validador do SDK, quebrando a tool. Decisão deliberada.
    com_schema = {"healthcheck", "listar_aspectos_tipos"}
    for tool in TOOLS:
        if tool.name in com_schema:
            assert tool.outputSchema is not None, f"Tool '{tool.name}' devia ter outputSchema"
            assert tool.outputSchema.get("type") == "object"
        else:
            assert tool.outputSchema is None, (
                f"Tool de cálculo '{tool.name}' não deve ter outputSchema (campos nuláveis)"
            )


def test_schema_da_pessoa_igual_em_todas_as_tools():
    """Objeto pessoa/natal: mesmos campos em todas as tools que o recebem."""
    campos = {"data", "hora", "local", "nome", "is_dst"}
    vistos = 0
    for tool in TOOLS:
        for nome in ("pessoa_a", "pessoa_b", "natal"):
            prop = tool.inputSchema["properties"].get(nome)
            if prop is None:
                continue
            vistos += 1
            assert prop["required"] == ["data"]
            assert set(prop["properties"]) == campos
            assert prop["properties"]["is_dst"]["type"] == ["boolean", "null"]
    assert vistos == 8  # sinastria 2, composto 2, trânsitos, progressões, 2 revoluções


def test_tools_exige_auth_quando_key_configurada():
    app, _ = _app(api_key="segredo")
    client = TestClient(app)

    # Sem auth → 401
    assert client.get("/tools").status_code == 401

    # Com Bearer correto → 200
    resp = client.get("/tools", headers={"Authorization": "Bearer segredo"})
    assert resp.status_code == 200

    # Query param não autentica mais (vazava a chave em logs de proxy) → 401
    resp = client.get("/tools?api_key=segredo")
    assert resp.status_code == 401

    # Com Bearer errado → 401
    resp = client.get("/tools", headers={"Authorization": "Bearer outro"})
    assert resp.status_code == 401


# ─────────────────────────────────────────────────────────────
# Registro e despacho
# ─────────────────────────────────────────────────────────────
def test_dispatch_tool_desconhecida_levanta():
    with pytest.raises(ValueError, match="Tool desconhecida"):
        _dispatch("nao_existe", {})


def test_registro_cobre_todas_as_tools():
    _, ceu = _app()
    assert set(ceu.registro) == {t.name for t in TOOLS}


def test_schemas_de_pessoa_nao_sao_compartilhados_entre_tools():
    """Mutar o schema de uma tool não pode vazar para outra."""
    por_nome = {t.name: t for t in TOOLS}
    pares = [
        (por_nome["calcular_sinastria"].inputSchema["properties"]["pessoa_a"],
         por_nome["calcular_mapa_composto"].inputSchema["properties"]["pessoa_a"]),
        (por_nome["calcular_sinastria"].inputSchema["properties"]["pessoa_a"],
         por_nome["calcular_sinastria"].inputSchema["properties"]["pessoa_b"]),
        (por_nome["calcular_transitos"].inputSchema["properties"]["natal"],
         por_nome["calcular_progressoes"].inputSchema["properties"]["natal"]),
        (por_nome["calcular_revolucao_solar"].inputSchema["properties"]["natal"],
         por_nome["calcular_revolucao_lunar"].inputSchema["properties"]["natal"]),
    ]
    for um, outro in pares:
        assert um == outro
        um["properties"]["data"]["x-teste"] = True
        try:
            assert "x-teste" not in outro["properties"]["data"]
        finally:
            del um["properties"]["data"]["x-teste"]


def test_dispatch_listar_aspectos_tipos():
    resultado = _dispatch("listar_aspectos_tipos", {})
    assert {a["tipo"] for a in resultado["aspectos"]} >= {"conjuncao", "oposicao"}


def test_healthcheck_traz_a_versao_configurada():
    _, ceu = _app(server_version="7.7.7")
    assert ceu.dispatch("healthcheck", {}) == {
        "status": "ok", "versao": "7.7.7", "transporte": "streamable-http",
        "proximo_passo": PROXIMO_PASSO, "codigo_fonte": CODIGO_FONTE,
    }


def test_conectar_leva_ao_mapa_da_pessoa():
    _, ceu = _app()
    assert "data, hora e cidade" in PROXIMO_PASSO
    assert ceu.server.instructions == INSTRUCOES
    assert "DD/MM/AAAA" in ceu.server.instructions


def test_toda_tool_tem_titulo_e_anotacao_de_leitura():
    for t in TOOLS:
        assert t.title, t.name
        assert t.annotations.title == t.title, t.name
        assert t.annotations.readOnlyHint is True, t.name
        assert len(t.name) <= 64, t.name


def test_desafio_openai_404_sem_token():
    app, _ = _app()
    assert TestClient(app).get("/.well-known/openai-apps-challenge").status_code == 404


def test_desafio_openai_devolve_so_o_token_mesmo_com_chave_configurada():
    app, _ = _app(openai_apps_challenge="tok-123", api_key="segredo")
    r = TestClient(app).get("/.well-known/openai-apps-challenge")
    assert r.status_code == 200
    assert r.text == "tok-123"
    assert r.headers["content-type"].startswith("text/plain")


def test_call_tool_healthcheck_retorna_tupla_estruturada():
    _, ceu = _app()
    conteudo, estruturado = asyncio.run(ceu.call_tool("healthcheck", {}))
    assert estruturado["status"] == "ok"
    # texto preserva acentos (ensure_ascii=False), não \uXXXX
    assert conteudo[0].text == _json.dumps(estruturado, ensure_ascii=False)


def test_call_tool_erro_marca_iserror_sem_vazar_detalhe(monkeypatch):
    _, ceu = _app()

    def explode(name, arguments):
        raise RuntimeError("segredo interno: /etc/coisa")
    monkeypatch.setattr(ceu, "dispatch", explode)

    resultado = asyncio.run(ceu.call_tool("calcular_mapa_natal", {"data": "01/01/2000"}))
    assert resultado.isError is True
    corpo = _json.loads(resultado.content[0].text)
    assert corpo["erro"] == "Erro interno do servidor."
    assert "detalhe" not in corpo
    assert "segredo interno" not in resultado.content[0].text


def test_call_tool_value_error_marca_iserror(monkeypatch):
    _, ceu = _app()

    def explode(name, arguments):
        raise ValueError("data inválida")
    monkeypatch.setattr(ceu, "dispatch", explode)

    resultado = asyncio.run(ceu.call_tool("calcular_mapa_natal", {"data": "x"}))
    assert resultado.isError is True
    assert _json.loads(resultado.content[0].text)["erro"] == "data inválida"


def test_call_tool_emite_telemetria(caplog):
    _, ceu = _app()
    with caplog.at_level("INFO", logger="ceu-natal"):
        asyncio.run(ceu.call_tool("healthcheck", {}))
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


def test_server_importa_sem_kerykeion():
    """`sys.modules['kerykeion'] = None` faz qualquer `import kerykeion` falhar."""
    codigo = "import sys; sys.modules['kerykeion'] = None; import app.server; print('ok')"
    r = subprocess.run([sys.executable, "-c", codigo], capture_output=True, text=True, cwd=RAIZ)
    assert r.returncode == 0 and r.stdout.strip() == "ok", r.stderr


# ─────────────────────────────────────────────────────────────
# Limite de taxa no call_tool
# ─────────────────────────────────────────────────────────────
def test_chave_sessao_fora_de_request_eh_none():
    _, ceu = _app()
    assert ceu.chave_sessao() is None


def test_call_tool_barra_pela_sessao_com_iserror(monkeypatch, caplog):
    _, ceu = _app(rate_limit_session_per_min=2, rate_limit_global_per_min=0)
    monkeypatch.setattr(ceu, "chave_sessao", lambda: "sessao-1")
    with caplog.at_level("INFO", logger="ceu-natal"):
        asyncio.run(ceu.call_tool("healthcheck", {}))
        asyncio.run(ceu.call_tool("healthcheck", {}))
        terceiro = asyncio.run(ceu.call_tool("healthcheck", {}))
    assert terceiro.isError is True
    assert _json.loads(terceiro.content[0].text)["erro"].startswith("Limite de chamadas atingido. Aguarde ")
    ultimo = [_json.loads(r.getMessage()) for r in caplog.records if r.getMessage().startswith("{")][-1]
    assert ultimo["status"] == "rate_limited"


def test_sem_sessao_conta_so_no_global():
    _, ceu = _app(rate_limit_session_per_min=1, rate_limit_global_per_min=3)
    resultados = [asyncio.run(ceu.call_tool("healthcheck", {})) for _ in range(4)]
    assert [isinstance(r, tuple) for r in resultados] == [True, True, True, False]


def test_cada_app_tem_o_proprio_limitador():
    _, ceu = _app(rate_limit_session_per_min=0, rate_limit_global_per_min=1)
    asyncio.run(ceu.call_tool("healthcheck", {}))
    _, outro = _app(rate_limit_session_per_min=0, rate_limit_global_per_min=1)
    assert isinstance(asyncio.run(outro.call_tool("healthcheck", {})), tuple)


def test_health_expoe_limites():
    app, _ = _app(rate_limit_session_per_min=30, rate_limit_global_per_min=600)
    body = TestClient(app).get("/health").json()
    assert body["limites"] == {"por_sessao_por_min": 30, "global_por_min": 600}


# ─────────────────────────────────────────────────────────────
# /llms.txt e / (públicos)
# ─────────────────────────────────────────────────────────────
def test_llms_txt_publico_utf8_e_com_urls():
    app, _ = _app(
        api_key="segredo",
        public_mcp_url="https://mcp.exemplo.test/",
        public_site_url="https://site.exemplo.test",
    )
    resp = TestClient(app).get("/llms.txt")
    assert resp.status_code == 200
    assert resp.headers["content-type"].startswith("text/plain") and "charset=utf-8" in resp.headers["content-type"]
    assert resp.text.startswith("# Céu Natal")
    assert "https://mcp.exemplo.test/mcp/" in resp.text and "https://mcp.exemplo.test//" not in resp.text
    assert "https://site.exemplo.test" in resp.text
    assert "calcular_revolucao_lunar" in resp.text and "trânsitos" in resp.text


def test_raiz_redireciona_para_o_site_default():
    app, _ = _app(api_key="segredo")
    resp = TestClient(app).get("/", follow_redirects=False)
    assert resp.status_code == 302
    assert resp.headers["location"] == "https://github.com/gucancado/ceu-natal"
