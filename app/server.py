# SPDX-License-Identifier: AGPL-3.0-or-later
"""
Servidor MCP do céu-natal: expõe tools de astrologia por Streamable HTTP (`/mcp/`,
principal) e SSE (`/sse`, legado).

Endpoints:
  GET  /sse        — abre o canal SSE (handshake MCP, legado)
  POST /messages/  — canal de mensagens SSE
  POST /mcp        — Streamable HTTP (protocolo MCP >= 2025-03-26)
  GET  /health     — healthcheck público (sem auth)
  GET  /llms.txt   — descrição do servidor para LLMs (público)
  GET  /           — redireciona (302) para PUBLIC_SITE_URL (público)
  POST /mapa-rapido — mapa natal para o formulário do site (público, CORS só
                      para PUBLIC_SITE_URL, limite por IP)

Autenticação: header `Authorization: Bearer <key>` (a chave na query string não
é aceita: vazaria em logs de proxy). Se MCP_API_KEY não estiver configurado,
libera tudo (modo dev).

Configuração: `app.config.Settings` (variáveis de ambiente lidas em
`Settings.do_ambiente()`). `create_app(settings)` monta uma aplicação
independente — servidor MCP, transportes e limitadores próprios —, e o módulo
expõe `app = create_app()` para o uvicorn (`app.server:app`).
"""
import contextlib
import copy
import functools
import hmac
import ipaddress
import json
import logging
import math
import time
from collections.abc import AsyncIterator, Callable
from pathlib import Path
from types import SimpleNamespace
from typing import Any

import anyio
from mcp.server import Server
from mcp.server.sse import SseServerTransport
from mcp.server.streamable_http import TransportSecuritySettings
from mcp.server.streamable_http_manager import StreamableHTTPSessionManager
from mcp.types import CallToolResult, TextContent, Tool, ToolAnnotations
from starlette.applications import Starlette
from starlette.middleware import Middleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, PlainTextResponse, RedirectResponse, Response
from starlette.routing import Mount, Route

from app.config import Settings
from app.core.aspectos import listar_tipos_aspectos
from app.core.geocoder import GeocodingError
from app.core.ratelimit import LimitadorTaxa

# Teto do corpo do /mapa-rapido (bytes): data, hora e local cabem com folga.
MAPA_RAPIDO_BODY_MAX = 4096
# Caminhos que dispensam a chave de API.
_DESAFIO_OPENAI = "/.well-known/openai-apps-challenge"
_PUBLICOS = ["/health", "/llms.txt", "/", "/mapa-rapido", _DESAFIO_OPENAI]
_LLMS_TXT_PATH = Path(__file__).parent / "static" / "llms.txt"
TRANSPORTE = "streamable-http+sse"

logger = logging.getLogger("ceu-natal")


def configurar_logging() -> None:
    """Formato de log do processo; sem efeito se o logging já foi configurado."""
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
_DESCRICAO_IS_DST = (
    "Só para hora ambígua ou inexistente na transição do horário de verão: "
    "true = horário de verão, false = horário padrão."
)

# Objeto pessoa/natal das tools (lido por `EntradaNascimento.de_dict`).
# Modelo: cada uso passa por `_schema_pessoa()`, que devolve uma cópia própria.
_SCHEMA_PESSOA: dict = {
    "type": "object",
    "required": ["data"],
    "properties": {
        "data":  {"type": "string"},
        "hora":  {"type": ["string", "null"]},
        "local": {"type": ["string", "null"]},
        "nome":  {"type": ["string", "null"]},
        "is_dst": {"type": ["boolean", "null"], "description": _DESCRICAO_IS_DST},
    },
}


def _schema_pessoa(**descricoes: str) -> dict:
    """Cópia de `_SCHEMA_PESSOA` com `description` nos campos indicados."""
    schema = copy.deepcopy(_SCHEMA_PESSOA)
    for campo, descricao in descricoes.items():
        schema["properties"][campo]["description"] = descricao
    return schema


