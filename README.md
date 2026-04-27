# 🌌 Céu Natal API

API REST para cálculo de mapas astrais natais. Recebe nome, data, hora e local de nascimento e retorna um JSON estruturado com posições planetárias, casas e ângulos.

## Stack

- **Python 3.11**
- **FastAPI**
- **Kerykeion** (Swiss Ephemeris / NASA JPL)
- **Docker**

## Rodando localmente

```bash
# Clone o repositório
git clone https://github.com/gucancado/ceu-natal.git
cd ceu-natal

# Configure o .env
cp .env.example .env
# Edite o .env e coloque seu GEONAMES_USERNAME

# Suba com Docker
docker-compose up --build
```

A API estará disponível em `http://localhost:8000`

## Endpoints

### `GET /health`
Verifica se a API está rodando.

### `POST /natal-chart`
Calcula o mapa astral natal.

**Body:**
```json
{
  "nome": "Brina Vasconcelos",
  "data": "03/05/1987",
  "hora": "13:47",
  "local": "Mariana, MG"
}
```

- `hora` e `local` são opcionais.
- Sem `hora` ou `local`, ângulos e casas são omitidos.

**Resposta:**
```json
{
  "nome": "Brina Vasconcelos",
  "nascimento": {
    "data": "03/05/1987",
    "hora": "13:47",
    "local": "Mariana, MG"
  },
  "planetas": {
    "sol": { "signo": "Touro", "casa": 9, "grau": "12°44'", "retrogrado": false },
    "lua": { "signo": "Câncer", "casa": 11, "grau": "16°29'", "retrogrado": false }
  },
  "angulos": {
    "ascendente": { "signo": "Virgem", "grau": "3°41'" },
    "meio_do_ceu": { "signo": "Gêmeos", "grau": "10°58'" },
    "descendente": { "signo": "Peixes", "grau": "3°41'" },
    "fundo_do_ceu": { "signo": "Sagitário", "grau": "10°58'" }
  }
}
```

## Documentação interativa

Acesse `http://localhost:8000/docs` para o Swagger UI.
