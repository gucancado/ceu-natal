# Relatório de validação — ceu-natal

## 2026-11-05 — 2.2.1: dependências (`main` @ `4bbb44d`)

`timezonefinder` 6.5.2 → 8.3.0 (última que roda no Python 3.11; a 9.x exige 3.12)
libera `cffi` 2.1.1 e `cryptography` 50.0.2, fechando os 14 alertas do Dependabot
abertos ao ligar os alertas na 2.2.0. A auditoria da CI roda sem `--ignore-vuln`.
Só o servidor foi publicado; o site não mudou.

| Checagem | Resultado observado |
|---|---|
| Suíte completa (WSL), `pip-audit --strict`, ruff, mypy, CI | 350 passed; nenhuma vulnerabilidade; CI verde |
| Deploy do servidor | `finished`; `GET /health` → `versao 2.2.1`; app `running:healthy` |
| `POST /mapa-rapido` com cidade fora do cache (Ouro Preto, MG) | `200`; `local_resolvido {lat -20.39484, lng -43.50517, fuso America/Sao_Paulo}` — GeoNames + `TimezoneFinder` 8.3.0 no container novo |
| Logs do container novo | sem traceback nem aviso no arranque |
| `/status` do site | mostra 2.2.1 (lê o `/health` real) |
| Dependabot | 0 alertas abertos após o push em `main`; PR #6 (timezonefinder 9.2.0, Python 3.12) fechado |

## 2026-11-05 — 2.2.0: auditoria pré-divulgação (`main` @ `4be2f8c`)

Branch `auditoria/pre-divulgacao` (20 commits) mergeada fast-forward em `main`;
tag `v2.2.0` + release no GitHub com o trecho 2.2.0 do CHANGELOG; metadados do
repositório (descrição, homepage, 10 tópicos, wiki desligada, alertas do
Dependabot, correções automáticas e relato privado de vulnerabilidade ligados).
Servidor MCP e site publicados pelo `scripts/deploy.py` (uuids em
`scripts/deploy.env`, fora do repo).

| Checagem | Resultado observado |
|---|---|
| Suíte completa (WSL) e CI da branch | 350 passed; ruff, mypy e pip-audit limpos; CI verde |
| Deploy do servidor | `finished`; `GET /health` → `versao 2.2.0`, `streamable-http+sse`, `site` = mistico, limites 30/600 e mapa-rápido 6/120 |
| `GET /tools` | 9 tools (`calcular_mapa_natal` … `healthcheck`) |
| `POST /mapa-rapido` com `Origin` do site (12/03/1990 14:30, Belo Horizonte) | `200`, `Access-Control-Allow-Origin` = site, `local_resolvido {lat -19.92083, lng -43.93778, fuso America/Sao_Paulo}`; geocode via GeoNames e depois `cache_hit` |
| `POST /mapa-rapido` com corpo de 5 KB | `413` (teto 4096 bytes); log `status: body_too_large` |
| `?api_key=` na query string | ignorado (prod sem chave, `auth_required: false`; o transporte responde `406` sem `Accept`) |
| Deploy do site, 1ª tentativa | `failed` + rollback: o healthcheck do Coolify roda `curl`/`wget` dentro do container e a imagem `node:24-slim` não tem nenhum (o `curl` saiu na 2.2.0). Healthcheck do Coolify desligado no app; vale o `HEALTHCHECK` do Dockerfile (`node -e fetch`) |
| Deploy do site, 2ª tentativa | `finished`; app `running:healthy` pelo `HEALTHCHECK` do Dockerfile; Next "Ready" |
| Cabeçalhos do site | `Content-Security-Policy` (`default-src 'self'`, `connect-src` só o servidor MCP, `frame-ancestors 'none'`), `Referrer-Policy`, `Strict-Transport-Security`, `X-Content-Type-Options: nosniff`; `X-Powered-By` ausente |
| `/privacidade`, home | Versão 3 da política; email de contato em texto nas duas páginas |
| `/status`, `/conectar`, `/termos`, `/llms.txt`, `/sitemap.xml`, `/robots.txt`, `/opengraph-image` | `200`; `/status` mostra 2.2.0; rota inexistente → `404` |
| Logs do servidor após o deploy | sem traceback nas rotas novas; 2 ocorrências de `AssertionError: Unexpected message … http.response.start` ao encerrar sessão do transporte SSE legado (`handle_sse` devolve `Response()` depois do stream, sob `BaseHTTPMiddleware`) — código igual ao da 2.1.0, efeito só no log; follow-up |
| Cache do geocoder com o user `app` (sem root) | `GEOCODER_CACHE_PATH` não setada e sem volume persistente → cache efêmero dentro do container; nenhum aviso de escrita no log |

