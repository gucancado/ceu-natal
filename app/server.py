"""
Servidor MCP do céu-natal: expõe tools de astrologia via SSE sobre HTTP.

Endpoints:
  GET  /sse        — abre o canal SSE (handshake MCP, legado)
  POST /messages/  — canal de mensagens SSE
  POST /mcp        — Streamable HTTP (protocolo MCP >= 2025-03-26)
  GET  /health     — healthcheck público (sem auth)

Autenticação: header `Authorization: Bearer <key>` ou query `?api_key=<key>`.
Se MCP_API_KEY não estiver configurado, libera tudo (modo dev).

Variáveis de ambiente opcionais:
  MCP_ALLOWED_HOSTS — hosts permitidos no Streamable HTTP (anti-DNS rebinding),
                      separados por vírgula. Vazio = sem validação de host.
"""
import contextlib
import json
import logging
import os
import time
from collections.abc import AsyncIterator
from typing import Any

import anyio

from mcp.server import Server
from mcp.server.sse import SseServerTransport
from mcp.server.streamable_http_manager import StreamableHTTPSessionManager
from mcp.server.streamable_http import TransportSecuritySettings
from mcp.types import Tool, ToolAnnotations, TextContent, CallToolResult

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
from app.tools.revolucao_lunar import calcular_revolucao_lunar
from app.tools.revolucao_solar import calcular_revolucao_solar
from app.tools.sinastria import calcular_sinastria
from app.tools.transitos import calcular_transitos

SERVER_NAME = os.getenv("MCP_SERVER_NAME", "ceu-natal")
SERVER_VERSION = os.getenv("MCP_SERVER_VERSION", "2.0.0")
API_KEY = os.getenv("MCP_API_KEY", "").strip()
# Hosts permitidos no transporte Streamable HTTP (anti-DNS rebinding).
# Vazio = sem validação (modo dev / proxy reverso confiável).
ALLOWED_HOSTS = [h.strip() for h in os.getenv("MCP_ALLOWED_HOSTS", "").split(",") if h.strip()]

logger = logging.getLogger("ceu-natal")
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")


# Annotations compartilhadas:
# • tools de cálculo astrológico — somente leitura, idempotentes, podem
#   acionar geocodificação externa (openWorldHint=True).
# • tools puramente locais (healthcheck, listar_aspectos_tipos) não chamam
#   nada externo (openWorldHint=False).
_ANOTACOES_CALCULO = ToolAnnotations(
    readOnlyHint=True,
    destructiveHint=False,
    idempotentHint=True,
    openWorldHint=True,
)
_ANOTACOES_LOCAL = ToolAnnotations(
    readOnlyHint=True,
    destructiveHint=False,
    idempotentHint=True,
    openWorldHint=False,
)


def _log_tool_call(tool: str, status: str, duration_ms: float) -> None:
    logger.info(json.dumps({
        "event": "tool_call",
        "tool": tool,
        "status": status,
        "duration_ms": duration_ms,
    }, ensure_ascii=False))


