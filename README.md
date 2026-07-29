# Céu Natal — Servidor MCP de Astrologia

Servidor [Model Context Protocol](https://modelcontextprotocol.io/) que expõe
ferramentas de cálculo astrológico para agentes de IA. Calcula mapas natais e
sinastria com [Kerykeion](https://github.com/g-battaglia/kerykeion) +
[Swiss Ephemeris](https://www.astro.com/swisseph/swephinfo_e.htm) (NASA JPL).

- Transporte: **SSE** sobre HTTP (servidor remoto multi-cliente)
- Protocolo: MCP 2024-11-05
- Autenticação: API key via header `Authorization: Bearer ...` ou query `?api_key=...`
- Produção: `https://astrologia-mcp.gustavocancado.com.br`

> **Para LLMs / agentes que vão propor mudanças:** leia
> [CLAUDE.md](CLAUDE.md) primeiro. Anti-padrões mais comuns:
> não é mais REST FastAPI (foi migrado para MCP), tools de trânsitos /
> progressões / composto **já existem** em `app/tools/`, e o deploy no
> Coolify é manual. Verifique o estado real com
> `curl https://astrologia-mcp.gustavocancado.com.br/tools` antes de
> planejar trabalho novo.

---

## Tools expostas

9 tools no total. Todas aceitam `sistema_casas` opcional (P=Placidus, K=Koch,
W=Whole Sign, E=Equal, R=Regiomontanus, C=Campanus, O=Porphyrius, B=Alcabitus,
M=Morinus, T=Topocentric — default `P`).

### `calcular_mapa_natal`

Mapa natal completo com posições planetárias, casas, ângulos (ASC, MC, DESC,
FC), aspectos entre planetas, pontos sensíveis (nodos verdadeiros e Quíron) e
síntese (elementos, qualidades, hemisférios, stelliums).

**Parâmetros:**

| campo           | tipo            | obrigatório | descrição                                  |
|-----------------|-----------------|-------------|--------------------------------------------|
| `data`          | `string`        | sim         | DD/MM/YYYY                                 |
| `hora`          | `string \| null`| não         | HH:MM                                      |
| `local`         | `string \| null`| não         | "Cidade, UF" (BR) ou "Cidade, País"        |
| `nome`          | `string \| null`| não         | identificador no retorno                   |
| `sistema_casas` | `string \| null`| não         | identificador (P, K, W, ...). Default P.   |

Sem `hora` ou `local`, retorna apenas posições por signo (sem casas/ângulos).

### `calcular_sinastria`

Aspectos cruzados entre os mapas de duas pessoas e em quais casas de uma os
planetas da outra caem. Útil para análise de relacionamento.

**Parâmetros:** `pessoa_a`, `pessoa_b` (mesmo formato do `calcular_mapa_natal`)
e `sistema_casas` opcional (aplicado nos dois mapas).

### `calcular_transitos`

Trânsitos planetários para uma data específica em relação a um mapa natal.
Posições atuais, aspectos cruzados (com aplicando/separando), em qual casa
natal cada planeta em trânsito cai, e síntese com destaque para trânsitos
de planetas lentos (Saturno, Urano, Netuno, Plutão, Quíron) com orbe < 2°.

**Parâmetros:** `natal` (mesmo formato), `data_transito` (DD/MM/YYYY,
obrigatório), `hora_transito` (HH:MM — default 12:00 UTC), `local_transito`
(default Greenwich/UTC), `sistema_casas`.

### `calcular_progressoes`

Progressões secundárias (técnica "um dia = um ano") para uma data alvo.
Posições progredidas, aspectos progredido↔natal, destaque para Lua progredida
(fase emocional atual, ~2.5 anos por signo) e Sol progredido (~30 anos por
signo), com sinalização de ingressos recentes e mudanças iminentes de signo.

**Parâmetros:** `natal`, `data_alvo` (DD/MM/YYYY, obrigatório), `sistema_casas`.

### `calcular_mapa_composto`

Mapa composto (composite chart) de duas pessoas pelo método de **midpoints** —
o mapa da "relação como entidade". Posições compostas, ângulos (ASC e MC
compostos quando ambos têm hora+local), aspectos internos e síntese de
elementos. **Não retorna casas** — composto por midpoint não tem instante/local
definidos.

**Parâmetros:** `pessoa_a`, `pessoa_b` (mesmo formato), `sistema_casas`.

### `calcular_revolucao_solar`

Revolução solar (solar return) — o mapa do instante exato em que o Sol retorna à
longitude eclíptica que ocupava no nascimento. Técnica de **previsão anual**: o
mapa rege o período até a revolução seguinte. Como o ano trópico tem 365,2422
dias, o retorno cai na véspera, no dia ou no dia seguinte ao aniversário.

Retorna o mapa completo da revolução (planetas, casas, ângulos, aspectos
internos), os aspectos revolução↔natal, a sobreposição dos dois mapas nos dois
sentidos e destaques da leitura: ascendente da revolução com regentes moderno e
tradicional, os dois luminares com casa da revolução e casa natal, e planetas
angulares.

A conjunção do Sol da revolução com o Sol natal vem marcada com
`definicional: true` em `aspectos_revolucao_natal` — ela tem orbe 0 por
construção (é a definição da técnica), então encabeça a lista ordenada por orbe
sem ser um achado interpretativo.

`revolucao.vigencia` traz `inicio_utc` e `fim_aproximado_utc` com offset
explícito. O fim é o início somado à duração média do ciclo, não a revolução
seguinte calculada de fato — erro típico de 20 a 30 minutos, declarado no campo
`nota`.

**Parâmetros:**

| campo             | tipo            | obrigatório | descrição                                     |
|-------------------|-----------------|-------------|-----------------------------------------------|
| `natal`           | `object`        | sim         | mesmo formato das outras tools; exige `hora` e `local` |
| `ano`             | `integer`       | sim         | ano da revolução (1800–2200)                  |
| `local_revolucao` | `string`        | sim         | onde a pessoa estará no momento do retorno    |
| `sistema_casas`   | `string \| null`| não         | default P                                     |

`local_revolucao` é obrigatório de propósito: ele **não altera nenhuma posição
planetária** — define apenas ascendente, meio do céu e cúspides. Um default
silencioso entregaria as casas do local natal a quem mudou de cidade, que é a
maioria dos casos.

Revolução **trópica, sem correção de precessão** (declarado no campo `metodo` do
retorno). A hora de nascimento é obrigatória: sem ela o Sol natal erra até 0,5°,
o que desloca o instante do retorno em até 12 horas.

### `calcular_revolucao_lunar`

Revolução lunar (lunar return) — mesma mecânica com a Lua, ciclo de ~27,32 dias.
Técnica de **previsão mensal**. `destaques` tem o mesmo shape da solar, com
`luminar_principal: "lua"`.

**Parâmetros:** `natal`, `data_referencia` (DD/MM/YYYY, obrigatório),
`local_revolucao` (obrigatório), `sistema_casas`.

⚠️ Devolve o **próximo** retorno a partir de `data_referencia`, não o ciclo em
curso. Passar a data de hoje normalmente devolve o mês lunar que ainda vai
começar. Quando isso acontece, o resultado inclui o bloco `ciclo_em_curso` com
`inicio_aproximado_utc` — chame de novo com essa data para obter o mapa do ciclo
vigente.

### `listar_aspectos_tipos`

Tipos de aspectos suportados com ângulos, orbes e natureza
(harmônico/tensão/neutro). Sem parâmetros.

### `healthcheck`

Status e versão do servidor. Sem parâmetros.

---

## Aspectos calculados

| Aspecto      | Ângulo | Orbe (luminar) | Orbe (demais) | Natureza   |
|--------------|--------|----------------|---------------|------------|
| Conjunção    | 0°     | 8°             | 6°            | neutro     |
| Oposição     | 180°   | 8°             | 6°            | tensão     |
| Trígono      | 120°   | 4°             | 4°            | harmônico  |
| Quadratura   | 90°    | 6°             | 6°            | tensão     |
| Sextil       | 60°    | 4°             | 4°            | harmônico  |
| Quintil      | 72°    | 2°             | 2°            | neutro     |
| Inconjunção  | 150°   | 2°             | 2°            | tensão     |
| Semi-sextil  | 30°    | 2°             | 2°            | neutro     |

`exato: true` quando orbe < 0.5°. `aplicando: true` quando o aspecto se forma
(planetas se aproximando do ângulo exato).

---

## Como rodar localmente (Docker)

```bash
cp .env.example .env
# editar .env: GEONAMES_USERNAME e (opcional) MCP_API_KEY
docker compose up --build
```

Servidor sobe em `http://localhost:8000`:

- `GET /health` — healthcheck (público)
- `GET /tools` — lista as tools registradas em JSON (autenticado, útil pra debug)
- `POST/GET /mcp` — endpoint MCP Streamable HTTP (recomendado)
- `GET /sse` — handshake MCP via SSE (legado, autenticado)
- `POST /messages/` — canal de mensagens SSE (legado, autenticado)

Exemplo de inspeção rápida sem cliente MCP:

```bash
curl http://localhost:8000/tools | jq
```

---

## Variáveis de ambiente

| Variável                | Default                                          | Descrição                                                       |
|-------------------------|--------------------------------------------------|-----------------------------------------------------------------|
| `GEONAMES_USERNAME`     | `gucancado`                                      | conta GeoNames para geocodificação                              |
| `GEOCODER_CACHE_PATH`   | `/tmp/ceu-natal-geocode-cache.json`              | caminho do cache persistente. Em Docker, montar volume em `/var/cache/ceu-natal` |
| `MCP_API_KEY`           | *(vazio)*                                        | se vazio, libera tudo (modo dev)                                |
| `MCP_HOST`              | `0.0.0.0`                                        | bind                                                            |
| `MCP_PORT`              | `8000`                                           | porta                                                           |
| `MCP_SERVER_NAME`       | `ceu-natal`                                      | nome retornado em `initialize`                                  |
| `MCP_SERVER_VERSION`    | `2.0.0`                                          | versão exposta                                                  |

---

## Conectar ao Claude (web ou Desktop)

Guia passo-a-passo pra usuário final em
[docs/CONECTAR-CLAUDE-AI.md](docs/CONECTAR-CLAUDE-AI.md). Resumo abaixo.

### Claude Desktop

Em `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "ceu-natal": {
      "url": "https://astrologia-mcp.gustavocancado.com.br/mcp/",
      "headers": {
        "Authorization": "Bearer SEU_MCP_API_KEY"
      }
    }
  }
}
```

Sem `MCP_API_KEY` configurado no servidor, o header `Authorization` pode ser
omitido.

---

## Conectar ao n8n

No nó **MCP Client** do n8n:

- **Endpoint URL:** `https://astrologia-mcp.gustavocancado.com.br/mcp/`
- **Authentication:** Header Auth → `Authorization: Bearer SEU_MCP_API_KEY`

---

## Testes

```bash
docker compose run --rm ceu-natal pytest -v
```

Os testes usam coordenadas fixas (Belo Horizonte) sem chamar o geocoder, para
rodar sem rede.

A suite completa exige Linux — `pyswisseph`, dependência transitiva do
Kerykeion, não compila no Windows. `tests/test_periodos.py` é a exceção: não
importa Kerykeion e roda em qualquer ambiente com `pytest tests/test_periodos.py`.

---

## Estrutura

```
app/
├── server.py           # entrypoint MCP (Streamable HTTP + SSE legado)
├── core/
│   ├── kerykeion.py    # wrapper do AstrologicalSubject
│   ├── aspectos.py     # cálculo de aspectos com orbes do spec
│   ├── sintese.py      # elementos, hemisférios, stelliums
│   ├── formatter.py    # tradução PT-BR, formatação e regências
│   ├── validators.py   # parse de data/hora/local
│   ├── periodos.py     # lógica temporal das revoluções (sem Kerykeion)
│   ├── revolucoes.py   # core compartilhado das revoluções
│   └── geocoder.py     # GeoNames + Nominatim + cache
└── tools/
    ├── mapa_natal.py
    ├── sinastria.py
    ├── transitos.py
    ├── progressoes.py
    ├── composto.py
    ├── revolucao_solar.py
    └── revolucao_lunar.py
tests/                  # um arquivo por módulo de core/ e tools/
```