def _schema_natal_revolucao() -> dict:
    """Revoluções exigem hora e local: o schema diz isso nos campos."""
    return _schema_pessoa(
        data="DD/MM/YYYY.",
        hora="HH:MM. Obrigatória na prática.",
        local="Cidade e UF/país. Obrigatória na prática.",
    )

TOOLS: list[Tool] = [
    Tool(
        name="calcular_mapa_natal",
        description=(
            "Calcula o mapa astral natal completo de uma pessoa. Retorna posições "
            "planetárias, casas (Placidus por padrão; sistema configurável), ângulos, "
            "aspectos entre planetas, pontos sensíveis (nodos verdadeiros e Quíron) e "
            "síntese (elementos, qualidades, hemisférios, stelliums). Se hora ou local "
            "forem omitidos, retorna apenas posições por signo, sem casas nem ângulos. "
            "Sem hora, o cálculo usa 12:00 no horário local e a Lua vem marcada como "
            "incerta (posicao_incerta, signo_pode_mudar)."
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
                    "description": "Hora de nascimento no formato HH:MM. Opcional; sem ela, usa 12:00 local.",
                },
                "local": {
                    "type": ["string", "null"],
                    "description": "Cidade e UF/país (ex: 'Belo Horizonte, MG'). Opcional.",
                },
                "nome": {
                    "type": ["string", "null"],
                    "description": "Nome da pessoa (apenas para identificação). Opcional.",
                },
                "is_dst": {
                    "type": ["boolean", "null"],
                    "description": _DESCRICAO_IS_DST,
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
                "pessoa_a": _schema_pessoa(),
                "pessoa_b": _schema_pessoa(),
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
                "natal": _schema_pessoa(),
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
                "natal": _schema_pessoa(),
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
                "pessoa_a": _schema_pessoa(),
                "pessoa_b": _schema_pessoa(),
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
                "natal": _schema_natal_revolucao(),
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
                "natal": _schema_natal_revolucao(),
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
                "proximo_passo": {"type": "string"},
            },
            "required": ["status", "versao", "transporte", "proximo_passo"],
        },
    ),
]

# Os diretórios de conectores exigem título em toda tool.
_TITULOS = {
    "calcular_mapa_natal": "Mapa natal",
    "calcular_sinastria": "Sinastria",
    "calcular_transitos": "Trânsitos",
    "calcular_progressoes": "Progressões secundárias",
    "calcular_mapa_composto": "Mapa composto",
    "calcular_revolucao_solar": "Revolução solar",
    "calcular_revolucao_lunar": "Revolução lunar",
    "listar_aspectos_tipos": "Tipos de aspecto",
    "healthcheck": "Verificar o servidor",
}
TOOLS = [
    t.model_copy(update={
        "title": _TITULOS[t.name],
        "annotations": (t.annotations or ToolAnnotations()).model_copy(update={"title": _TITULOS[t.name]}),
    })
    for t in TOOLS
]


# ─────────────────────────────────────────────────────────────
# Registro de tools: nome → função(arguments) -> dict
# ─────────────────────────────────────────────────────────────
@functools.lru_cache(maxsize=1)
def _tools() -> SimpleNamespace:
    """Importa as tools de cálculo sob demanda (puxam Kerykeion/pyswisseph).

    Mantém `import app.server` leve e testável sem Kerykeion (ex.: Windows).
    """
    from app.tools.composto import calcular_mapa_composto
    from app.tools.mapa_natal import calcular_mapa_natal
    from app.tools.progressoes import calcular_progressoes
    from app.tools.revolucao_lunar import calcular_revolucao_lunar
    from app.tools.revolucao_solar import calcular_revolucao_solar
    from app.tools.sinastria import calcular_sinastria
    from app.tools.transitos import calcular_transitos

    return SimpleNamespace(
        calcular_mapa_natal=calcular_mapa_natal,
        calcular_sinastria=calcular_sinastria,
        calcular_transitos=calcular_transitos,
        calcular_progressoes=calcular_progressoes,
        calcular_mapa_composto=calcular_mapa_composto,
        calcular_revolucao_solar=calcular_revolucao_solar,
        calcular_revolucao_lunar=calcular_revolucao_lunar,
    )