def _resultado_erro(mensagem: str) -> CallToolResult:
    return CallToolResult(
        content=[TextContent(type="text", text=json.dumps({"erro": mensagem}, ensure_ascii=False))],
        isError=True,
    )


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
        annotations=_ANOTACOES_CALCULO,
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
        annotations=_ANOTACOES_CALCULO,
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
        annotations=_ANOTACOES_CALCULO,
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
        annotations=_ANOTACOES_CALCULO,
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
        annotations=_ANOTACOES_CALCULO,
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
        name="calcular_revolucao_solar",
        description=(
            "Calcula a revolução solar (solar return) de um ano — o mapa do instante "
            "exato em que o Sol retorna à longitude que ocupava no nascimento, técnica "
            "de previsão anual. Rege o período até a revolução seguinte. Retorna o mapa "
            "completo da revolução (planetas, casas, ângulos, aspectos internos), os "
            "aspectos entre a revolução e o mapa natal, a sobreposição dos dois mapas e "
            "destaques da leitura: ascendente da revolução e seus regentes, casa ocupada "
            "pelo Sol e planetas angulares. Exige hora e local de nascimento. O parâmetro "
            "local_revolucao é obrigatório e define ascendente, meio do céu e casas — as "
            "posições planetárias são as mesmas em qualquer lugar do mundo."
        ),
        annotations=_ANOTACOES_CALCULO,
        inputSchema={
            "type": "object",
            "required": ["natal", "ano", "local_revolucao"],
            "properties": {
                "natal": {
                    "type": "object",
                    "required": ["data"],
                    "properties": {
                        "data":  {"type": "string", "description": "DD/MM/YYYY."},
                        "hora":  {"type": ["string", "null"], "description": "HH:MM. Obrigatória na prática."},
                        "local": {
                            "type": ["string", "null"],
                            "description": "Cidade e UF/país. Obrigatória na prática.",
                        },
                        "nome":  {"type": ["string", "null"]},
                    },
                },
                "ano": {
                    "type": "integer",
                    "description": (
                        "Ano da revolução (1800–2200, nunca anterior ao nascimento). "
                        "É o retorno que ocorre em torno da data de nascimento nesse "
                        "ano — pode cair um dia antes ou depois do aniversário, e para "
                        "quem nasceu no começo de janeiro pode cair em dezembro do ano "
                        "anterior. Vale até o retorno seguinte, então para saber qual "
                        "rege hoje use o ano do último aniversário."
                    ),
                },
                "local_revolucao": {
                    "type": "string",
                    "description": (
                        "Cidade e UF/país onde a pessoa estará no momento do retorno "
                        "(ex: 'Lisboa, Portugal'). Obrigatório — muda apenas os ângulos "
                        "e as casas, nunca as posições planetárias."
                    ),
                },
                "sistema_casas": {"type": ["string", "null"]},
            },
        },
    ),
    Tool(
        name="calcular_revolucao_lunar",
        description=(
            "Calcula a revolução lunar (lunar return) — o mapa do instante exato em que "
            "a Lua retorna à longitude que ocupava no nascimento, técnica de previsão "
            "mensal com ciclo de ~27,3 dias. Retorna o primeiro retorno lunar a partir da "
            "data de referência informada, com mapa completo, aspectos com o natal, "
            "sobreposição dos dois mapas e destaques centrados na Lua: casa que ela ocupa, "
            "ascendente da revolução e seus regentes, planetas angulares. Exige hora e "
            "local de nascimento. O parâmetro local_revolucao é obrigatório."
        ),
        annotations=_ANOTACOES_CALCULO,
        inputSchema={
            "type": "object",
            "required": ["natal", "data_referencia", "local_revolucao"],
            "properties": {
                "natal": {
                    "type": "object",
                    "required": ["data"],
                    "properties": {
                        "data":  {"type": "string", "description": "DD/MM/YYYY."},
                        "hora":  {"type": ["string", "null"], "description": "HH:MM. Obrigatória na prática."},
                        "local": {
                            "type": ["string", "null"],
                            "description": "Cidade e UF/país. Obrigatória na prática.",
                        },
                        "nome":  {"type": ["string", "null"]},
                    },
                },
                "data_referencia": {
                    "type": "string",
                    "description": (
                        "Data DD/MM/YYYY a partir da qual buscar o retorno. Devolve o "
                        "PRÓXIMO retorno — o primeiro que ocorra nessa data ou depois "
                        "dela — e não o ciclo já em curso. Passar a data de hoje "
                        "costuma devolver o mês lunar que ainda vai começar; nesse caso "
                        "o resultado traz o bloco `ciclo_em_curso` com a data para "
                        "obter o ciclo vigente."
                    ),
                },
                "local_revolucao": {
                    "type": "string",
                    "description": (
                        "Cidade e UF/país onde a pessoa estará no momento do retorno. "
                        "Obrigatório — muda apenas os ângulos e as casas."
                    ),
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
        annotations=_ANOTACOES_LOCAL,
        inputSchema={"type": "object", "properties": {}},
        outputSchema={
            "type": "object",
            "properties": {
                "aspectos": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "tipo":             {"type": "string"},
                            "angulo":           {"type": "number"},
                            "orbe_padrao":      {"type": "number"},
                            "orbe_com_luminar": {"type": "number"},
                            "orbe_exato":       {"type": "number"},
                            "natureza":         {"type": "string"},
                        },
                    },
                },
            },
        },
    ),
    Tool(
        name="healthcheck",
        description="Verifica se o servidor está operacional e retorna a versão.",
        annotations=_ANOTACOES_LOCAL,
        inputSchema={"type": "object", "properties": {}},
        outputSchema={
            "type": "object",
            "properties": {
                "status":     {"type": "string"},
                "versao":     {"type": "string"},
                "transporte": {"type": "string"},
            },
            "required": ["status", "versao", "transporte"],
        },
    ),
]


# ─────────────────────────────────────────────────────────────
# MCP server: list_tools / call_tool
# ─────────────────────────────────────────────────────────────
server = Server(SERVER_NAME)