## 2026-11-04 — F2: site mistico.gustavocancado.com.br (`produto/f2` @ `9730000`)

Landing Next.js 16.4.4 em `web/` (Tasks 1–7 do plano F2) publicada no Coolify
como app separado (build pack
dockerfile, base directory `/web`, porta 3000, domínio
`https://mistico.gustavocancado.com.br`, envs `NEXT_PUBLIC_SITE_URL`/
`NEXT_PUBLIC_MCP_URL`/`NEXT_PUBLIC_REPO_URL` em prod e preview; a API do
Coolify 4.6 não aceita mais `is_build_time`, as envs valem no build por
padrão). O app provisório nginx foi apagado. O app
aponta para a branch `produto/f2` até o merge; depois do merge, trocar
`git_branch` para `main` e redeployar.

| Checagem | Resultado observado |
|---|---|
| Deploy do commit 73e63d6 | `failed`: build Docker ok e Next "Ready", mas o healthcheck do Coolify roda `curl`/`wget` no container e `node:24-slim` não tem nenhum → rollback |
| Deploys de 73e63d6 e b7ca167 | `finished` com o healthcheck do Coolify desligado (validação intermediária) |
| Deploy de 9730000 (`curl` na imagem, healthcheck do Coolify ligado) | `finished`; app `running:healthy` |
| `GET /`, `/conectar`, `/conectar/<7 guias>`, `/privacidade`, `/termos`, `/status` | `200 text/html`; `/status` mostra `No ar · versão 2.1.0 · limites 30/600` lendo o `/health` real |
| `GET /llms.txt`, `/llms-full.txt` | `200 text/plain; charset=utf-8`, `cache-control: public, max-age=3600` |
| `GET /sitemap.xml` (11 URLs, sem `/status`), `/robots.txt`, `/opengraph-image` | `200` (`application/xml`, `text/plain`, `image/png` 44 KB) |
| `<head>` da home | `<title>Céu Natal</title>`, canonical `https://mistico.gustavocancado.com.br`, `og:title`, `og:image`, JSON-LD `SoftwareApplication`; guia: `Como conectar no Claude.ai · Céu Natal` |
| TLS | Let's Encrypt (Traefik), válido até 2027-02-01 |
| Layout via CDP (Chrome headless) em 360 px claro/escuro e 1280 claro | `scrollWidth == clientWidth` (sem rolagem horizontal da página; tabela de planos, abas e `<pre>` rolam dentro de si); temas `html.light`/`html.dark` aplicam |
| Servidor MCP: env `PUBLIC_SITE_URL=https://mistico.gustavocancado.com.br` (prod e preview) + restart | `/health` → `"site":"https://mistico.gustavocancado.com.br"` em ~85 s; `GET /` → `302` para o site |
| Conector do claude.ai (`healthcheck`) | `versao 2.1.0`, `streamable-http+sse` |
| `app/static/llms.txt` do servidor com `{site_url}` nos links de política e guia | ainda não no ar: o servidor faz deploy de `main`; entra no deploy após o merge |

## 2026-11-03 — starlette 1.x (`main` @ `3c9c5db`)

