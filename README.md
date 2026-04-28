# Ceu Natal API

API REST para calculo de mapas astrais natais. Desenvolvida para ser consumida por agentes de IA especializados em astrologia.

## Stack

- Python 3.11 + FastAPI
- Kerykeion 5.x com Swiss Ephemeris (precisao NASA JPL)
- Nominatim / GeoNames para geocodificacao (cidade para coordenadas + timezone)
- Docker

---

## URLs

| Ambiente | URL |
|---|---|
| Producao | `https://ceu-natal-api.pu5h6p.easypanel.host` |
| Interno (EasyPanel) | `http://ceu-natal_api:8000` |
| Swagger/Docs | `https://ceu-natal-api.pu5h6p.easypanel.host/docs` |
| Local | `http://localhost:8000` |

---

## Autenticacao

A API nao requer autenticacao - e aberta para qualquer chamada HTTP.

---

## Endpoints

### `GET /health`

```json
{ "status": "ok", "service": "ceu-natal", "version": "2.0.0" }
```

---

### `POST /natal-chart`

Calcula o mapa astral natal completo.

**Parametros:**

| Campo | Tipo | Obrigatorio | Formato | Exemplo |
|---|---|---|---|---|
| `nome` | string | sim | Texto livre | `"Brina Vasconcelos"` |
| `data` | string | sim | DD/MM/YYYY | `"03/05/1987"` |
| `hora` | string | nao | HH:MM | `"13:47"` |
| `local` | string | nao | Cidade, UF ou Cidade, Pais | `"Mariana, MG"` |
| `sistema_casas` | string | nao | Ver tabela abaixo | `"Placidus"` (padrao) |
| `incluir_aspectos` | boolean | nao | true/false | `true` (padrao) |

**Sistemas de casas disponiveis:** Placidus, Whole Sign, Koch, Equal House, Regiomontanus, Campanus, Porphyry, Morinus, Topocentric.

**Comportamento com campos opcionais:**

| hora | local | Resultado |
|---|---|---|
| sim | sim | Mapa completo (planetas + casas + angulos + aspectos) |
| nao | sim | Planetas + aspectos - angulos e casas sao null |
| sim | nao | Planetas + aspectos - angulos e casas sao null |
| nao | nao | Apenas posicoes planetarias basicas (meio-dia UTC) |

---

## Campos de cada planeta

| Campo | Tipo | Descricao |
|---|---|---|
| `signo` | string | Signo zodiacal em portugues |
| `casa` | integer | Casa astrologica (1-12) |
| `grau` | string | Posicao no signo no formato grau minuto |
| `grau_decimal` | float | Posicao decimal no signo |
| `posicao_absoluta` | float | Longitude eclitica 0-360 |
| `retrogrado` | boolean | Se esta em movimento retrogrado |
| `velocidade` | float | Velocidade diaria em graus/dia |
| `declinacao` | float | Declinacao eclitica em graus |
| `elemento` | string | Fogo, Terra, Ar ou Agua |
| `qualidade` | string | Cardinal, Fixo ou Mutavel |

---

## Planetas e pontos calculados

| Grupo | Pontos |
|---|---|
| Planetas classicos | Sol, Lua, Mercurio, Venus, Marte |
| Planetas modernos | Jupiter, Saturno, Urano, Netuno, Plutao |
| Pontos sensiveis | Nodo Norte Verdadeiro, Nodo Sul Verdadeiro, Chiron |
| Angulos | Ascendente, Meio do Ceu, Descendente, Fundo do Ceu |
| Casas | 12 cuspides completas (sistema configuravel) |

---

## Conversao de grau para decimal

```
grau_decimal = graus + minutos / 60
Exemplo: 12 graus 44 minutos = 12 + 44/60 = 12.7333
```

---

## Rodando localmente

```bash
git clone https://github.com/gucancado/ceu-natal.git
cd ceu-natal
cp .env.example .env
docker compose up --build
```

Swagger disponivel em `http://localhost:8000/docs`

---

## Deploy no EasyPanel

- Projeto: `ceu-natal` / Servico: `api`
- Source: GitHub `gucancado/ceu-natal`, branch `main`
- Build: Dockerfile / Porta: 8000
- Env: `GEONAMES_USERNAME=gucancado`

Reimplantar em: `https://pu5h6p.easypanel.host/projects/ceu-natal/app/api`

---

## Precisao

- Efemerides: Swiss Ephemeris (NASA JPL)
- Geocodificacao: Nominatim (OpenStreetMap) com fallback GeoNames
- Timezone: Calculada via `timezonefinder`
- Cache: Coordenadas e timezones cacheadas localmente