# Só descrevem o servidor: os diretórios rejeitam texto que dite o comportamento do assistente.
INSTRUCOES = (
    "O Céu Natal calcula astrologia com as efemérides suíças: mapa natal, sinastria, mapa "
    "composto, trânsitos, progressões e revoluções solar e lunar. O mapa natal precisa da "
    "data de nascimento em DD/MM/AAAA e, para casas e ângulos, de hora e cidade."
)
PROXIMO_PASSO = "Servidor conectado. Para calcular um mapa natal são necessários data, hora e cidade de nascimento."


# `healthcheck` depende da versão configurada e entra por aplicação
# (`Aplicacao.registro`); as demais não dependem de configuração.
REGISTRO: dict[str, Callable[[dict], dict]] = {
    "calcular_mapa_natal": lambda a: _tools().calcular_mapa_natal(
        data=a["data"],
        hora=a.get("hora"),
        local=a.get("local"),
        nome=a.get("nome"),
        sistema_casas=a.get("sistema_casas"),
        is_dst=a.get("is_dst"),
    ),
    "calcular_sinastria": lambda a: _tools().calcular_sinastria(
        pessoa_a=a["pessoa_a"],
        pessoa_b=a["pessoa_b"],
        sistema_casas=a.get("sistema_casas"),
    ),
    "calcular_transitos": lambda a: _tools().calcular_transitos(
        natal=a["natal"],
        data_transito=a["data_transito"],
        hora_transito=a.get("hora_transito"),
        local_transito=a.get("local_transito"),
        sistema_casas=a.get("sistema_casas"),
    ),
    "calcular_progressoes": lambda a: _tools().calcular_progressoes(
        natal=a["natal"],
        data_alvo=a["data_alvo"],
        sistema_casas=a.get("sistema_casas"),
    ),
    "calcular_mapa_composto": lambda a: _tools().calcular_mapa_composto(
        pessoa_a=a["pessoa_a"],
        pessoa_b=a["pessoa_b"],
        sistema_casas=a.get("sistema_casas"),
    ),
    "calcular_revolucao_solar": lambda a: _tools().calcular_revolucao_solar(
        natal=a["natal"],
        ano=a["ano"],
        local_revolucao=a["local_revolucao"],
        sistema_casas=a.get("sistema_casas"),
    ),
    "calcular_revolucao_lunar": lambda a: _tools().calcular_revolucao_lunar(
        natal=a["natal"],
        data_referencia=a["data_referencia"],
        local_revolucao=a["local_revolucao"],
        sistema_casas=a.get("sistema_casas"),
    ),
    "listar_aspectos_tipos": lambda a: {"aspectos": listar_tipos_aspectos()},
}


def _dispatch(
    name: str,
    arguments: dict[str, Any],
    registro: dict[str, Callable[[dict], dict]] = REGISTRO,
) -> dict:
    """Despacho síncrono puro. Levanta ValueError/GeocodingError; sem I/O async."""
    funcao = registro.get(name)
    if funcao is None:
        raise ValueError(f"Tool desconhecida: {name}")
    return funcao(arguments)


# ─────────────────────────────────────────────────────────────
# Auth middleware (só header Bearer)
# ─────────────────────────────────────────────────────────────
def _extrair_key(request: Request) -> str | None:
    """Chave do header `Authorization: Bearer`; query string não é aceita."""
    auth = request.headers.get("authorization", "")
    if auth.lower().startswith("bearer "):
        return auth[7:].strip()
    return None


class APIKeyMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, api_key: str) -> None:
        super().__init__(app)
        self.api_key = api_key

    async def dispatch(self, request: Request, call_next):
        # Caminhos de _PUBLICOS dispensam a chave.
        if request.url.path in _PUBLICOS:
            return await call_next(request)

        # Sem chave configurada → libera (modo dev)
        if not self.api_key:
            return await call_next(request)

        key = _extrair_key(request)
        if key is None or not hmac.compare_digest(key.encode(), self.api_key.encode()):
            return JSONResponse({"erro": "API key inválida ou ausente."}, status_code=401)
        return await call_next(request)


# ─────────────────────────────────────────────────────────────
# IP do cliente e CORS (/mapa-rapido)
# ─────────────────────────────────────────────────────────────
def _ip_global(host: str | None) -> bool:
    if not host:
        return False
    try:
        return ipaddress.ip_address(host).is_global
    except ValueError:
        return False


def _ip_cliente(request: Request) -> str | None:
    """IP de quem chamou, sem confiar no que o cliente escreve no X-Forwarded-For.

    Conexão vinda de IP global → é o próprio cliente (sem proxy na frente).
    Conexão de rede privada → o ÚLTIMO item do X-Forwarded-For, que é o
    endereço que o proxy viu; os itens anteriores são do cliente e podem ser
    forjados.
    """
    # A confiança é "peer privado (rede Docker)", não "peer = Traefik": qualquer
    # conexão de endereço não global tem o último item do XFF aceito. Vale porque
    # a porta do container não é publicada; só o proxy alcança o app por rede
    # privada.
    host = request.client.host if request.client else None
    if _ip_global(host):
        return host
    xff = [p.strip() for p in request.headers.get("x-forwarded-for", "").split(",") if p.strip()]
    if xff:
        return xff[-1]
    return host


_CAMPOS_MAPA_RAPIDO = ("data", "hora", "local")


