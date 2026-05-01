"""
Servidor MCP do céu-natal: expõe tools de astrologia via SSE sobre HTTP.

Endpoints:
  GET  /sse        — abre o canal SSE (handshake MCP)
  POST /messages/  — recebe as mensagens do cliente MCP
  GET  /health     — healthcheck público (sem auth)

Autenticação: header `Authorization: Bearer <key>` ou query `?api_key=<key>`.
Se MCP_API_KEY não estiver configurado, libera tudo (modo dev).
"""
import json
import logging
import os
from typing import Any

from mcp.server import Server
from mcp.server.sse import SseServerTransport
from mcp.types import Tool, TextContent

from starlette.applications import Starlette
from starlette.middleware import Middleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response
from starlette.routing import Mount, Route

from app.core.aspectos import listar_tipos_aspectos
from app.core.geocoder import GeocodingError
from app.tools.composto import calcular_mapa_composto
from app.tools.mapa_natal import calcular_mapa_natal
from app.tools.progressoes import calcular_progressoes
from app.tools.sinastria import calcular_sinastria
from app.tools.transitos import calcular_transitos

SERVER_NAME = os.getenv("MCP_SERVER_NAME", "ceu-natal")
SERVER_VERSION = os.getenv("MCP_SERVER_VERSION", "2.0.0")
API_KEY = os.getenv("MCP_API_KEY", "").strip()

logger = logging.getLogger("ceu-natal")
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")


