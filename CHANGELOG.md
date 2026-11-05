# Changelog

Mudanças relevantes do servidor e do site. Formato inspirado no
[Keep a Changelog](https://keepachangelog.com/pt-BR/1.1.0/); versões seguem o
[Versionamento Semântico](https://semver.org/lang/pt-BR/).

## [2.2.0] — 2026-11-05

### Corrigido

- Aspecto "aplicando" de trânsitos, progressões e revoluções considera o lado natal parado (antes saía invertido com a Lua natal).
- Grau truncado nunca mostra `30°00'`.
- Hora ambígua ou inexistente no horário de verão vira erro claro pedindo `is_dst`, aceito por todas as tools.
- Sinastria só calcula casas e composto só calcula ângulos quando as duas pessoas têm hora e local.
- Acima de 66° de latitude o mapa natal omite casas e ângulos com aviso; trânsitos, progressões e revoluções recusam.
- Síntese sem casas devolve hemisférios nulos; empate vira "equilibrado".
- Progressões contam em tempo universal, sem o deslocamento de 1 h quando o horário de verão muda.
- Geocoder: UF que também é estado dos EUA (AL, MA, MS, MT, PA, SC) não força o Brasil; só cidades, a mais populosa primeiro.
- Fuso de coordenadas no mar ou na fronteira resolvido por `timezone_at_land`.
- Evicção do cache do geocoder preserva a falha recém-gravada.
- Cada tool recebe sua própria cópia do schema de pessoa.
- Site: botão grande com o tamanho de texto certo e estado visível do botão pausar.

### Adicionado

- Sem hora, a Lua vem com `posicao_incerta` e `signo_pode_mudar`, e os aspectos dela com `incerto`.
- Mapa natal com cidade devolve `local_resolvido` (latitude, longitude e fuso).
- Datas aceitas de 1000 a 3000.
- Teto de chamadas simultâneas ao geocoder (`GEOCODER_MAX_CONCORRENTES`, `GEOCODER_ESPERA_MAX_S`) e cache de falhas com TTL e limite de tamanho.
- `/health` expõe os limites do `/mapa-rapido`.
- CI com `ruff`, `mypy` e `pip-audit`; Dependabot para pip, npm e GitHub Actions.
- CHANGELOG, CONTRIBUTING, SECURITY, código de conduta e templates de issue e PR.
- Cabeçalho SPDX em todo arquivo Python de `app/` e `scripts/`.

### Segurança

- Limite por IP do `/mapa-rapido` usa o último `X-Forwarded-For` atrás do proxy (o cliente não forja).
- Corpo do `/mapa-rapido` limitado a 4 KB (413).
- Chave de API só por header `Authorization: Bearer`, comparada em tempo constante.
- Geocodificação GeoNames por HTTPS.
- Imagem Docker roda como usuário sem privilégios; `docker-compose` publica a porta só em `127.0.0.1`.
- Site com CSP, HSTS, `nosniff` e `Referrer-Policy`.

### Alterado

- Sem `GEONAMES_USERNAME` o geocoder usa só o Nominatim e avisa uma vez no log, em vez de usar a conta GeoNames do mantenedor.
- `EntradaNascimento` é a entrada única de pessoa/natal de todas as tools.
- `Settings` e `create_app(settings)` substituem a configuração espalhada no import do servidor.
- Dependências de runtime em `requirements.in` com lock em `requirements.txt`; desenvolvimento em `requirements-dev.txt`.
- `scripts/deploy.py` lê destino e token do ambiente ou de `scripts/deploy.env` local, sem valores no código.
- Descrição de `calcular_mapa_natal` diz que, sem hora, o cálculo usa 12:00 local.
- `server.json` aponta o site em `https://mistico.gustavocancado.com.br`.
- README reescrito; `CLAUDE.md` só com orientação de código.
- Testes com dados de nascimento fictícios.
- Site: caixa baixa só no marketing, bundle menor sem o barrel do `@beeads/ui`, formulário e rotador acessíveis, email de contato em texto.

### Removido

- Chave de API por query string (`?api_key=`).
- Workflow de sincronização automática do `CLAUDE.md`.
- Planos e specs internos de `docs/superpowers/` do repositório.
- `MCP_HOST` e `MCP_PORT` de `.env.example` e `docker-compose.yml` (nenhum código as lia).

## [2.1.0] — 2026-11-03

### Adicionado

- Limite de taxa por sessão MCP (30/min) e global (600/min).
- `/llms.txt` e redirect da raiz com URLs públicas por env.
- `server.json` para o MCP Registry e guia de distribuição.
- Sessões Streamable HTTP expiram por inatividade.
- Política de privacidade do serviço gratuito.
- `scripts/deploy.py` para deploy manual.
- `/mapa-rapido` e o site em `web/` (Next.js): guias de conexão por cliente, política, termos e status.

### Corrigido

- Progressões aceitam data alvo no dia do nascimento.
- Site: digitação dos prompts travava na primeira letra.
- `starlette>=1.3.1` fecha cinco avisos de segurança.

### Alterado

- Tools importadas sob demanda; os testes do servidor rodam sem Kerykeion.
