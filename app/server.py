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
from app.tools.mapa_natal import calcular_mapa_natal
from app.tools.sinastria import calcular_sinastria

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
            "planetárias, casas (Placidus strict), ângulos, aspectos entre planetas, "
            "pontos sensíveis (nodos verdadeiros e Quíron) e síntese (elementos, "
            "qualidades, hemisférios, stelliums). Se hora ou local forem omitidos, "
            "retorna apenas posições por signo, sem casas nem ângulos."
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
            )
        elif name == "calcular_sinastria":
            resultado = calcular_sinastria(
                pessoa_a=arguments["pessoa_a"],
                pessoa_b=arguments["pessoa_b"],
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