# ─────────────────────────────────────────────────────────────
# Definição das tools (schemas em JSON Schema padrão MCP)
# ─────────────────────────────────────────────────────────────
TOOLS: list[Tool] = [
    Tool(
        name="calcular_mapa_natal",
        description=(
            "Calcula o mapa astral natal completo de uma pessoa. Retorna posições "
            "planetárias, casas (Placidus por padrão; sistema configurável), ângulos, "
            "aspectos entre planetas, pontos sensíveis (nodos verdadeiros e Quíron) e "
            "síntese (elementos, qualidades, hemisférios, stelliums). Se hora ou local "
            "forem omitidos, retorna apenas posições por signo, sem casas nem ângulos."
        ),
        inputSchema={
            "type": "object",
            "required": ["data"],
            "properties": {
                "data": {
                    "type": "string",
                    "description": "Data de nascimento no formato DD/MM/YYYY.",
                },
                "hora": {
                    "type": ["string", "null"],
                    "description": "Hora de nascimento no formato HH:MM. Opcional.",
                },
                "local": {
                    "type": ["string", "null"],
                    "description": "Cidade e UF/país (ex: 'Belo Horizonte, MG'). Opcional.",
                },
                "nome": {
                    "type": ["string", "null"],
                    "description": "Nome da pessoa (apenas para identificação). Opcional.",
                },
                "sistema_casas": {
                    "type": ["string", "null"],
                    "description": (
                        "Sistema de casas: P (Placidus, default), K (Koch), W (Whole "
                        "Sign), E (Equal), R (Regiomontanus), C (Campanus), O "
                        "(Porphyrius), B (Alcabitus), M (Morinus), T (Topocentric)."
                    ),
                },
            },
        },
    ),
    Tool(
        name="calcular_sinastria",
        description=(
            "Calcula a sinastria entre duas pessoas: aspectos cruzados (planetas "
            "de A vs planetas de B), em quais casas do mapa de uma cada planeta "
            "da outra cai, e síntese com contagem de aspectos harmônicos / tensão / "
            "neutros. Útil para análise de relacionamento."
        ),
        inputSchema={
            "type": "object",
            "required": ["pessoa_a", "pessoa_b"],
            "properties": {
                "pessoa_a": {
                    "type": "object",
                    "required": ["data"],
                    "properties": {
                        "data":  {"type": "string"},
                        "hora":  {"type": ["string", "null"]},
                        "local": {"type": ["string", "null"]},
                        "nome":  {"type": ["string", "null"]},
                    },
                },
                "pessoa_b": {
                    "type": "object",
                    "required": ["data"],
                    "properties": {
                        "data":  {"type": "string"},
                        "hora":  {"type": ["string", "null"]},
                        "local": {"type": ["string", "null"]},
                        "nome":  {"type": ["string", "null"]},
                    },
                },
                "sistema_casas": {
                    "type": ["string", "null"],
                    "description": (
                        "Sistema de casas usado nos dois mapas. Default Placidus. "
                        "Identificadores: P, K, W, E, R, C, O, B, M, T."
                    ),
                },
            },
        },
    ),
    Tool(
        name="calcular_transitos",
        description=(
            "Calcula os trânsitos planetários para uma data específica em relação "
            "a um mapa natal. Retorna a posição atual dos planetas, aspectos entre "
            "planetas em trânsito e planetas natais (com aplicando/separando), em "
            "qual casa natal cada planeta em trânsito está caindo, e síntese com "
            "destaque para trânsitos de planetas lentos (Saturno, Urano, Netuno, "
            "Plutão e Quíron) com orbe < 2°."
        ),
        inputSchema={
            "type": "object",
            "required": ["natal", "data_transito"],
            "properties": {
                "natal": {
                    "type": "object",
                    "required": ["data"],
                    "properties": {
                        "data":  {"type": "string"},
                        "hora":  {"type": ["string", "null"]},
                        "local": {"type": ["string", "null"]},
                        "nome":  {"type": ["string", "null"]},
                    },
                },
                "data_transito": {
                    "type": "string",
                    "description": "Data do trânsito no formato DD/MM/YYYY.",
                },
                "hora_transito": {
                    "type": ["string", "null"],
                    "description": "Hora HH:MM. Default 12:00 UTC se omitida.",
                },
                "local_transito": {
                    "type": ["string", "null"],
                    "description": "Local de observação. Default Greenwich/UTC.",
                },
                "sistema_casas": {"type": ["string", "null"]},
            },
        },
    ),
    Tool(
        name="calcular_progressoes",
        description=(
            "Calcula as progressões secundárias (técnica 'um dia = um ano') de um "
            "mapa natal para uma data alvo. Retorna posições progredidas, aspectos "
            "entre planetas progredidos e natais, destaque para Lua progredida (fase "
            "emocional atual, ~2.5 anos por signo), Sol progredido (capítulo de vida, "
            "~30 anos por signo), e sinaliza ingressos recentes e mudanças iminentes "
            "de signo."
        ),
        inputSchema={
            "type": "object",
            "required": ["natal", "data_alvo"],
            "properties": {
                "natal": {
                    "type": "object",
                    "required": ["data"],
                    "properties": {
                        "data":  {"type": "string"},
                        "hora":  {"type": ["string", "null"]},
                        "local": {"type": ["string", "null"]},
                        "nome":  {"type": ["string", "null"]},
                    },
                },
                "data_alvo": {
                    "type": "string",
                    "description": "Data alvo (presente/futuro) no formato DD/MM/YYYY.",
                },
                "sistema_casas": {"type": ["string", "null"]},
            },
        },
    ),
    Tool(
        name="calcular_mapa_composto",
        description=(
            "Calcula o mapa composto (composite chart) de duas pessoas pelo método "
            "de midpoints — o mapa da 'relação como entidade'. Diferente da sinastria, "
            "que compara dois mapas, o composto cria um terceiro mapa a partir dos "
            "pontos médios das longitudes planetárias. Retorna posições compostas, "
            "ângulos (ASC e MC compostos quando ambas as pessoas têm hora+local), "
            "aspectos internos do composto e síntese de elementos. Não retorna casas "
            "— composto por midpoint não tem instante/local definidos."
        ),
        inputSchema={
            "type": "object",
            "required": ["pessoa_a", "pessoa_b"],
            "properties": {
                "pessoa_a": {
                    "type": "object",
                    "required": ["data"],
                    "properties": {
                        "data":  {"type": "string"},
                        "hora":  {"type": ["string", "null"]},
                        "local": {"type": ["string", "null"]},
                        "nome":  {"type": ["string", "null"]},
                    },
                },
                "pessoa_b": {
                    "type": "object",
                    "required": ["data"],
                    "properties": {
                        "data":  {"type": "string"},
                        "hora":  {"type": ["string", "null"]},
                        "local": {"type": ["string", "null"]},
                        "nome":  {"type": ["string", "null"]},
                    },
                },
                "sistema_casas": {"type": ["string", "null"]},
            },
        },
    ),
    Tool(
        name="listar_aspectos_tipos",
        description=(
            "Retorna os tipos de aspectos suportados pelo servidor com seus "
            "ângulos, orbes padrão (e orbes ampliados quando há luminar), e "
            "natureza (harmônico, tensão ou neutro)."
        ),
        inputSchema={"type": "object", "properties": {}},
    ),
    Tool(
        name="healthcheck",
        description="Verifica se o servidor está operacional e retorna a versão.",
        inputSchema={"type": "object", "properties": {}},
    ),
]


# ─────────────────────────────────────────────────────────────
# MCP server: list_tools / call_tool
# ─────────────────────────────────────────────────────────────
server = Server(SERVER_NAME)


@server.list_tools()
async def _list_tools() -> list[Tool]:
    return TOOLS