Teto do starlette subido de `<1.0.0` para `>=1.3.1,<2.0.0` (decisão do mantenedor)
e os 5 `--ignore-vuln` do starlette removidos da CI (PYSEC-2026-161/248/249/
2280/2281; as duas primeiras envenenam `request.url.path` pelo header `Host`,
critério de rota pública do `APIKeyMiddleware`). CI verde (`testes` +
`auditoria` sem os ignores). Deploy `finished`.

| Checagem | Resultado observado |
|---|---|
| Suíte local (Windows, 5 arquivos) com starlette 1.10.0 | 67 passed em 21 s; 1 aviso: `TestClient` com `httpx` depreciado, usar `httpx2` |
| Log do build no Coolify | `starlette-1.10.0`, `sse_starlette-3.6.0`, `mcp-1.30.0`, `uvicorn-0.54.0` |
| `GET /health` | `"versao":"2.1.0"`, `"auth_required":false`, limites 30/600 |
| `GET /` e `GET /llms.txt` (rotas públicas do middleware) | `302` para o GitHub; `# Céu Natal` |
| `POST /mcp/` sem sessão | `400` do protocolo (não `401` do middleware) |
| Conector do claude.ai (`healthcheck`) | `versao 2.1.0`, `streamable-http+sse` |

## 2026-11-03 — 2.1.0: limite de taxa, llms.txt, CI

Merge fast-forward de `produto/f1` em `main` (head `7f6f039`, CI verde), envs
`PUBLIC_SITE_URL` e `PUBLIC_MCP_URL` criadas no Coolify (prod e preview),
health check do Coolify ligado (`/health`, porta 8000; confirmado via API:
`True /health`) e deploy com `scripts/deploy.py`: `status: finished`, exit 0.

| Checagem | Resultado observado |
|---|---|
| `GET /health` | `"versao":"2.1.0"`, `"site":"https://github.com/gucancado/ceu-natal"`, `"limites":{"por_sessao_por_min":30,"global_por_min":600}` |
| `GET /` | `302` para `https://github.com/gucancado/ceu-natal` |
| `GET /llms.txt` | primeira linha `# Céu Natal`, acento íntegro |
| Smoke do limite, 35 chamadas seguidas de `healthcheck` numa sessão MCP | **nenhuma barrada** (ver nota) |
| Smoke do limite, 60 chamadas | primeiro barrado na chamada **48**, com `isError` e a mensagem de espera |
| Conector do claude.ai (`healthcheck` → `versao 2.1.0`) | executado pelo orquestrador após o deploy: `versao 2.1.0` (clientes já configurados não quebraram) |

Nota sobre o smoke: o balde da sessão é de 30 tokens e recarrega 0,5/s. Pela
internet cada chamada leva algumas centenas de ms, então a recarga durante a
rajada empurra o primeiro bloqueio para depois da chamada 31 (a chamada 31
só é barrada com chamadas quase instantâneas, como nos testes locais). O
limite está ativo e funciona; o número exato depende da latência do cliente.

## 2026-07-29 — Correções pós-teste das revoluções

Bateria de 17 checagens executada por um agente contra produção: **17/17 verdes
no cálculo**, zero erro astronômico. As correções abaixo saíram do relatório
crítico do mesmo agente.

