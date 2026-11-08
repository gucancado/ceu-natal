# CLAUDE.md

Orientação para quem (pessoa ou agente) vai mexer neste repositório.

## O que é

Servidor **MCP** (Model Context Protocol) de astrologia em português: calcula
mapas, não interpreta, não guarda dados de pessoas. Transporte Streamable HTTP
em `/mcp/`. O site de apresentação mora em
`web/` e é um app separado.

## Stack

- Python 3.11, Starlette + uvicorn, MCP SDK 1.x (`mcp<2`)
- Kerykeion 5.x (Swiss Ephemeris via pyswisseph) para o cálculo
- GeoNames com Nominatim de reserva, cache persistente de coordenadas
- Tools rodam em threadpool (`anyio.to_thread`); log JSON por chamada
- Site: Next.js 16 + `@beeads/ui` em `web/`

## Mapa de pastas

| Pasta | Conteúdo |
|-------|----------|
| `app/config.py` | `Settings` imutável; todas as envs do servidor (`Settings.do_ambiente()`) |
| `app/server.py` | `create_app(settings)`, schemas das tools (`TOOLS`), rotas HTTP, auth, limites |
| `app/core/` | cálculo: `entrada.py` (entrada única de nascimento), `kerykeion.py`, `aspectos.py`, `sintese.py`, `geocoder.py`, `periodos.py`, `revolucoes.py`, `formatter.py`, `validators.py`, `ratelimit.py` |
| `app/tools/` | um handler por técnica |
| `app/static/llms.txt` | texto servido em `/llms.txt` |
| `tests/` | pytest; fixtures fictícias em `tests/conftest.py` |
| `scripts/` | `deploy.py` (deploy manual), `validacao_producao.py` |
| `docs/` | guia de conexão, distribuição, validação em produção e política de privacidade (`docs/legal/`; os termos ficam em `web/src/content/legal/`) |
| `web/` | site Next.js |

## Tools (`app/tools/`)

| Tool | Arquivo |
|------|---------|
| `calcular_mapa_natal` | `app/tools/mapa_natal.py` |
| `calcular_sinastria` | `app/tools/sinastria.py` |
| `calcular_transitos` | `app/tools/transitos.py` |
| `calcular_progressoes` | `app/tools/progressoes.py` |
| `calcular_mapa_composto` | `app/tools/composto.py` |
| `calcular_revolucao_solar` | `app/tools/revolucao_solar.py` |
| `calcular_revolucao_lunar` | `app/tools/revolucao_lunar.py` |
| `listar_aspectos_tipos` | inline em `app/server.py` |
| `healthcheck` | inline em `app/server.py` |

## Convenções

- Português em comentários, docstrings, mensagens de erro e commits
  (Conventional Commits: `fix(core): ...`, `docs: ...`).
- Todo `.py` de `app/` e `scripts/` começa com
  `# SPDX-License-Identifier: AGPL-3.0-or-later` e uma docstring.
- Erro para o usuário: `ValueError`/`GeocodingError` com mensagem clara; o
  servidor devolve `{"erro": "..."}` com `isError`. Exceção genérica vira
  "Erro interno do servidor." sem vazar detalhe.
- Lógica nova vai em `app/core/` ou `app/tools/`; `app/server.py` só registra
  e despacha. Entrada de pessoa/natal passa sempre por `EntradaNascimento`.
- Testes com Kerykeion passam `lat`/`lng`/`tz_str` direto (sem rede).
- Dependências de runtime em `requirements.in` (com tetos de major) e lock em
  `requirements.txt`, gerado por
  `uv pip compile requirements.in -o requirements.txt --python-version 3.11`.
  Dependências de desenvolvimento em `requirements-dev.txt`.

## Testes

- **Windows:** só a parte que não importa Kerykeion (pyswisseph não compila):
  `python -m pytest tests/test_server.py tests/test_ratelimit.py tests/test_server_json.py tests/test_deploy_script.py tests/test_periodos.py tests/test_validators.py -q`
- **Linux, WSL ou CI:** suíte completa com
  `pip install -r requirements-dev.txt`, depois `ruff check .`, `mypy app`
  e `python -m pytest -q`.
- **Site:** `cd web && pnpm install && pnpm typecheck && pnpm test && pnpm build`.

## O que não propor

- Endpoints REST de cálculo ou FastAPI: o servidor é MCP sobre Starlette.
  Swagger/OpenAPI também não; o equivalente é o `inputSchema` de cada tool.
- Reimplementar tools que já existem (tabela acima).
- Tirar os tetos de major do `requirements.in`: uma major nova no PyPI já
  derrubou o deploy sem mudança de código. Migrar para `mcp` 2.x é tarefa
  própria.
- Subir Kerykeion ou Python sem discussão: pyswisseph é frágil em wheels.
- Aceitar a chave de API por query string: só `Authorization: Bearer`.
- Deploy automático no push: publicar é decisão explícita (`scripts/deploy.py`).