@server.list_tools()
async def _list_tools() -> list[Tool]:
    return TOOLS


def _dispatch(name: str, arguments: dict[str, Any]) -> dict:
    """Despacho síncrono puro. Levanta ValueError/GeocodingError; sem I/O async."""
    if name == "calcular_mapa_natal":
        return calcular_mapa_natal(
            data=arguments["data"],
            hora=arguments.get("hora"),
            local=arguments.get("local"),
            nome=arguments.get("nome"),
            sistema_casas=arguments.get("sistema_casas"),
        )
    elif name == "calcular_sinastria":
        return calcular_sinastria(
            pessoa_a=arguments["pessoa_a"],
            pessoa_b=arguments["pessoa_b"],
            sistema_casas=arguments.get("sistema_casas"),
        )
    elif name == "calcular_transitos":
        return calcular_transitos(
            natal=arguments["natal"],
            data_transito=arguments["data_transito"],
            hora_transito=arguments.get("hora_transito"),
            local_transito=arguments.get("local_transito"),
            sistema_casas=arguments.get("sistema_casas"),
        )
    elif name == "calcular_progressoes":
        return calcular_progressoes(
            natal=arguments["natal"],
            data_alvo=arguments["data_alvo"],
            sistema_casas=arguments.get("sistema_casas"),
        )
    elif name == "calcular_mapa_composto":
        return calcular_mapa_composto(
            pessoa_a=arguments["pessoa_a"],
            pessoa_b=arguments["pessoa_b"],
            sistema_casas=arguments.get("sistema_casas"),
        )
    elif name == "calcular_revolucao_solar":
        return calcular_revolucao_solar(
            natal=arguments["natal"],
            ano=arguments["ano"],
            local_revolucao=arguments["local_revolucao"],
            sistema_casas=arguments.get("sistema_casas"),
        )
    elif name == "calcular_revolucao_lunar":
        return calcular_revolucao_lunar(
            natal=arguments["natal"],
            data_referencia=arguments["data_referencia"],
            local_revolucao=arguments["local_revolucao"],
            sistema_casas=arguments.get("sistema_casas"),
        )
    elif name == "listar_aspectos_tipos":
        return {"aspectos": listar_tipos_aspectos()}
    elif name == "healthcheck":
        return {"status": "ok", "versao": SERVER_VERSION, "transporte": "streamable-http+sse"}
    else:
        raise ValueError(f"Tool desconhecida: {name}")


@server.call_tool()
async def _call_tool(name: str, arguments: dict[str, Any]):
    """Marshaller: cronometra, roda o cálculo em threadpool, loga e trata erros."""
    inicio = time.monotonic()
    status = "ok"
    try:
        try:
            resultado = await anyio.to_thread.run_sync(_dispatch, name, arguments)
        except GeocodingError as exc:
            status = "geocoding_error"
            return _resultado_erro(str(exc))
        except ValueError as exc:
            status = "value_error"
            return _resultado_erro(str(exc))
        except Exception:  # noqa: BLE001
            status = "internal_error"
            logger.exception("erro inesperado em %s", name)
            return _resultado_erro("Erro interno do servidor.")

        conteudo = [TextContent(type="text", text=json.dumps(resultado, ensure_ascii=False))]
        return (conteudo, resultado)
    finally:
        duracao_ms = round((time.monotonic() - inicio) * 1000, 1)
        _log_tool_call(name, status, duracao_ms)


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
# Transporte Streamable HTTP (MCP >= 2025-03-26) + lifespan
# ─────────────────────────────────────────────────────────────
_security = (
    TransportSecuritySettings(allowed_hosts=ALLOWED_HOSTS)
    if ALLOWED_HOSTS
    else None
)

session_manager = StreamableHTTPSessionManager(
    app=server,
    security_settings=_security,
)


@contextlib.asynccontextmanager
async def lifespan(_app: Any) -> AsyncIterator[None]:
    async with session_manager.run():
        yield


# ─────────────────────────────────────────────────────────────
# Transporte SSE legado + /messages
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
        "transporte": "streamable-http+sse",
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
    lifespan=lifespan,
    routes=[
        Route("/health", endpoint=_health, methods=["GET"]),
        Route("/tools", endpoint=_list_tools_http, methods=["GET"]),
        Route("/sse", endpoint=_handle_sse, methods=["GET"]),
        Mount("/messages/", app=sse_transport.handle_post_message),
        Mount("/mcp", app=session_manager.handle_request),
    ],
    middleware=[Middleware(APIKeyMiddleware)],
)