| Achado | Veredito | Ação |
|---|---|---|
| `ano` anterior ao nascimento era aceito | **bug confirmado** — um `ano` anterior ao do nascimento devolvia mapa sem erro | `validar_ano_revolucao` agora recebe `ano_nascimento` e barra |
| Lunar devolve o próximo ciclo, não o vigente | procedente — semântica oposta à da solar, e "como está meu mês?" com a data de hoje devolvia o mês que ainda não começou | bloco `ciclo_em_curso` no resultado + descrição da tool reescrita. A semântica de busca foi mantida (decisão de design) |
| `vigencia` sem timezone | procedente — datetime naive podia ser lido como hora local | renomeado para `inicio_utc` / `fim_aproximado_utc`, com `+00:00` explícito |
| Método do `fim_aproximado` não documentado | procedente | campos `duracao_dias` e `nota` explicando que é o início + duração média do ciclo (erro de 20–30 min) |
| `destaques` com shape diferente nas duas tools | procedente — `lua_na_casa` duplicava `lua_revolucao.casa_revolucao`, e a solar não trazia `sol_revolucao` | `montar_destaques` unificado: os dois luminares sempre presentes + `luminar_principal` |
| Conjunção definicional encabeçava a lista de aspectos | procedente — sol×sol orbe 0 é a definição da técnica, não um achado, e a lista é ordenada por orbe | campo `definicional: true` no aspecto |
| Descrição de `ano` não cobria bordas | procedente | reescrita cobrindo 29/02 e nascidos no começo de janeiro |
| Limiar de `exato` não exposto | procedente | `ORBE_EXATO` extraído e publicado em `listar_aspectos_tipos` |
| Acentuação inconsistente nas `nota` | procedente | notas de método acentuadas |
| **`local` natal cairia em Greenwich silenciosamente** | **refutado** | o gate existe e funciona: natal com `hora` e sem `local` retorna `isError` com "Revoluções exigem o local de nascimento". O teste que gerou a suspeita omitiu só a `hora` |
| `sintese.hemisferio_horizontal` desempata em silêncio (`leste >= oeste` → "Leste") | procedente, **fora de escopo** | código preexistente em `app/core/sintese.py`, afeta as 6 tools que devolvem síntese. Mudar quebraria contrato — decidir separadamente |

Testes: 30 casos em `tests/test_periodos.py` (rodam no Windows), incluindo
`ciclo_anterior` e o gate de ano vs. nascimento.

### Incidente de deploy — `mcp` 2.0.0

O primeiro deploy destas correções **falhou**, e não por causa do código:

```
File "/app/app/server.py", line 456, in <module>
    @server.list_tools()
AttributeError: 'Server' object has no attribute 'list_tools'
```

`requirements.txt` trazia `mcp>=1.9.0` sem teto de major. O SDK 2.0.0 foi
publicado no PyPI em **28/07/2026**, um dia depois do deploy anterior, e removeu
a API de decorators do `Server`. Como o Coolify resolve as dependências do zero a
cada build, o mesmo commit que funcionava passou a falhar sem nenhuma alteração
nossa. O Coolify detectou o container unhealthy e fez rollback automático —
produção seguiu no ar durante todo o episódio.

Correção: tetos de major em todos os pacotes sem pin exato
(`mcp>=1.28.1,<2.0.0` e afins). Verificado que `mcp` 1.28.1 e 1.29.0 mantêm
`Server.list_tools` e `Server.call_tool`. Registrado como regra em `CLAUDE.md`.
Migrar para `mcp` 2.x fica como tarefa própria.

### Revalidação após o deploy corrigido

| Item | Resultado |
|---|---|
| `ano` anterior ao nascimento | ✅ `isError` informando o ano do nascimento |
| `vigencia` com offset | ✅ início e fim com offset UTC explícito |
| `duracao_dias` + `nota` | ✅ `365.2422` |
| `destaques` com shape idêntico nas duas tools | ✅ mesmas 5 chaves |
| `luminar_principal` | ✅ `"sol"` na solar, `"lua"` na lunar |
| Aspecto `definicional` | ✅ exatamente 1 em cada, no luminar correto |
| `ciclo_em_curso` com `data_referencia` = hoje | ✅ retorno futuro e ciclo em curso corretos |
| `orbe_exato` em `listar_aspectos_tipos` | ✅ `0.5` |
| Notas acentuadas | ✅ |
| Gate de `local` natal | ✅ `isError` |
| **Regressão: Sol da RS × Sol natal** | ✅ longitudes iguais nos dois |
| **Regressão: Lua da RL × Lua natal** | ✅ longitudes iguais nas duas |

## 2026-07-27 — Revoluções solar e lunar (`main` @ `a9376c9`)