# ─────────────────────────────────────────────────────────────
# Aplicação: estado e handlers de uma instância (create_app)
# ─────────────────────────────────────────────────────────────
class Aplicacao:
    """Servidor MCP, transportes, limitadores e handlers HTTP de um app.

    Cada `create_app` cria a sua: nada de estado montado no import do módulo.
    """

    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.limitador = LimitadorTaxa(
            settings.rate_limit_session_per_min, settings.rate_limit_global_per_min,
        )
        self.limitador_mapa_rapido = LimitadorTaxa(
            settings.rate_limit_mapa_rapido_ip_per_min,
            settings.rate_limit_mapa_rapido_global_per_min,
        )
        self.llms_txt = _LLMS_TXT_PATH.read_text(encoding="utf-8").format(
            mcp_url=settings.public_mcp_url, site_url=settings.public_site_url,
        )
        self.registro: dict[str, Callable[[dict], dict]] = {
            **REGISTRO,
            "healthcheck": lambda a: {
                "status": "ok", "versao": settings.server_version, "transporte": TRANSPORTE,
                "proximo_passo": PROXIMO_PASSO,
            },
        }

        self.server = Server(settings.server_name, instructions=INSTRUCOES)

        @self.server.list_tools()
        async def _list_tools() -> list[Tool]:
            return TOOLS

        @self.server.call_tool()
        async def _call_tool(name: str, arguments: dict[str, Any]):
            return await self.call_tool(name, arguments)

        # Transporte Streamable HTTP (MCP >= 2025-03-26).
        security = (
            TransportSecuritySettings(allowed_hosts=list(settings.allowed_hosts))
            if settings.allowed_hosts
            else None
        )
        self.session_manager = StreamableHTTPSessionManager(
            app=self.server,
            security_settings=security,
            # Sessão sem requisições por 30 min é encerrada (recomendação do SDK);
            # sem isso o dicionário de sessões do SDK só cresce.
            session_idle_timeout=1800,
        )
        # Transporte SSE legado + /messages.
        self.sse_transport = SseServerTransport("/messages/")

    # ── MCP ──────────────────────────────────────────────────
    def dispatch(self, name: str, arguments: dict[str, Any]) -> dict:
        return _dispatch(name, arguments, self.registro)

    def chave_sessao(self) -> str | None:
        """Id da sessão MCP (header mcp-session-id) ou None fora de request/SSE legado."""
        try:
            request = self.server.request_context.request
        except LookupError:
            return None
        if request is None:
            return None
        return request.headers.get("mcp-session-id")

    async def call_tool(self, name: str, arguments: dict[str, Any]):
        """Marshaller: cronometra, roda o cálculo em threadpool, loga e trata erros."""
        inicio = time.monotonic()
        status = "ok"
        try:
            permitido, espera = self.limitador.tentar(self.chave_sessao())
            if not permitido:
                status = "rate_limited"
                return _resultado_erro(
                    f"Limite de chamadas atingido. Aguarde {math.ceil(espera)} segundos e tente de novo."
                )
            try:
                resultado = await anyio.to_thread.run_sync(self.dispatch, name, arguments)
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

    @contextlib.asynccontextmanager
    async def lifespan(self, _app: Any) -> AsyncIterator[None]:
        async with self.session_manager.run():
            yield

    async def handle_sse(self, request: Request) -> Response:
        async with self.sse_transport.connect_sse(
            request.scope, request.receive, request._send,  # noqa: SLF001
        ) as (read_stream, write_stream):
            await self.server.run(read_stream, write_stream, self.server.create_initialization_options())
        return Response()

    # ── HTTP ─────────────────────────────────────────────────
    async def health(self, _: Request) -> JSONResponse:
        s = self.settings
        return JSONResponse({
            "status": "ok",
            "service": s.server_name,
            "versao": s.server_version,
            "transporte": TRANSPORTE,
            "auth_required": bool(s.api_key),
            "site": s.public_site_url,
            "limites": {
                "por_sessao_por_min": s.rate_limit_session_per_min,
                "global_por_min": s.rate_limit_global_per_min,
            },
            "mapa_rapido": {
                "por_ip_por_min": s.rate_limit_mapa_rapido_ip_per_min,
                "global_por_min": s.rate_limit_mapa_rapido_global_per_min,
            },
        })

    async def llms_txt_endpoint(self, _: Request) -> PlainTextResponse:
        return PlainTextResponse(self.llms_txt, media_type="text/plain; charset=utf-8")

    async def desafio_openai(self, _: Request) -> PlainTextResponse:
        """Token de verificação de domínio do portal de plugins da OpenAI."""
        token = self.settings.openai_apps_challenge
        if not token:
            return PlainTextResponse("", status_code=404)
        return PlainTextResponse(token, media_type="text/plain; charset=utf-8")

    async def raiz(self, _: Request) -> RedirectResponse:
        return RedirectResponse(self.settings.public_site_url, status_code=302)

    def _cabecalhos_cors(self, request: Request) -> dict[str, str]:
        origem = request.headers.get("origin", "").rstrip("/")
        if origem and origem in self.settings.cors_efetivos:
            return {
                "Access-Control-Allow-Origin": origem,
                "Access-Control-Allow-Methods": "POST, OPTIONS",
                "Access-Control-Allow-Headers": "Content-Type",
                "Access-Control-Max-Age": "600",
                "Vary": "Origin",
            }
        return {"Vary": "Origin"}

    async def mapa_rapido(self, request: Request) -> Response:
        """Mapa natal para o formulário do site: data, hora e local; nada é guardado."""
        cors = self._cabecalhos_cors(request)
        if request.method == "OPTIONS":
            return Response(status_code=204, headers=cors)

        inicio = time.monotonic()
        status = "ok"
        try:
            permitido, espera = self.limitador_mapa_rapido.tentar(_ip_cliente(request))
            if not permitido:
                status = "rate_limited"
                cors_429 = {**cors, "Retry-After": str(math.ceil(espera))}
                return JSONResponse(
                    {"erro": f"Muitos pedidos. Aguarde {math.ceil(espera)} segundos e tente de novo."},
                    status_code=429, headers=cors_429,
                )
            grande = JSONResponse({"erro": "Corpo grande demais."}, status_code=413, headers=cors)
            try:
                tamanho_declarado = int(request.headers.get("content-length", "0"))
            except ValueError:
                tamanho_declarado = 0
            if tamanho_declarado > MAPA_RAPIDO_BODY_MAX:
                status = "body_too_large"
                return grande
            bruto = await request.body()
            if len(bruto) > MAPA_RAPIDO_BODY_MAX:  # upload chunked não traz Content-Length
                status = "body_too_large"
                return grande
            try:
                corpo = json.loads(bruto)
            except ValueError:
                corpo = None
            if not isinstance(corpo, dict) or not isinstance(corpo.get("data"), str):
                status = "value_error"
                return JSONResponse({"erro": "Envie um JSON com data (DD/MM/YYYY)."}, status_code=400, headers=cors)
            argumentos: dict[str, Any] = {}
            for campo in _CAMPOS_MAPA_RAPIDO:
                valor = corpo.get(campo)
                if valor is None or (isinstance(valor, str) and not valor.strip()):
                    continue
                if not isinstance(valor, str) or len(valor) > 120:
                    status = "value_error"
                    return JSONResponse({"erro": f"Campo inválido: {campo}."}, status_code=400, headers=cors)
                argumentos[campo] = valor.strip()
            try:
                resultado = await anyio.to_thread.run_sync(self.dispatch, "calcular_mapa_natal", argumentos)
            except GeocodingError as exc:
                status = "geocoding_error"
                return JSONResponse({"erro": str(exc)}, status_code=422, headers=cors)
            except ValueError as exc:
                status = "value_error"
                return JSONResponse({"erro": str(exc)}, status_code=400, headers=cors)
            except Exception:  # noqa: BLE001
                status = "internal_error"
                logger.exception("erro inesperado em mapa_rapido")
                return JSONResponse({"erro": "Erro interno do servidor."}, status_code=500, headers=cors)
            return JSONResponse(resultado, headers=cors)
        finally:
            _log_tool_call("mapa_rapido", status, round((time.monotonic() - inicio) * 1000, 1))

    async def listar_tools_http(self, _: Request) -> JSONResponse:
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
            "service": self.settings.server_name,
            "versao": self.settings.server_version,
            "count": len(payload_tools),
            "tools": payload_tools,
        })


