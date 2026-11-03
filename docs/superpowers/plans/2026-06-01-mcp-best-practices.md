# Boas práticas MCP — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Elevar o servidor MCP `ceu-natal` às práticas de mercado: concorrência sem bloqueio, telemetria objetiva por tool, sinalização correta de erro, metadados de tool (annotations + structured output) e transporte Streamable HTTP — sem alterar o contrato astrológico dos resultados.

**Architecture:** Toda a lógica de cálculo (síncrona, CPU-bound, com I/O de rede no geocoder) passa a rodar em threadpool via `anyio.to_thread.run_sync`, destravando o event loop SSE/HTTP. O handler `_call_tool` vira um marshaller fino que cronometra a chamada, emite log estruturado, e converte falhas em `CallToolResult(isError=True)`. As tools ganham `annotations` e passam a devolver `structuredContent`. O servidor expõe **dois transportes em paralelo** durante um grace period: o SSE legado (`/sse` + `/messages/`) e o novo Streamable HTTP (`/mcp`).

**Tech Stack:** Python 3.11, Starlette, uvicorn, `mcp` SDK (low-level `Server` + `SseServerTransport` + `StreamableHTTPSessionManager`), `anyio`, Kerykeion, geopy/Nominatim + GeoNames.

---

## Restrições do ambiente (ler antes de executar)

- **Versões verificadas localmente:** `mcp 1.27.1`, `anyio 4.13.0`. `StreamableHTTPSessionManager` e `anyio.to_thread.run_sync` existem e foram inspecionados.
- **Testes de `app/server.py` NÃO rodam no Windows local:** importar `app.server` puxa as tools, que importam `app.core.kerykeion`, que faz `from kerykeion import ...` no topo do módulo. Sem `kerykeion` instalado (não há wheel trivial no Windows), o import falha. **Todos os testes que tocam o servidor/tools rodam dentro do container Docker** (a imagem é Linux e instala kerykeion + pyswisseph).
  - Comando padrão de teste do servidor: `docker build -t ceu-natal-test . ; docker run --rm ceu-natal-test python -m pytest tests/ -v`
- **Testes de `app/core/geocoder.py` rodam localmente** (o geocoder não importa kerykeion). Comando: `.venv-validacao\Scripts\pytest.exe tests/test_geocoder.py -v`
- **Não bumpar Kerykeion nem Python** (CLAUDE.md). A única dependência que sobe é o piso do `mcp` (Task 5).
- **Decisões de escopo já fechadas com o dono:**
  - Telemetria = **somente logs estruturados** (sem OpenTelemetry/Prometheus neste ciclo).
  - Migração SSE → Streamable HTTP = **incluída agora**, em modo dual (SSE mantido como legado).
  - `outputSchema` estrito só nas duas tools triviais (`listar_aspectos_tipos`, `healthcheck`). Os 5 cálculos passam a devolver `structuredContent` **sem** `outputSchema` estrito — o output é profundamente aninhado e um schema rígido seria frágil e de baixo ROI. Isso é uma decisão deliberada, não um corte silencioso.

## File Structure

| Arquivo | Responsabilidade | Ação |
|---|---|---|
| `app/core/geocoder.py` | Resolução cidade→coords + cache. Ganha rate-limit do Nominatim e log estruturado de resolução. | Modify |
| `app/server.py` | Registro de tools, despacho, transporte. Ganha threadpool, telemetria, `isError`, annotations/structured output, Streamable HTTP. | Modify |
| `requirements.txt` | Sobe piso do `mcp` para garantir Streamable HTTP. | Modify |
| `tests/test_geocoder.py` | Cobre rate-limit e log de fonte. | Modify |
| `tests/test_server.py` | Corrige assert stale; cobre `isError`, telemetria, annotations, rota `/mcp`. | Modify |
| `CLAUDE.md`, `README.md`, `docs/CONECTAR-CLAUDE-AI.md`, `docs/validacao.md` | Documentam o endpoint `/mcp` e o estado pós-migração. | Modify |

---

## Task 1: Rate-limit do Nominatim (item #6)

**Files:**
- Modify: `app/core/geocoder.py`
- Test: `tests/test_geocoder.py`

