# Revoluções planetárias (solar e lunar) — design

**Data:** 2026-07-27
**Status:** aprovado, pronto para implementação

---

## Problema

O servidor tem cinco tools de cálculo (natal, sinastria, trânsitos, progressões,
composto). O eixo preditivo cobre o curto prazo (trânsitos) e o longo prazo
(progressões), mas não tem a técnica de **previsão anual** — a revolução solar —
nem a de **previsão mensal** — a revolução lunar. São as duas técnicas preditivas
mais pedidas em consulta depois dos trânsitos.

## Fundamentação astrológica

Uma revolução planetária é o mapa levantado para o instante exato em que um
planeta em trânsito retorna à longitude eclíptica que ocupava no nascimento.

**Revolução solar:** o Sol retorna à sua longitude natal. Como o ano trópico tem
365,2422 dias, o retorno cai na véspera, no dia ou no dia seguinte ao aniversário,
com a hora variando muito de ano para ano. Vigência: até a próxima revolução
(~365,25 dias).

**Revolução lunar:** a Lua retorna à sua longitude natal, a cada ~27,32 dias
(mês sideral). Vigência: até o próximo retorno.

Três variáveis definem o resultado:

| Variável | Efeito | Decisão deste design |
|---|---|---|
| **Local** onde o mapa é levantado | Muda apenas ASC/MC/casas — as longitudes planetárias são idênticas em qualquer ponto da Terra | Parâmetro **obrigatório**. Força a escolha consciente e evita entregar silenciosamente as casas do local natal para quem mudou de cidade (a escola majoritária usa o local de residência/permanência no momento do retorno) |
| **Precessão** | A variante precessionada soma ~50,3"/ano à longitude alvo. Aos 40 anos isso dá ~0,56°, deslocando o instante em ~13,5h e mudando completamente o ASC | **Não aplicada.** Revolução trópica pura, que é o default esmagador. Declarado explicitamente no campo `metodo` do output |
| **Sistema de casas** | Muda as cúspides | Herdado do subject natal via `houses_system_identifier`; parâmetro `sistema_casas` já existente nas outras tools |

O que se lê numa revolução: o ASC e seu regente, a casa ocupada pelo Sol (solar)
ou pela Lua (lunar), os planetas angulares (casas 1/4/7/10), a sobreposição sobre
o mapa natal e os aspectos entre revolução e natal.

## Viabilidade

Kerykeion **5.12.7** — a versão já pinada em `requirements.txt` — inclui
`kerykeion/planetary_return_factory.py` com a classe `PlanetaryReturnFactory`,
que resolve o problema inteiro:

- usa `swe.solcross_ut(sol_natal.abs_pos, julian_day)` e
  `swe.mooncross_ut(lua_natal.abs_pos, julian_day)` — precisão melhor que 0,001",
  sem busca iterativa própria;
- monta o mapa completo via `AstrologicalSubjectFactory.from_iso_utc_time(...)`
  com `online=False`, aceitando `lat`/`lng`/`tz_str` — encaixa direto no nosso
  `app/core/geocoder.py`;
- herda `houses_system_identifier`, `zodiac_type`, `sidereal_mode`,
  `perspective_type` e `active_points` do subject natal;
- devolve `PlanetReturnModel`, subclasse de `AstrologicalBaseModel`, portanto
  compatível com `planetas_iter`, `casas_iter`, `pontos_sensiveis_iter`,
  `formatar_planeta` e `formatar_casas` sem qualquer alteração.

`pyswisseph>=2.10.3.1` já é dependência transitiva do Kerykeion. **Nenhuma
dependência nova, nenhuma alteração em `requirements.txt`.**

## Decisões de escopo

1. **Duas tools separadas**, `calcular_revolucao_solar` e
   `calcular_revolucao_lunar`, compartilhando um core. Descrições nítidas para o
   agente consumidor, em vez de uma tool com parâmetro `tipo`.
2. **`local_revolucao` obrigatório** nas duas.
3. **Entrada temporal específica por técnica:** a solar recebe `ano` (inteiro);
   a lunar recebe `data_referencia` (DD/MM/YYYY) e devolve o próximo retorno a
   partir dela. O output declara o período de vigência, o que desarma a confusão
   entre "a revolução do ano X" e "a revolução vigente hoje".

