# Céu Natal — Servidor MCP de Astrologia

Servidor [Model Context Protocol](https://modelcontextprotocol.io/) que expõe
ferramentas de cálculo astrológico para agentes de IA. Calcula mapas natais e
sinastria com [Kerykeion](https://github.com/g-battaglia/kerykeion) +
[Swiss Ephemeris](https://www.astro.com/swisseph/swephinfo_e.htm) (NASA JPL).

- Transporte: **SSE** sobre HTTP (servidor remoto multi-cliente)
- Protocolo: MCP 2024-11-05
- Autenticação: API key via header `Authorization: Bearer ...` ou query `?api_key=...`
- Produção: `https://ceu-natal-api.pu5h6p.easypanel.host`

---

## Tools expostas

### `calcular_mapa_natal`

Mapa natal completo com posições planetárias, casas (Placidus strict), ângulos
(ASC, MC, DESC, FC), aspectos entre planetas, pontos sensíveis (nodos
verdadeiros e Quíron) e síntese (elementos, qualidades, hemisférios,
stelliums).

**Parâmetros:**

| campo  | tipo            | obrigatório | descrição                                  |
|--------|-----------------|-------------|--------------------------------------------|
| `data` | `string`        | sim         | DD/MM/YYYY                                 |
| `hora` | `string \| null`| não         | HH:MM                                      |
| `local`| `string \| null`| não         | "Cidade, UF" (BR) ou "Cidade, País"        |
| `nome` | `string \| null`| não         | identificador no retorno                   |

Sem `hora` ou `local`, retorna apenas posições por signo (sem casas/ângulos).

### `calcular_sinastria`

Aspectos cruzados entre os mapas de duas pessoas e em quais casas de uma os
planetas da outra caem. Útil para análise de relacionamento.

**Parâmetros:** `pessoa_a` e `pessoa_b`, cada um com o mesmo formato de
`calcular_mapa_natal`.

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
- `GET /sse` — handshake MCP via SSE (autenticado)
- `POST /messages/` — canal de mensagens MCP (autenticado)

---

## Variáveis de ambiente

| Variável             | Default       | Descrição                                          |
|----------------------|---------------|----------------------------------------------------|
| `GEONAMES_USERNAME`  | `gucancado`   | conta GeoNames para geocodificação                 |
| `MCP_API_KEY`        | *(vazio)*     | se vazio, libera tudo (modo dev)                   |
| `MCP_HOST`           | `0.0.0.0`     | bind                                               |
| `MCP_PORT`           | `8000`        | porta                                              |
| `MCP_SERVER_NAME`    | `ceu-natal`   | nome retornado em `initialize`                     |
| `MCP_SERVER_VERSION` | `2.0.0`       | versão exposta                                     |

---

## Conectar ao Claude Desktop

Em `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "ceu-natal": {
      "url": "https://ceu-natal-api.pu5h6p.easypanel.host/sse",
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

- **Endpoint URL:** `https://ceu-natal-api.pu5h6p.easypanel.host/sse`
- **Authentication:** Header Auth → `Authorization: Bearer SEU_MCP_API_KEY`

---

## Testes

```bash
docker compose run --rm ceu-natal pytest -v
```

Os testes usam coordenadas fixas (Belo Horizonte) sem chamar o geocoder, para
rodar sem rede.

---

## Estrutura

```
app/
├── server.py           # entrypoint MCP (Starlette + SSE)
├── core/
│   ├── kerykeion.py    # wrapper do AstrologicalSubject
│   ├── aspectos.py     # cálculo de aspectos com orbes do spec
│   ├── sintese.py      # elementos, hemisférios, stelliums
│   ├── formatter.py    # tradução PT-BR e formatação
│   ├── validators.py   # parse de data/hora/local
│   └── geocoder.py     # GeoNames + Nominatim + cache
└── tools/
    ├── mapa_natal.py
    └── sinastria.py
tests/
├── test_mapa_natal.py
└── test_sinastria.py
```