**Contexto:** Nominatim/OSM exige ≤ 1 req/s. Hoje não há throttle ([geocoder.py:146](../../../app/core/geocoder.py#L146)). Vamos serializar as chamadas a Nominatim com um intervalo mínimo configurável.

- [ ] **Step 1: Write the failing tests**

Adicionar ao final de `tests/test_geocoder.py`:

```python
# ─────────────────────────────────────────────────────────────
# Rate-limit do Nominatim (≤ 1 req/s por padrão)
# ─────────────────────────────────────────────────────────────
class TestThrottleNominatim:
    def test_segunda_chamada_imediata_dorme(self, geocoder, monkeypatch):
        dormidas = []
        monkeypatch.setattr(geocoder.time, "sleep", lambda s: dormidas.append(s))
        # relógio que avança 0.0s entre leituras → segunda chamada precisa esperar
        monkeypatch.setattr(geocoder.time, "monotonic", lambda: 100.0)
        geocoder._last_nominatim = 0.0

        geocoder._throttle_nominatim()  # primeira: marca o relógio, não dorme
        geocoder._throttle_nominatim()  # segunda: gap = 0 → dorme ~intervalo

        assert len(dormidas) == 1
        assert dormidas[0] > 0

    def test_apos_intervalo_nao_dorme(self, geocoder, monkeypatch):
        dormidas = []
        monkeypatch.setattr(geocoder.time, "sleep", lambda s: dormidas.append(s))
        relogio = {"t": 100.0}
        monkeypatch.setattr(geocoder.time, "monotonic", lambda: relogio["t"])
        geocoder._last_nominatim = 0.0

        geocoder._throttle_nominatim()      # marca t=100
        relogio["t"] = 100.0 + geocoder._NOMINATIM_MIN_INTERVAL + 0.1
        geocoder._throttle_nominatim()      # já passou o intervalo → não dorme

        assert dormidas == []
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `.venv-validacao\Scripts\pytest.exe tests/test_geocoder.py::TestThrottleNominatim -v`
Expected: FAIL — `AttributeError: module 'app.core.geocoder' has no attribute 'time'` (e `_throttle_nominatim` / `_NOMINATIM_MIN_INTERVAL` inexistentes).

- [ ] **Step 3: Implement throttle**

Em `app/core/geocoder.py`, adicionar `import time` ao bloco de imports do topo (junto de `import threading`):

```python
import time
```

Logo após a definição de `HTTP_TIMEOUT = 8` (linha ~17), adicionar:

```python
# Nominatim/OSM exige no máximo 1 req/s. Serializamos as chamadas.
_NOMINATIM_MIN_INTERVAL = float(os.getenv("NOMINATIM_MIN_INTERVAL_S", "1.0"))
```

Junto das globais de cache (após `_cache_lock = threading.Lock()`, linha ~57), adicionar:

```python
_nominatim_lock = threading.Lock()
_last_nominatim = 0.0


def _throttle_nominatim() -> None:
    """Garante intervalo mínimo entre chamadas ao Nominatim (política OSM ≤ 1 req/s)."""
    global _last_nominatim
    with _nominatim_lock:
        espera = _NOMINATIM_MIN_INTERVAL - (time.monotonic() - _last_nominatim)
        if espera > 0:
            time.sleep(espera)
        _last_nominatim = time.monotonic()
```

Na função `_try_nominatim` (linha ~146), chamar o throttle como primeira linha do corpo, antes do `try`:

```python
def _try_nominatim(cidade: str, nacao: str) -> Optional[Tuple[float, float]]:
    _throttle_nominatim()
    try:
        geolocator = Nominatim(user_agent=NOMINATIM_USER_AGENT, timeout=HTTP_TIMEOUT)
        ...
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `.venv-validacao\Scripts\pytest.exe tests/test_geocoder.py -v`
Expected: PASS (os 12 antigos + os 2 novos = 14).

- [ ] **Step 5: Commit**

```bash
git add app/core/geocoder.py tests/test_geocoder.py
git commit -m "feat(geocoder): rate-limit do Nominatim (politica OSM 1 req/s)"
```

---

## Task 2: Log estruturado de resolução no geocoder (item #2, parte geocoder)

**Files:**
- Modify: `app/core/geocoder.py`
- Test: `tests/test_geocoder.py`

**Contexto:** Telemetria objetiva precisa do sinal de cache-hit e de qual provedor resolveu. Vamos emitir uma linha JSON por resolução.

- [ ] **Step 1: Write the failing tests**

Adicionar ao final de `tests/test_geocoder.py`:

```python
# ─────────────────────────────────────────────────────────────
# Log estruturado de resolução (telemetria)
# ─────────────────────────────────────────────────────────────
import json as _json


class TestLogResolucao:
    def _eventos(self, caplog):
        eventos = []
        for rec in caplog.records:
            try:
                obj = _json.loads(rec.getMessage())
            except (ValueError, TypeError):
                continue
            if obj.get("event") == "geocode":
                eventos.append(obj)
        return eventos

    def test_loga_fonte_geonames(self, geocoder, monkeypatch, caplog):
        monkeypatch.setattr(geocoder, "_try_geonames", lambda c, n: (-19.92, -43.94))
        monkeypatch.setattr(geocoder, "_resolve_timezone", lambda lat, lng: "America/Sao_Paulo")
        with caplog.at_level("INFO", logger="app.core.geocoder"):
            geocoder.geocode("Belo Horizonte", "MG")
        eventos = self._eventos(caplog)
        assert eventos and eventos[-1]["source"] == "geonames"
        assert eventos[-1]["cache_hit"] is False

    def test_loga_cache_hit_na_segunda(self, geocoder, monkeypatch, caplog):
        monkeypatch.setattr(geocoder, "_try_geonames", lambda c, n: (-19.92, -43.94))
        monkeypatch.setattr(geocoder, "_resolve_timezone", lambda lat, lng: "America/Sao_Paulo")
        geocoder.geocode("Belo Horizonte", "MG")
        with caplog.at_level("INFO", logger="app.core.geocoder"):
            geocoder.geocode("Belo Horizonte", "MG")
        eventos = self._eventos(caplog)
        assert eventos and eventos[-1]["cache_hit"] is True
        assert eventos[-1]["source"] == "cache"
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `.venv-validacao\Scripts\pytest.exe tests/test_geocoder.py::TestLogResolucao -v`
Expected: FAIL — nenhum evento `geocode` é emitido ainda (lista vazia → `assert eventos` falha).

- [ ] **Step 3: Implement structured logging in `geocode()`**

Em `app/core/geocoder.py`, adicionar um helper logo após `_throttle_nominatim`:

```python
def _log_geocode(cidade: str, nacao: str, source: str, cache_hit: bool) -> None:
    logger.info(json.dumps({
        "event": "geocode",
        "cidade": cidade,
        "nacao": nacao,
        "source": source,
        "cache_hit": cache_hit,
    }, ensure_ascii=False))
```

Reescrever o corpo de `geocode()` (a partir do cache lookup, linha ~174) para registrar a fonte. Substituir o bloco que vai de `cache = _load_cache()` até o `return resultado` final por:

```python
    cache = _load_cache()
    if cache_key in cache:
        _log_geocode(cidade, nacao, source="cache", cache_hit=True)
        return cache[cache_key]

    geonames_result = _try_geonames(cidade, nacao)
    if geonames_result:
        coords, source = geonames_result, "geonames"
    else:
        nominatim_result = _try_nominatim(cidade, nacao)
        coords, source = nominatim_result, "nominatim"

    if coords is None:
        # Diferenciar "todos os provedores indisponíveis" vs "cidade não encontrada"
        # é difícil sem expor estado interno; mensagem cobre ambos os casos.
        raise GeocodingError(
            f"Não foi possível geocodificar '{cidade}"
            f"{', ' + nacao if nacao else ''}'. "
            "Verifique o nome da cidade ou tente novamente em instantes."
        )

    lat, lng = coords
    if lat is None or lng is None:
        raise GeocodingError(
            f"Resposta do geocoder sem coordenadas válidas para '{cidade}'."
        )

    tz_str = _resolve_timezone(lat, lng)

    resultado = {"lat": lat, "lng": lng, "tz_str": tz_str}
    with _cache_lock:
        cache[cache_key] = resultado
        _save_cache()
    _log_geocode(cidade, nacao, source=source, cache_hit=False)
    return resultado
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `.venv-validacao\Scripts\pytest.exe tests/test_geocoder.py -v`
Expected: PASS (16 testes — os anteriores + os 2 novos).

- [ ] **Step 5: Commit**

```bash
git add app/core/geocoder.py tests/test_geocoder.py
git commit -m "feat(geocoder): log estruturado de resolucao (source + cache_hit)"
```

---

## Task 3: Threadpool + telemetria + `isError` no handler (itens #1, #2-servidor, #3)

**Files:**
- Modify: `app/server.py`
- Test: `tests/test_server.py`

**Contexto:** Hoje `_call_tool` ([server.py:269-323](../../../app/server.py#L269-L323)) chama funções síncronas/bloqueantes direto no event loop, devolve erro como conteúdo normal (sem `isError`) e vaza `str(exc)` interno. Vamos: (a) extrair o `if/elif` para um `_dispatch` síncrono e rodá-lo em threadpool; (b) cronometrar e logar cada chamada; (c) marcar falhas com `CallToolResult(isError=True)` e parar de vazar detalhe interno.

- [ ] **Step 1: Write the failing tests**

Adicionar ao final de `tests/test_server.py`:

```python
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
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `docker build -t ceu-natal-test . ; docker run --rm ceu-natal-test python -m pytest tests/test_server.py -v`
Expected: FAIL — `_dispatch` não existe; `_call_tool` ainda retorna `list[TextContent]` (não tupla, não `CallToolResult`).

- [ ] **Step 3: Refactor `app/server.py` — imports e helpers**

No bloco de imports do topo, ajustar/adicionar:

```python
import json
import logging
import os
import time
from typing import Any

import anyio

from mcp.server import Server
from mcp.server.sse import SseServerTransport
from mcp.types import Tool, TextContent, CallToolResult
```

Adicionar, logo após `logging.basicConfig(...)` (linha ~41):

```python
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
```

- [ ] **Step 4: Refactor `app/server.py` — extrair `_dispatch` e reescrever `_call_tool`**

Substituir todo o handler atual `@server.call_tool()` / `async def _call_tool(...)` (linhas ~269-323) por:

```python
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
```

Notas:
- O retorno `(conteudo, resultado)` é o formato `CombinationContent` do SDK: `conteudo` vira `content` (texto PT-BR legível) e `resultado` vira `structuredContent`.
- Falhas retornam `CallToolResult(isError=True)`, que o SDK repassa direto.
- `_log_tool_call` no `finally` cobre todos os caminhos de saída.

- [ ] **Step 5: Run tests to verify they pass**

Run: `docker build -t ceu-natal-test . ; docker run --rm ceu-natal-test python -m pytest tests/test_server.py -v`
Expected: PASS nos 5 novos testes. (Os testes pré-existentes de `/health` e `/tools` continuam passando — `/health` ainda reporta `transporte` que será ajustado na Task 5; o assert stale de `/tools` é corrigido na Task 4.)

- [ ] **Step 6: Commit**

```bash
git add app/server.py tests/test_server.py
git commit -m "feat(server): despacho em threadpool, telemetria por tool e isError em falhas"
```

---

## Task 4: Annotations + structured output + corrigir teste stale (item #4)

**Files:**
- Modify: `app/server.py`
- Test: `tests/test_server.py`

**Contexto:** As tools não declaram `annotations` (todas são read-only; as de cálculo batem em rede → open-world). Vamos anotar todas e adicionar `outputSchema` às duas triviais. Também corrigir o assert stale em [test_server.py:64](../../../tests/test_server.py#L64) que não inclui `sistema_casas`.

- [ ] **Step 1: Write/adjust the failing tests**

Em `tests/test_server.py`, **corrigir** o assert stale na função `test_tools_traz_required_e_properties` (linha ~64):

```python
    assert set(mapa_natal["properties"]) == {"data", "hora", "local", "nome", "sistema_casas"}
```

E adicionar ao final do arquivo:

```python
def test_tools_tem_annotations_read_only(monkeypatch):
    mod = _carregar_app(monkeypatch, api_key="")
    for tool in mod.TOOLS:
        assert tool.annotations is not None, f"{tool.name} sem annotations"
        assert tool.annotations.readOnlyHint is True, f"{tool.name} deveria ser read-only"


def test_tools_de_calculo_sao_open_world(monkeypatch):
    mod = _carregar_app(monkeypatch, api_key="")
    de_calculo = {
        "calcular_mapa_natal", "calcular_sinastria", "calcular_transitos",
        "calcular_progressoes", "calcular_mapa_composto",
    }
    for tool in mod.TOOLS:
        if tool.name in de_calculo:
            assert tool.annotations.openWorldHint is True, f"{tool.name} usa rede → open-world"


def test_tools_triviais_tem_output_schema(monkeypatch):
    mod = _carregar_app(monkeypatch, api_key="")
    por_nome = {t.name: t for t in mod.TOOLS}
    assert por_nome["healthcheck"].outputSchema is not None
    assert por_nome["listar_aspectos_tipos"].outputSchema is not None
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `docker build -t ceu-natal-test . ; docker run --rm ceu-natal-test python -m pytest tests/test_server.py -v`
Expected: FAIL — `tool.annotations` é `None`; `outputSchema` é `None`.

- [ ] **Step 3: Add `ToolAnnotations` import**

No import de tipos do `mcp` em `app/server.py`, acrescentar `ToolAnnotations`:

```python
from mcp.types import Tool, TextContent, CallToolResult, ToolAnnotations
```

- [ ] **Step 4: Add annotations to the 5 calc tools**

Em cada um dos 5 `Tool(...)` de cálculo (`calcular_mapa_natal`, `calcular_sinastria`, `calcular_transitos`, `calcular_progressoes`, `calcular_mapa_composto`), adicionar o campo `annotations` logo após `inputSchema=...` (antes do `)` que fecha o `Tool`). Exemplo no `calcular_mapa_natal` — adicionar após o fechamento do `inputSchema` dict:

```python
        annotations=ToolAnnotations(
            readOnlyHint=True,
            idempotentHint=True,
            openWorldHint=True,  # geocodifica via GeoNames/Nominatim (rede externa)
        ),
```

Repetir o mesmo bloco `annotations=ToolAnnotations(readOnlyHint=True, idempotentHint=True, openWorldHint=True)` nas outras quatro tools de cálculo.

- [ ] **Step 5: Add annotations + outputSchema to the 2 trivial tools**

No `Tool(name="listar_aspectos_tipos", ...)`, substituir o `inputSchema=...` de uma linha pelo bloco com schema de saída e annotations:

```python
        inputSchema={"type": "object", "properties": {}},
        outputSchema={
            "type": "object",
            "required": ["aspectos"],
            "properties": {
                "aspectos": {
                    "type": "array",
                    "items": {"type": "object"},
                },
            },
        },
        annotations=ToolAnnotations(
            readOnlyHint=True,
            idempotentHint=True,
            openWorldHint=False,
        ),
```

No `Tool(name="healthcheck", ...)`:

```python
        inputSchema={"type": "object", "properties": {}},
        outputSchema={
            "type": "object",
            "required": ["status", "versao", "transporte"],
            "properties": {
                "status": {"type": "string"},
                "versao": {"type": "string"},
                "transporte": {"type": "string"},
            },
        },
        annotations=ToolAnnotations(
            readOnlyHint=True,
            idempotentHint=True,
            openWorldHint=False,
        ),
```

> Validação cruzada: como `_dispatch` devolve `{"status","versao","transporte"}` para `healthcheck` e `{"aspectos": [...]}` para `listar_aspectos_tipos`, e o `_call_tool` devolve a tupla `(conteudo, resultado)`, o SDK validará `resultado` contra esses `outputSchema`. Os formatos batem.

- [ ] **Step 6: Run tests to verify they pass**

Run: `docker build -t ceu-natal-test . ; docker run --rm ceu-natal-test python -m pytest tests/test_server.py -v`
Expected: PASS (incluindo o `test_tools_traz_required_e_properties` corrigido e os 3 novos). Rodar a suíte inteira para garantir que `healthcheck`/`listar_aspectos_tipos` ainda respondem com o output válido: `docker run --rm ceu-natal-test python -m pytest tests/ -v`.

- [ ] **Step 7: Commit**

```bash
git add app/server.py tests/test_server.py
git commit -m "feat(server): annotations (readOnly/openWorld) + outputSchema nas tools triviais"
```

---

## Task 5: Transporte Streamable HTTP em paralelo ao SSE (item #5)

**Files:**
- Modify: `app/server.py`
- Modify: `requirements.txt`
- Test: `tests/test_server.py`

**Contexto:** SSE (`SseServerTransport`, [server.py:355](../../../app/server.py#L355)) é o transporte deprecado de 2024-11. Vamos adicionar o Streamable HTTP em `/mcp` mantendo o SSE como legado. Proteção anti-DNS-rebinding do SDK vem ligada por padrão com allowlist vazia (bloquearia o host de produção atrás do Traefik), então será controlada por env `MCP_ALLOWED_HOSTS`.

- [ ] **Step 1: Bump do piso do `mcp`**

Em `requirements.txt`, trocar a primeira linha:

```
mcp>=1.9.0
```

(Streamable HTTP estável; ambiente local já roda 1.27.1.)

- [ ] **Step 2: Write the failing tests**

Adicionar ao final de `tests/test_server.py`:

```python
def test_rota_mcp_existe(monkeypatch):
    mod = _carregar_app(monkeypatch, api_key="")
    paths = {getattr(r, "path", None) or getattr(r, "path_format", None) for r in mod.app.routes}
    assert any(p and p.startswith("/mcp") for p in paths), f"sem rota /mcp em {paths}"


def test_health_reporta_dois_transportes(monkeypatch):
    mod = _carregar_app(monkeypatch, api_key="")
    body = TestClient(mod.app).get("/health").json()
    assert "streamable-http" in body["transporte"]
    assert "sse" in body["transporte"]


def test_security_settings_desliga_rebinding_sem_allowed_hosts(monkeypatch):
    monkeypatch.delenv("MCP_ALLOWED_HOSTS", raising=False)
    mod = _carregar_app(monkeypatch, api_key="")
    assert mod._security.enable_dns_rebinding_protection is False


def test_security_settings_liga_rebinding_com_allowed_hosts(monkeypatch):
    monkeypatch.setenv("MCP_ALLOWED_HOSTS", "astrologia-mcp.gustavocancado.com.br")
    mod = _carregar_app(monkeypatch, api_key="")
    assert mod._security.enable_dns_rebinding_protection is True
    assert "astrologia-mcp.gustavocancado.com.br" in mod._security.allowed_hosts
```

- [ ] **Step 3: Run tests to verify they fail**

Run: `docker build -t ceu-natal-test . ; docker run --rm ceu-natal-test python -m pytest tests/test_server.py -k "mcp or transporte or rebinding" -v`
Expected: FAIL — rota `/mcp` inexistente; `transporte` ainda é `"sse"`; `_security` inexistente.

- [ ] **Step 4: Add imports e session manager**

No topo de `app/server.py`, adicionar imports:

```python
import contextlib

from mcp.server.streamable_http_manager import StreamableHTTPSessionManager
from mcp.server.transport_security import TransportSecuritySettings
```

E em starlette, garantir o import do `Mount` (já existe na linha de routing) — nenhuma mudança ali.

- [ ] **Step 5: Configurar security settings + session manager**

Logo após a criação do `sse_transport = SseServerTransport("/messages/")` (linha ~355), adicionar:

```python
# Streamable HTTP: proteção anti-DNS-rebinding é ligada por env.
# Atrás de proxy confiável (Traefik) e com auth aberta, default é desligar
# (espelha o comportamento do SSE legado, que não valida Host).
_allowed_hosts = [h.strip() for h in os.getenv("MCP_ALLOWED_HOSTS", "").split(",") if h.strip()]
if _allowed_hosts:
    _security = TransportSecuritySettings(
        enable_dns_rebinding_protection=True,
        allowed_hosts=_allowed_hosts,
    )
else:
    _security = TransportSecuritySettings(enable_dns_rebinding_protection=False)

session_manager = StreamableHTTPSessionManager(
    app=server,
    json_response=False,
    stateless=False,
    security_settings=_security,
)


async def _handle_streamable_http(scope, receive, send) -> None:
    await session_manager.handle_request(scope, receive, send)


@contextlib.asynccontextmanager
async def _lifespan(app):
    async with session_manager.run():
        yield
```

- [ ] **Step 6: Atualizar `/health` e registrar a rota `/mcp` + lifespan**

Na função `_health` (linha ~366), trocar o valor de `transporte`:

```python
        "transporte": "streamable-http+sse",
```

Na construção do `app = Starlette(...)` (linha ~396), adicionar a rota `/mcp` e o `lifespan`:

```python
app = Starlette(
    debug=False,
    routes=[
        Route("/health", endpoint=_health, methods=["GET"]),
        Route("/tools", endpoint=_list_tools_http, methods=["GET"]),
        Route("/sse", endpoint=_handle_sse, methods=["GET"]),
        Mount("/messages/", app=sse_transport.handle_post_message),
        Mount("/mcp", app=_handle_streamable_http),
    ],
    middleware=[Middleware(APIKeyMiddleware)],
    lifespan=_lifespan,
)
```

> Nota: os testes existentes usam `TestClient(mod.app)` sem `with`, então o `lifespan` (que entra em `session_manager.run()`) não é acionado — eles só batem em `/health` e `/tools`. Sem regressão. O `session_manager.run()` só roda sob uvicorn em produção e em testes que usem `with TestClient(...)`.

- [ ] **Step 7: Run tests to verify they pass**

Run: `docker build -t ceu-natal-test . ; docker run --rm ceu-natal-test python -m pytest tests/test_server.py -v`
Expected: PASS (incluindo os 4 novos). Atualizar também o assert de transporte no teste antigo `test_health_publico_sem_auth` se ele checar `== "sse"`:

```python
    assert "sse" in body["transporte"]
```

(Trocar a igualdade estrita por `in` para refletir o valor combinado.)

- [ ] **Step 8: Smoke test do handshake Streamable HTTP no container**

```bash
docker run --rm -d --name ceu-smoke -p 8001:8000 ceu-natal-test
# initialize handshake (Streamable HTTP aceita POST em /mcp)
curl -s -X POST http://localhost:8001/mcp \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -d '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2025-03-26","capabilities":{},"clientInfo":{"name":"smoke","version":"0"}}}'
docker stop ceu-smoke
```
Expected: resposta JSON-RPC com `result.serverInfo.name == "ceu-natal"` (e header `mcp-session-id`). Não pode vir erro de host/rebinding.

- [ ] **Step 9: Commit**

```bash
git add app/server.py requirements.txt tests/test_server.py
git commit -m "feat(server): transporte Streamable HTTP em /mcp (dual com SSE legado)"
```

---

## Task 6: Documentação + deploy + validação (rollout do item #5)

**Files:**
- Modify: `docs/CONECTAR-CLAUDE-AI.md`
- Modify: `README.md`
- Modify: `CLAUDE.md`
- Modify: `docs/validacao.md`

**Contexto:** Publicar o `/mcp` como endpoint recomendado, manter `/sse` documentado como legado durante o grace period, disparar deploy no Coolify e validar.

- [ ] **Step 1: Documentar o endpoint `/mcp`**

Em `CLAUDE.md`, na tabela de endpoints HTTP, adicionar a linha do Streamable HTTP (acima de `/sse`):

```markdown
| `/mcp` | POST/GET | endpoint MCP Streamable HTTP (recomendado) |
```

E marcar a linha `/sse` como legado:

```markdown
| `/sse` | GET | handshake MCP via SSE (legado — em descontinuação) |
```

Em `docs/CONECTAR-CLAUDE-AI.md` e `README.md`, onde a URL de conexão aparece como `.../sse`, adicionar nota de que o endpoint recomendado passou a ser `https://astrologia-mcp.gustavocancado.com.br/mcp` (Streamable HTTP) e que `/sse` segue funcionando temporariamente para clientes legados.

- [ ] **Step 2: Commit das docs**

```bash
git add CLAUDE.md README.md docs/CONECTAR-CLAUDE-AI.md
git commit -m "docs: publica endpoint /mcp (Streamable HTTP) e marca /sse como legado"
```

- [ ] **Step 3: Push**

```bash
git push origin main
```

- [ ] **Step 4: Configurar env de produção no Coolify (antes do deploy)**

No app `ceu-natal` (projeto `astrologia`, uuid `ejbfwl0yfego72kk5n2us1gh`), definir a env opcional:

```
MCP_ALLOWED_HOSTS=astrologia-mcp.gustavocancado.com.br
```

> Se preferir manter o comportamento aberto (sem validação de Host, igual ao SSE), **não** defina a variável — o default desliga a proteção. Definir é o caminho mais seguro e é o recomendado já que o FQDN é fixo.

- [ ] **Step 5: Disparar deploy**

```bash
curl -X POST \
  -H "Authorization: Bearer $COOLIFY_TOKEN" \
  "http://5.78.199.192:8000/api/v1/deploy?uuid=ejbfwl0yfego72kk5n2us1gh"
```
(Token em `~/.claude/CLAUDE.md`.)

- [ ] **Step 6: Validar produção**

```bash
curl -s https://astrologia-mcp.gustavocancado.com.br/health
curl -s https://astrologia-mcp.gustavocancado.com.br/tools | jq '.count'
curl -s -X POST https://astrologia-mcp.gustavocancado.com.br/mcp \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -d '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2025-03-26","capabilities":{},"clientInfo":{"name":"validacao","version":"0"}}}'
```
Expected:
- `/health` → `"transporte":"streamable-http+sse"`.
- `/tools` → `7`.
- `/mcp` → JSON-RPC com `result.serverInfo.name == "ceu-natal"`, sem erro de host.

- [ ] **Step 7: Reconfigurar o conector no Claude.ai**

Trocar a URL do conector custom `ceu-natal`/`astrologia-mcp` de `.../sse` para `.../mcp` e confirmar que as 7 tools aparecem e que `calcular_mapa_natal` responde para um caso conhecido (ex.: data/hora/local de BH).

- [ ] **Step 8: Atualizar `docs/validacao.md`**

Registrar: data da validação, que o transporte Streamable HTTP (`/mcp`) está no ar em paralelo ao SSE legado, que `MCP_ALLOWED_HOSTS` está setado, e que a telemetria por tool (`event:"tool_call"`) e do geocoder (`event:"geocode"`) está saindo nos logs do Coolify. Commit:

```bash
git add docs/validacao.md
git commit -m "docs: valida transporte Streamable HTTP e telemetria em producao"
git push origin main
```

- [ ] **Step 9 (futuro, fora deste ciclo): remover o SSE legado**

Após ~2 semanas com o conector estável em `/mcp`, abrir tarefa separada para remover `SseServerTransport`, as rotas `/sse` + `/messages/`, e simplificar `/health` para `"transporte":"streamable-http"`. **Não fazer agora.**

---

## Self-Review

**Cobertura do diagnóstico (6 itens):**
- #1 bloqueio do event loop → Task 3 (threadpool via `anyio.to_thread.run_sync`). ✅
- #2 telemetria objetiva → Task 2 (geocoder: source/cache_hit) + Task 3 (servidor: tool/status/duration_ms). ✅ (logs estruturados, conforme decisão.)
- #3 `isError` + parar de vazar `detalhe` → Task 3 (`_resultado_erro` com `isError=True`, mensagem genérica). ✅
- #4 annotations + outputSchema → Task 4 (annotations em todas; outputSchema nas 2 triviais; structuredContent em todas via tupla). ✅
- #5 SSE → Streamable HTTP → Tasks 5 e 6 (dual transport + rollout). ✅
- #6 rate-limit Nominatim → Task 1. ✅
- Bônus: teste stale corrigido (Task 4, Step 1).

**Placeholder scan:** sem TBD/TODO; todo passo de código traz o código real. ✅

**Consistência de tipos/nomes:** `_dispatch(name, arguments) -> dict` (Task 3) é consumido por `_call_tool` via `anyio.to_thread.run_sync(_dispatch, name, arguments)` (mesma assinatura). `_resultado_erro` retorna `CallToolResult(isError=True)` consistente com os asserts dos testes (`.isError`, `.content[0].text`). `_security` (Task 5) é referenciado pelos testes com o mesmo nome. `transporte: "streamable-http+sse"` aparece igual em `_dispatch` (healthcheck), `_health` e nos asserts. ✅

**Decisões deliberadas registradas (não são cortes silenciosos):** outputSchema estrito só nas 2 tools triviais; SSE mantido em paralelo; telemetria só em logs. Todas alinhadas com o dono.