## Arquitetura

| Arquivo | Responsabilidade | Depende de kerykeion |
|---|---|---|
| `app/core/periodos.py` (novo) | Lógica temporal pura: âncora de busca da revolução solar, janela de vigência, validação de faixa de ano | não |
| `app/core/revolucoes.py` (novo) | Core compartilhado: gate de validação do natal, geocoding do local da revolução, instanciação da `PlanetaryReturnFactory`, montagem do payload comum | sim |
| `app/tools/revolucao_solar.py` (novo) | `calcular_revolucao_solar(...)` — âncora anual e destaques da técnica solar | sim |
| `app/tools/revolucao_lunar.py` (novo) | `calcular_revolucao_lunar(...)` — próximo retorno a partir da data e destaques do ciclo lunar | sim |
| `app/core/formatter.py` | Acrescenta `REGENTES_SIGNO` e `regentes_de()` — necessários para o regente do ASC da revolução | não |
| `app/server.py` | Duas entradas em `TOOLS` e dois branches em `_dispatch` | — |

`app/core/kerykeion.py`, `app/core/aspectos.py` e `app/core/sintese.py` ficam
intocados.

A separação de `periodos.py` existe por uma razão operacional: `pyswisseph` não
compila no Windows (sem toolchain C) e não há Docker local, então tudo que
depende de kerykeion só roda em produção. Manter a lógica temporal — que é onde
moram as bordas de calendário — num módulo sem essa dependência permite testá-la
localmente.

## Fluxo de cálculo

1. `validar_sistema_casas(sistema_casas)`; parse de `natal` (data, hora, local).
2. **Gate:** hora e local natais são obrigatórios. Sem hora, o Sol natal erra até
   0,5°, o que desloca o instante do retorno em até 12 horas e destrói o ASC —
   que é o centro da técnica. Sem local, não há cúspides natais para a
   sobreposição.
3. `criar_subject(...)` para o mapa natal (geocoding do local natal já embutido).
4. `parse_local(local_revolucao)` → `geocode()` → `lat`, `lng`, `tz_str` do local
   da revolução.
5. `PlanetaryReturnFactory(subject_natal, lat=..., lng=..., tz_str=...,
   online=False)`.
6. Resolução do instante:
   - **Solar:** âncora = aniversário no ano pedido menos 3 dias; chamada a
     `next_return_from_date(ancora.year, ancora.month, ancora.day,
     return_type="Solar")`. O retorno nunca se afasta mais de ~1 dia do
     aniversário, então 3 dias garantem que o próximo cruzamento é o do ano
     correto. Nascidos em 29/02 usam 28/02 nos anos não bissextos. Aniversários
     em 1, 2 ou 3 de janeiro produzem âncora em dezembro do ano anterior, o que
     é válido e correto.
   - **Lunar:** `next_return_from_iso_formatted_time(data_referencia_iso,
     "Lunar")`, com `data_referencia` convertida para meia-noite UTC.
7. Montagem do output.

`KerykeionException` não é tratada hoje pelo `_call_tool` do servidor — cairia em
"Erro interno do servidor", sem informação útil. O core captura e converte em
`ValueError` com mensagem PT-BR.

## Contrato de entrada

**`calcular_revolucao_solar`** — required: `natal`, `ano`, `local_revolucao`

| Campo | Tipo | Descrição |
|---|---|---|
| `natal` | object | `data` (obrigatório, DD/MM/YYYY), `hora` (HH:MM), `local`, `nome` |
| `ano` | integer | Ano da revolução, 1800–2200 |
| `local_revolucao` | string | Cidade e UF/país onde a pessoa estará no momento do retorno |
| `sistema_casas` | string \| null | P (default), K, W, E, R, C, O, B, M, T |

**`calcular_revolucao_lunar`** — required: `natal`, `data_referencia`,
`local_revolucao`

Idêntica, trocando `ano` por `data_referencia` (string DD/MM/YYYY): a tool
devolve o primeiro retorno lunar que ocorre a partir dessa data.

Nenhuma das duas declara `outputSchema` — as tools de cálculo tiveram o
`outputSchema` removido no commit `a9d5b22` porque campos nuláveis quebram a
validação estrita do MCP.