@server.call_tool()
async def _call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent]:
    logger.info("tool call: %s", name)
    try:
        if name == "calcular_mapa_natal":
            resultado = calcular_mapa_natal(
                data=arguments["data"],
                hora=arguments.get("hora"),
                local=arguments.get("local"),
                nome=arguments.get("nome"),
                sistema_casas=arguments.get("sistema_casas"),
            )
        elif name == "calcular_sinastria":
            resultado = calcular_sinastria(
                pessoa_a=arguments["pessoa_a"],
                pessoa_b=arguments["pessoa_b"],
                sistema_casas=arguments.get("sistema_casas"),
            )
        elif name == "calcular_transitos":
            resultado = calcular_transitos(
                natal=arguments["natal"],
                data_transito=arguments["data_transito"],
                hora_transito=arguments.get("hora_transito"),
                local_transito=arguments.get("local_transito"),
                sistema_casas=arguments.get("sistema_casas"),
            )
        elif name == "calcular_progressoes":
            resultado = calcular_progressoes(
                natal=arguments["natal"],
                data_alvo=arguments["data_alvo"],
                sistema_casas=arguments.get("sistema_casas"),
            )
        elif name == "calcular_mapa_composto":
            resultado = calcular_mapa_composto(
                pessoa_a=arguments["pessoa_a"],
                pessoa_b=arguments["pessoa_b"],
                sistema_casas=arguments.get("sistema_casas"),
            )
        elif name == "listar_aspectos_tipos":
            resultado = {"aspectos": listar_tipos_aspectos()}
        elif name == "healthcheck":
            resultado = {"status": "ok", "versao": SERVER_VERSION, "transporte": "sse"}
        else:
            raise ValueError(f"Tool desconhecida: {name}")

        return [TextContent(type="text", text=json.dumps(resultado, ensure_ascii=False))]
    except GeocodingError as exc:
        return [TextContent(type="text", text=json.dumps({"erro": str(exc)}, ensure_ascii=False))]
    except ValueError as exc:
        return [TextContent(type="text", text=json.dumps({"erro": str(exc)}, ensure_ascii=False))]
    except Exception as exc:  # noqa: BLE001
        logger.exception("erro inesperado em %s", name)
        return [TextContent(type="text", text=json.dumps(
            {"erro": "Erro interno do servidor.", "detalhe": str(exc)}, ensure_ascii=False
        ))]


# ─────────────────────────────────────────────────────────────
# Auth middleware (header Bearer ou ?api_key=)
# ─────────────────────────────────────────────────────────────
def _extrair_key(request: Request) -> str | None:
    auth = request.headers.get("authorization", "")
    if auth.lower().startswith("bearer "):
        return auth[7:].strip()
    return request.query_params.get("api_key")


class APIKeyMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # /health é público
        if request.url.path == "/health":
            return await call_next(request)

        # Sem chave configurada → libera (modo dev)
        if not API_KEY:
            return await call_next(request)

        key = _extrair_key(request)
        if key != API_KEY:
            return JSONResponse({"erro": "API key inválida ou ausente."}, status_code=401)
        return await call_next(request)


# ─────────────────────────────────────────────────────────────
# Starlette app: SSE + /messages + /health
# ─────────────────────────────────────────────────────────────
sse_transport = SseServerTransport("/messages/")


async def _handle_sse(request: Request) -> Response:
    async with sse_transport.connect_sse(
        request.scope, request.receive, request._send,  # noqa: SLF001
    ) as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server.create_initialization_options())
    return Response()


async def _health(_: Request) -> JSONResponse:
    return JSONResponse({
        "status": "ok",
        "service": SERVER_NAME,
        "versao": SERVER_VERSION,
        "transporte": "sse",
        "auth_required": bool(API_KEY),
    })


async def _list_tools_http(_: Request) -> JSONResponse:
    """Lista as tools registradas via HTTP puro (debug). Reutiliza TOOLS."""
    payload_tools = []
    for tool in TOOLS:
        schema = tool.inputSchema or {}
        properties = list((schema.get("properties") or {}).keys())
        payload_tools.append({
            "name": tool.name,
            "description": tool.description,
            "required": list(schema.get("required") or []),
            "properties": properties,
        })
    return JSONResponse({
        "service": SERVER_NAME,
        "versao": SERVER_VERSION,
        "count": len(payload_tools),
        "tools": payload_tools,
    })


app = Starlette(
    debug=False,
    routes=[
        Route("/health", endpoint=_health, methods=["GET"]),
        Route("/tools", endpoint=_list_tools_http, methods=["GET"]),
        Route("/sse", endpoint=_handle_sse, methods=["GET"]),
        Mount("/messages/", app=sse_transport.handle_post_message),
    ],
    middleware=[Middleware(APIKeyMiddleware)],
)
