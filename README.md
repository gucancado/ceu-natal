# Céu Natal

Servidor MCP que calcula mapas astrais com efemérides suíças para o seu assistente de IA interpretar.

**In English.** Céu Natal is an open-source Model Context Protocol server that computes
natal charts, synastry, transits, progressions and solar/lunar returns with the Swiss
Ephemeris, answering in Portuguese. A free public endpoint runs at
`https://astrologia-mcp.gustavocancado.com.br/mcp/` (no sign-up). Licensed AGPL-3.0.

[![CI](https://github.com/gucancado/ceu-natal/actions/workflows/ci.yml/badge.svg)](https://github.com/gucancado/ceu-natal/actions/workflows/ci.yml)
[![Licença: AGPL-3.0](https://img.shields.io/badge/licen%C3%A7a-AGPL--3.0-blue.svg)](LICENSE)
[![Python 3.11](https://img.shields.io/badge/python-3.11-blue.svg)](https://www.python.org/downloads/release/python-3110/)

## Por que existe

Peça um mapa astral a um assistente de IA e ele responde com segurança, mas as posições
costumam ser inventadas: o modelo não tem efemérides, então chuta o signo da Lua e o
ascendente. Este servidor faz a conta de verdade e devolve os números; a IA só interpreta.

## Use agora

Endpoint MCP público e gratuito (Streamable HTTP, sem login):

```
https://astrologia-mcp.gustavocancado.com.br/mcp/
```

Passo a passo para Claude (web, Desktop e Code), ChatGPT, Gemini, Cursor e n8n:
<https://mistico.gustavocancado.com.br/conectar>.

## O que calcula

| Tool | O que faz |
|------|-----------|
| `calcular_mapa_natal` | Posições, casas, ângulos, aspectos, nodos, Quíron e síntese de um mapa natal. |
| `calcular_sinastria` | Aspectos cruzados entre duas pessoas e planetas de uma nas casas da outra. |
| `calcular_transitos` | Posições numa data, aspectos com o mapa natal e destaque dos trânsitos lentos. |
| `calcular_progressoes` | Progressões secundárias (1 dia = 1 ano), com Lua e Sol progredidos. |
| `calcular_mapa_composto` | Mapa composto de duas pessoas pelo método de midpoints. |
| `calcular_revolucao_solar` | Mapa do retorno do Sol à posição natal num ano, com local da revolução. |
| `calcular_revolucao_lunar` | Próximo retorno da Lua à posição natal a partir de uma data. |
| `listar_aspectos_tipos` | Aspectos suportados, com ângulos, orbes e natureza. |
| `healthcheck` | Status e versão do servidor. |

Entrada de pessoa: `data` (DD/MM/YYYY, obrigatória), `hora` (HH:MM), `local`
("Cidade, UF" ou "Cidade, País"), `nome`, `is_dst`. No mapa natal sem `hora`, o cálculo usa 12:00 no
horário local, a Lua vem marcada como incerta (`posicao_incerta`, `signo_pode_mudar`) e
não saem casas nem ângulos. `sistema_casas` é opcional: `P` Placidus (padrão), `K` Koch,
`W` Whole Sign, `E` Equal, `R` Regiomontanus, `C` Campanus, `O` Porphyrius, `B` Alcabitus,
`M` Morinus, `T` Topocentric. Os schemas completos estão em `GET /tools`.

## Exemplo

Pedido (`tools/call`):

```json
{
  "name": "calcular_mapa_natal",
  "arguments": {"nome": "Ana", "data": "12/03/1990", "hora": "14:30", "local": "Belo Horizonte, MG"}
}
```

Trecho da resposta:

```json
{
  "planetas": {
    "sol": {"signo": "Peixes", "grau": "21°52'", "grau_decimal": 21.8779, "posicao_absoluta": 351.8779,
            "retrogrado": false, "elemento": "Agua", "qualidade": "Mutavel", "casa": 8},
    "lua": {"signo": "Libra", "grau": "6°19'", "grau_decimal": 6.329, "posicao_absoluta": 186.329,
            "retrogrado": false, "elemento": "Ar", "qualidade": "Cardinal", "casa": 3}
  },
  "angulos": {
    "ascendente": {"signo": "Cancer", "grau": "18°38'", "grau_decimal": 18.6412, "posicao_absoluta": 108.6412}
  },
  "aspectos": [
    {"planeta_a": "lua", "planeta_b": "venus", "tipo": "trigono", "orbe": 0.48,
     "aplicando": true, "exato": true, "natureza": "harmonico"}
  ],
  "local_resolvido": {"lat": -19.9167, "lng": -43.9333, "fuso": "America/Sao_Paulo"}
}
```

A resposta completa traz também os outros planetas, as 12 casas, meio do céu,
descendente, fundo do céu, pontos sensíveis e a síntese (elementos, qualidades,
hemisférios, stelliums).

## Rodar local

Com Docker:

```bash
cp .env.example .env
docker compose up --build        # http://localhost:8000
```

Com `pip` (Linux ou macOS; no Windows, use o WSL, porque o pyswisseph não compila nele):

```bash
python3.11 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.server:app --port 8000
```

Rotas: `/mcp/` (MCP Streamable HTTP), `/sse` e `/messages/` (SSE legado), `/health`,
`/tools` (lista de tools; pública quando `MCP_API_KEY` está vazia), `/llms.txt`,
`/mapa-rapido` (formulário do site) e `/` (redireciona para `PUBLIC_SITE_URL`).

Para desenvolver, instale `requirements-dev.txt` e rode `ruff check .`, `mypy app` e
`python -m pytest -q`. Detalhes em [CONTRIBUTING.md](CONTRIBUTING.md).

## Variáveis de ambiente

| Variável | Default | Descrição |
|----------|---------|-----------|
| `MCP_SERVER_NAME` | `ceu-natal` | nome devolvido no `initialize` |
| `MCP_SERVER_VERSION` | `2.2.0` | versão exposta |
| `MCP_API_KEY` | *(vazio)* | se definida, exige `Authorization: Bearer <chave>`; vazia, libera tudo |
| `MCP_ALLOWED_HOSTS` | *(vazio)* | hosts aceitos no `/mcp/` (anti-DNS rebinding), separados por vírgula; vazio = sem validação |
| `RATE_LIMIT_SESSION_PER_MIN` | `30` | chamadas de tool por minuto por sessão MCP (0 desliga) |
| `RATE_LIMIT_GLOBAL_PER_MIN` | `600` | chamadas de tool por minuto no total (0 desliga) |
| `RATE_LIMIT_MAPA_RAPIDO_IP_PER_MIN` | `6` | pedidos ao `/mapa-rapido` por minuto por IP (0 desliga) |
| `RATE_LIMIT_MAPA_RAPIDO_GLOBAL_PER_MIN` | `120` | pedidos ao `/mapa-rapido` por minuto no total (0 desliga) |
| `PUBLIC_SITE_URL` | `https://github.com/gucancado/ceu-natal` | destino do redirect de `/` e link do site no `/llms.txt` |
| `PUBLIC_MCP_URL` | `https://astrologia-mcp.gustavocancado.com.br` | URL do MCP exibida no `/llms.txt` |
| `CORS_ORIGINS` | *(vazio = `PUBLIC_SITE_URL`)* | origens aceitas pelo CORS do `/mapa-rapido`, separadas por vírgula |
| `GEONAMES_USERNAME` | `gucancado` | conta GeoNames da geocodificação (crie a sua em geonames.org) |
| `NOMINATIM_USER_AGENT` | `ceu-natal-mcp/2.0` | User-Agent enviado ao Nominatim (OSM) |
| `NOMINATIM_MIN_INTERVAL_S` | `1.0` | intervalo mínimo (s) entre chamadas ao Nominatim |
| `GEOCODER_MAX_CONCORRENTES` | `4` | teto de chamadas simultâneas aos provedores de geocodificação |
| `GEOCODER_ESPERA_MAX_S` | `3.0` | espera máxima (s) por uma vaga nesse teto; depois, erro |
| `GEOCODER_CACHE_PATH` | `<tmp>/ceu-natal-geocode-cache.json` | cache persistente de coordenadas; no Docker, volume em `/var/cache/ceu-natal` |

## Site (`web/`)

O site de apresentação (<https://mistico.gustavocancado.com.br>) é um app Next.js 16
separado, com imagem Docker própria (`web/Dockerfile`). Para rodar:
`cd web && pnpm install && pnpm dev`; as URLs vêm de `web/.env.example`.

## Precisão e limites

- **Efemérides:** Swiss Ephemeris, da Astrodienst AG, via
  [Kerykeion](https://github.com/g-battaglia/kerykeion) e pyswisseph. Zodíaco tropical.
- **Latitude acima de 66°:** o cálculo de casas não é confiável perto dos polos. O mapa
  natal sai sem casas nem ângulos, com aviso; trânsitos, progressões e revoluções recusam.
- **Anos:** datas de 1000 a 3000; revolução solar de 1800 a 2200.
- **Horário de verão:** se a hora cai na transição (ambígua ou inexistente), o servidor
  devolve erro pedindo `is_dst` (`true` = horário de verão, `false` = padrão).
- **Sem hora de nascimento:** cálculo às 12:00 locais; a Lua pode estar até ~6,5° antes ou
  depois, e o resultado diz quando o signo dela pode mudar.
- **Limites do endpoint público:** 30 chamadas por minuto por sessão e 600 por minuto no
  total. Nada sobre pessoas é armazenado; veja a
  [política de privacidade](docs/legal/privacidade.md).

## Contribuir

Issues e pull requests são bem-vindos. Veja [CONTRIBUTING.md](CONTRIBUTING.md); para
falhas de segurança, [SECURITY.md](SECURITY.md).

## Licença

[AGPL-3.0-or-later](LICENSE). A AGPL vale também para uso pela rede: quem oferecer este
servidor como serviço modificado precisa publicar o código. O endpoint público roda
exatamente o código deste repositório.

A escolha segue as dependências: o Kerykeion é AGPL-3.0, e o pyswisseph (Swiss Ephemeris)
é distribuído sob AGPL-3.0 ou sob a licença profissional paga da Astrodienst. Um uso fora
dos termos da AGPL exigiria a licença profissional da Swiss Ephemeris e trocar o
Kerykeion. O site usa os pacotes `@beeads/*`, sob licença MIT, compatível
com a AGPL.