## Contrato de saída

Espelha o padrão já estabelecido por `app/tools/progressoes.py` e
`app/tools/transitos.py`:

```
natal                      → nome, data, hora, local
revolucao                  → tipo ("solar" | "lunar"), instante_utc,
                             instante_local, local, lat, lng, tz_str,
                             vigencia { inicio, fim_aproximado }
metodo                     → tecnica, precessao: "nao_aplicada",
                             fonte: "swisseph solcross_ut/mooncross_ut via kerykeion",
                             nota (o local escolhido muda só ângulos e casas)
planetas                   → formatar_planeta, com a casa DA REVOLUÇÃO
casas                      → formatar_casas
angulos                    → ascendente, meio_do_ceu
pontos_sensiveis           → nodos verdadeiros e Quíron
aspectos_internos          → calcular_aspectos sobre os pontos da revolução
aspectos_revolucao_natal   → calcular_aspectos_sinastria (revolução × natal)
sobreposicao               → planetas_revolucao_em_casas_natais,
                             planetas_natais_em_casas_revolucao
sintese                    → calcular_sintese (elementos, qualidades, hemisférios,
                             stelliums)
destaques                  → específico por técnica (abaixo)
```

`vigencia.fim_aproximado` é `inicio + 365,2422 dias` (solar) ou
`inicio + 27,32158 dias` (lunar). É deliberadamente aproximado: calcular o fim
exato exigiria construir um segundo mapa completo, e o nome do campo declara a
aproximação.

**`destaques` da revolução solar:**

```
ascendente_revolucao   → signo, grau, regente_moderno, regente_tradicional,
                         casa_natal_onde_cai
sol_na_casa            → número da casa da revolução ocupada pelo Sol
planetas_angulares     → planetas da revolução em casas 1, 4, 7 ou 10
lua_revolucao          → signo, casa da revolução, casa natal
```

**`destaques` da revolução lunar:** mesma estrutura, invertendo a ênfase —
`lua_na_casa` como campo principal e `sol_revolucao` como secundário.

## Erros

Todos como `ValueError` com mensagem PT-BR, capturados pelo `_call_tool` e
devolvidos como `CallToolResult(isError=True)`:

- hora natal ausente — explicando o impacto de até 12h no instante do retorno;
- local natal ausente;
- `local_revolucao` ausente ou vazio;
- `ano` fora de 1800–2200 (limite prático das efemérides);
- `data_referencia` malformada;
- falha do Kerykeion, convertida da `KerykeionException`.

`GeocodingError` continua sendo tratada pelo marshaller existente.

## Testes

**Rodam no Windows** (`tests/test_periodos.py`, sem kerykeion):

- âncora da revolução solar: caso comum, aniversário em 01/01 (âncora cai no ano
  anterior), nascido em 29/02 em ano bissexto e em ano comum;
- janela de vigência solar e lunar;
- validação de faixa de ano.

**Rodam apenas em produção** (`tests/test_revolucoes.py`, marcados como o resto
da suite que depende de kerykeion): estrutura do payload, invariância das
longitudes planetárias ao trocar `local_revolucao` e variância correspondente do
ASC — que é justamente a garantia astrológica que a técnica exige.

## Deploy e documentação

1. `CLAUDE.md`: duas linhas na tabela "Tools já implementadas em `app/tools/`".
2. `README.md`: seção descrevendo as duas tools e seus parâmetros.
3. Push para `origin/main`, deploy manual via API do Coolify
   (app uuid `ejbfwl0yfego72kk5n2us1gh`).
4. Validação em produção: `curl /health`, `curl /tools` (deve listar 9 tools) e
   uma chamada real a `calcular_revolucao_solar` via Streamable HTTP em `/mcp/`.
5. `docs/validacao.md` atualizado com o resultado.

## Fora de escopo

- Revolução precessionada (variante minoritária; adicionável depois como flag).
- Demi-revolução solar (Sol em oposição, ~6 meses).
- Comparativo de relocação (vários `local_revolucao` lado a lado).
- Retornos de outros planetas (Saturno, Júpiter) — a `PlanetaryReturnFactory`
  só suporta `"Solar"` e `"Lunar"`.