Deploy concluído em ~110s. Duas tools novas,
`calcular_revolucao_solar` e `calcular_revolucao_lunar`, sobre a
`PlanetaryReturnFactory` do Kerykeion 5.12.7. Sem dependência nova.

| Checagem | Resultado |
|----------|-----------|
| `GET /health` | ✅ versão 2.0.0, `transporte: "streamable-http+sse"` |
| `GET /tools` | ✅ 9 tools; as duas novas com `required` correto |
| Sol da revolução × Sol natal | ✅ **idênticos** até a quarta casa decimal |
| Lua da revolução × Lua natal | ✅ **idênticas** até a quarta casa decimal |
| Instante invariante ao local | ✅ BH e Lisboa devolvem o mesmo instante UTC |
| Longitudes invariantes ao local | ✅ nenhum dos 10 planetas muda entre BH e Lisboa |
| Ângulos variam com o local | ✅ ASC diferente entre BH e Lisboa |
| Regentes do ASC | ✅ Leão → sol/sol; Aquário → urano (moderno) / saturno (tradicional) |
| Erro sem hora natal | ✅ `isError`, mensagem PT-BR explicando o impacto de 12h |
| Erro `ano` fora de 1800–2200 | ✅ `isError` |
| Erro `local_revolucao` vazio | ✅ `isError` |
| Borda: aniversário 01/01 | ✅ nascido 01/01/1990 → retorno em `2026-01-01T05:47:12Z` |
| Borda: nascido 29/02 | ✅ 29/02/1988 → retorno em `2026-02-28T18:13:47Z` |
| Revolução lunar dentro do ciclo | ✅ referência 01/07/2026 → retorno em 07/07/2026 |

**Observações:**
- A validação do Sol e da Lua é a garantia astrológica central da técnica: o
  retorno é *definido* como o instante em que o astro reencontra sua longitude
  natal. Bater na quarta casa decimal confirma o `swe.solcross_ut`.
- Revolução trópica, **sem correção de precessão** — declarado no campo
  `metodo.precessao` de todo retorno.
- `local_revolucao` é obrigatório por decisão de design: não afeta nenhuma
  longitude, só ângulos e casas, e um default silencioso entregaria as casas do
  local natal a quem mudou de cidade.
- Testes: `tests/test_periodos.py` (21 casos de borda de calendário) roda em
  qualquer ambiente, inclusive Windows; `tests/test_revolucoes.py` exige Linux.

## 2026-06-02 — Boas práticas MCP (PR #1, `main` @ `df0184a`)

Deploy em produção validado após merge do PR #1 (concorrência em threadpool,
telemetria por tool, `isError`, annotations, transporte Streamable HTTP).

| Checagem | Resultado |
|----------|-----------|
| `GET /health` | ✅ `transporte: "streamable-http+sse"`, versão 2.0.0 |
| `GET /tools` | ✅ 7 tools |
| `POST /mcp/` initialize | ✅ 200, `Mcp-Session-Id` presente, `serverInfo.name=ceu-natal` (SDK mcp 1.27.2) |
| Deploy Coolify | ✅ live ~105s |

**Observações:**
- ⚠️ `POST /mcp` (sem barra) responde **307 → `/mcp/`** com `Location: http://` (downgrade de
  esquema atrás do Traefik). Use sempre a URL **com barra final** `/mcp/` ao configurar conectores.
  Docs já atualizadas.
- `MCP_ALLOWED_HOSTS` **não setado** → proteção anti-DNS-rebinding desligada (modo aberto, igual ao
  SSE legado). Setar a env se quiser travar por host.
- Telemetria estruturada (`event:"tool_call"` e `event:"geocode"`) sai nos logs do Coolify.
- Pendente (gate humano): reconfigurar conector Claude.ai de `/sse` → `/mcp/`.
- Suíte de servidor: 128/129 no ambiente Linux remoto (1 falha preexistente:
  `test_data_alvo_igual_nascimento_idade_zero`).
