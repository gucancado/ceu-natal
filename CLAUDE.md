# CLAUDE.md — Orientação para agentes LLM

Leia este arquivo **antes** de propor qualquer mudança no projeto. Ele
existe pra eliminar planos baseados em premissas desatualizadas.

---

## O que é

Servidor **MCP** (Model Context Protocol) de astrologia, exposto via
**SSE sobre HTTP**. Stack:

- Python 3.11 + Starlette + uvicorn
- MCP SDK (`mcp>=1.2.0`) com `SseServerTransport`
- Kerykeion 5.x (Swiss Ephemeris) para cálculo astrológico
- GeoNames + Nominatim com cache persistente para geocodificação

**URL produção:** https://ceu-natal-api.pu5h6p.easypanel.host

**Endpoints HTTP:**

| Path | Tipo | Descrição |
|------|------|-----------|
| `/sse` | GET | handshake MCP via SSE |
| `/messages/` | POST | canal de mensagens MCP |
| `/health` | GET | healthcheck (público) |
| `/tools` | GET | lista as tools registradas (debug, autenticado) |

---

## O que NÃO propor

- ❌ **Não é mais uma API REST FastAPI.** A migração aconteceu em
  abril/2026 (commit `574a881` — "feat: migra REST API para servidor MCP
  via SSE"). Não recriar `POST /natal-chart`, `POST /sinastria`,
  `POST /transitos` ou outros endpoints REST de cálculo.
- ❌ **Não usar FastAPI.** Starlette é o framework HTTP, e só hospeda
  o transporte MCP + endpoints utilitários (`/health`, `/tools`).
- ❌ **Não pedir Swagger / OpenAPI.** O equivalente em MCP é o
  `inputSchema` por Tool e o `GET /tools`.
- ❌ **Não reimplementar tools que já existem** (ver lista abaixo).
- ❌ **Não atualizar versões de Kerykeion ou Python sem discussão.**
  Pyswisseph (dependência transitiva) é frágil em build de wheels.

---

## Tools já implementadas em `app/tools/`

| Tool | Arquivo | Status em produção |
|------|---------|---------------------|
| `calcular_mapa_natal` | [app/tools/mapa_natal.py](app/tools/mapa_natal.py) | ✅ deployada |
| `calcular_sinastria` | [app/tools/sinastria.py](app/tools/sinastria.py) | ✅ deployada |
| `calcular_transitos` | [app/tools/transitos.py](app/tools/transitos.py) | ⏳ aguardando deploy |
| `calcular_progressoes` | [app/tools/progressoes.py](app/tools/progressoes.py) | ⏳ aguardando deploy |
| `calcular_mapa_composto` | [app/tools/composto.py](app/tools/composto.py) | ⏳ aguardando deploy |
| `listar_aspectos_tipos` | inline em [app/server.py](app/server.py) | ✅ deployada |
| `healthcheck` | inline em [app/server.py](app/server.py) | ✅ deployada |

**Como verificar quais tools estão deployadas agora:**

```bash
curl -s https://ceu-natal-api.pu5h6p.easypanel.host/tools | jq '.tools[].name'
```

Ou, se um cliente MCP estiver conectado, listar as tools via protocolo.

---

## Estado atual (verificável)

- **Branch ativa:** `main`
- **Deploy não é automático** — push pra `main` não publica em produção.
  É necessário clicar **Implantar** em
  https://pu5h6p.easypanel.host/projects/ceu-natal/app/api
- **Diferença atual entre `main` e produção:** as 3 tools da Fase 2
  (`calcular_transitos`, `calcular_progressoes`, `calcular_mapa_composto`)
  estão em `main` desde o commit `8aa5c1e` mas ainda não foram
  reimplantadas. Antes de planejar trabalho novo nessas tools, vale
  pedir o redeploy.
- **Auth:** modo aberto (`MCP_API_KEY=` vazia em produção). Decisão
  consciente — Claude.ai web só aceita OAuth para conector custom, e
  ainda não implementamos OAuth no servidor.

---

## Onde olhar pra entender mais

| Quero saber... | Leia... |
|----------------|---------|
| Como conectar como usuário | [docs/CONECTAR-CLAUDE-AI.md](docs/CONECTAR-CLAUDE-AI.md) |
| Visão geral / parâmetros / exemplos | [README.md](README.md) |
| Estado real validado em produção | [docs/validacao.md](docs/validacao.md) |
| Decisões arquiteturais e histórico | `git log --oneline` (commits são detalhados) |

---

## Convenções de código

- **Idioma:** comentários, docstrings e mensagens de erro em português
- **Type hints:** sempre, estilo `Optional[str]`, `dict[str, Any]`
- **Estilo:** aspas duplas, indentação 4 espaços, sem black/ruff
  configurados — manter o que já está
- **Erros pro usuário final:** levantar `ValueError` com mensagem PT-BR
  clara — cai no `except ValueError` do `_call_tool` em
  [app/server.py](app/server.py) e vira `{"erro": "..."}` no retorno
  da tool MCP
- **Lógica nova:** mora em `app/core/` (cálculo) ou `app/tools/`
  (handler MCP). Não inflar `app/server.py` — ele só registra schemas
  e despacha
- **Testes:** padrão `pytest`, fixtures em `tests/conftest.py`. Casos
  com Kerykeion devem passar lat/lng/tz_str diretos pra evitar
  dependência de rede

---

## Workflow padrão de mudança

1. Editar código localmente
2. Rodar `pytest -v` (subset que não exige Kerykeion roda em qualquer
   ambiente; suite completa exige Linux + pyswisseph compilado)
3. Commit em `main` (projeto pessoal — sem PR formal)
4. Push para `origin/main`
5. **Clicar Implantar no EasyPanel** (deploy manual)
6. Validar com `curl /health` e `curl /tools`
7. Atualizar `docs/validacao.md` se for mudança que afete contrato
   ou estabilidade

---

## Como bootstrappar uma nova sessão de planejamento no Claude.ai

Cole o snippet abaixo no início da conversa antes de pedir um plano:

> Antes de propor mudanças no projeto ceu-natal, leia (via web fetch):
>
> - https://github.com/gucancado/ceu-natal/blob/main/CLAUDE.md
> - https://github.com/gucancado/ceu-natal/blob/main/docs/validacao.md
> - https://github.com/gucancado/ceu-natal/blob/main/README.md
>
> Confirme o estado atual antes de propor implementação.

Sem isso, o Claude.ai opera com base em conversas antigas e pode
propor regressões (exemplo real: pedir reimplementação de
`calcular_transitos` como endpoint REST FastAPI, ignorando que a tool
MCP equivalente já existe).