def create_app(settings: Settings | None = None) -> Starlette:
    """Monta a aplicação Starlette; sem `settings`, lê o ambiente.

    A `Aplicacao` fica em `app.state.ceu` (testes chamam `call_tool`/`dispatch`
    por ali).
    """
    configurar_logging()
    ceu = Aplicacao(settings or Settings.do_ambiente())
    app = Starlette(
        debug=False,
        lifespan=ceu.lifespan,
        routes=[
            Route("/", endpoint=ceu.raiz, methods=["GET"]),
            Route("/llms.txt", endpoint=ceu.llms_txt_endpoint, methods=["GET"]),
            Route("/health", endpoint=ceu.health, methods=["GET"]),
            Route(_DESAFIO_OPENAI, endpoint=ceu.desafio_openai, methods=["GET"]),
            Route("/tools", endpoint=ceu.listar_tools_http, methods=["GET"]),
            Route("/mapa-rapido", endpoint=ceu.mapa_rapido, methods=["POST", "OPTIONS"]),
            Route("/sse", endpoint=ceu.handle_sse, methods=["GET"]),
            Mount("/messages/", app=ceu.sse_transport.handle_post_message),
            Mount("/mcp", app=ceu.session_manager.handle_request),
        ],
        middleware=[Middleware(APIKeyMiddleware, api_key=ceu.settings.api_key)],
    )
    app.state.ceu = ceu
    return app


app = create_app()
