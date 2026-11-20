# Plano de divulgação do Céu Natal

Prioridade: público brasileiro. Segundo plano: quem usa MCP em qualquer idioma.
Os passos de cada diretório estão em [distribuicao.md](distribuicao.md) e [diretorios/envio.md](diretorios/envio.md).
O roteiro para o Claude in Chrome está em [prompt-chrome-divulgacao.md](prompt-chrome-divulgacao.md).

## Diagnóstico (2026-11-11)

- MCP Registry oficial: não publicado. É a fonte de PulseMCP, da galeria de MCP do VS Code e de vários agregadores.
- Glama indexa o repositório. Smithery, PulseMCP e mcp.so não têm o servidor.
- O site tinha 4 URLs no sitemap e nenhuma página para buscas de técnica ("sinastria grátis", "revolução solar").
- Nada em inglês para quem chega pelos diretórios internacionais.
- Search Console e Bing Webmaster Tools sem cadastro. O Bing alimenta o ChatGPT Search.

## Frente 1: Brasil (busca e IAs em português)

| Ação | Responsável | Estado |
|---|---|---|
| Páginas por técnica: `/sinastria`, `/transitos`, `/revolucao-solar`, `/revolucao-lunar`, `/progressoes`, `/mapa-composto`, com pedidos de exemplo e FAQ em schema.org | Claude | feito |
| Sitemap com todas as páginas e `hreflang` | Claude | feito |
| `llms.txt` com as técnicas | Claude | feito |
| Schema.org da home com autor, repositório e lista de técnicas | Claude | feito |
| Cadastro no Google Search Console (domínio `gustavocancado.com.br`) e no Bing (importado do Google), sitemap enviado | Claude in Chrome | feito (2026-11-12) |
| Post no TabNews e em comunidades de astrologia mostrando o `/mapa` no ChatGPT | Gustavo | pendente |
| Site em `ceunatal.gustavocancado.com.br`; o endereço antigo (`mistico`) redireciona com o caminho | Claude | feito (2026-11-19) |
| `robots.txt` com os robôs das IAs pelo nome, link para o `llms.txt` no cabeçalho, datas e `llms.txt` no sitemap, autor nos dados estruturados | Claude | feito (2026-11-19) |
| Search Console: sitemap `https://ceunatal.gustavocancado.com.br/sitemap.xml` enviado e indexação pedida para a home, `/mapa`, `/en` e as três landings | Claude in Chrome | feito (2026-11-19); sitemap processado, 11 páginas encontradas |
| Bing: `ceunatal.gustavocancado.com.br` verificado pela meta `msvalidate.01`, sitemap e as seis páginas enviados | Claude in Chrome | feito (2026-11-19); a meta precisa continuar no site, senão o Bing tira a verificação |
| `/en` com `<html lang="en">` e `llms.txt` em inglês em `/en/llms.txt` | Claude | feito (2026-11-19) |

## Frente 2: global (diretórios de MCP e inglês)

| Ação | Responsável | Estado |
|---|---|---|
| Página `/en` com o essencial em inglês e `hreflang` com a home | Claude | feito |
| Seção em inglês no `llms.txt` | Claude | feito |
| `/.well-known/mcp/server-card.json` no site | Claude | feito |
| Publicação no MCP Registry oficial (`io.github.gucancado/ceu-natal` 2.2.6) | Claude | feito (2026-11-12) |
| Descrição e tópicos do GitHub em inglês e português, seção em inglês no README | Claude | feito |
| PR no `punkpeye/awesome-mcp-servers` ([#19327](https://github.com/punkpeye/awesome-mcp-servers/pull/19327), em Spirituality & Esoterica) | Claude | aberto, checagens verdes e selo do Glama reconhecido; o servidor já tem release no Glama (2026-11-19). Espera o mantenedor |
| Glama: conta criada, servidor reivindicado (Discovery 33%); build pelo modo stdio (`python -m app.stdio`) | Claude in Chrome | feito (2026-11-19): build aprovado e release 2.2.6 publicada, Discovery em 67%. O passo de build precisa de `--break-system-packages` (o Python da imagem é instalado pelo uv); ver o [prompt](prompt-chrome-glama-build.md). Auto-Release ligado: cada release no GitHub gera uma no Glama. Falta o Glama calcular a nota das tools (TDQS) e a coerência |
| Smithery | — | fechou envios em 2026-10-31 |
| PulseMCP | — | envios pausados; importa do MCP Registry |
| mcp.so | — | só envio pago (US$ 39); não fazer |
| Diretório de conectores do Claude | Gustavo | publicado em 2026-11-20: https://claude.ai/directory/ceu-natal. A documentação do envio aponta para `mistico…/en`, que redireciona; a troca é pedida a `directory@anthropic.com` (rascunho no Gmail corrigido em 2026-11-20, falta enviar) |
| Endereço novo no PR do Docker (#7024) e no campo de site do repositório no GitHub | Claude | feito (2026-11-19) |
| Endereço novo no Glama | — | não há campo de site; o endereço vem do README do repositório, já corrigido, e entra no próximo sync |
| Divulgação pela API (`scripts/divulgacao.py`): IndexNow ligado (chave em `web/public/`), Bing, Glama (só leitura) e Search Console | Claude | feito (2026-11-20): IndexNow, Bing, Glama e Search Console respondem pelo script; chaves em `scripts/deploy.env` (fora do git). Diretório do Claude e Docker não têm API (e-mail e PR) |
| Endereço novo no MCP Registry | Claude | pendente; vai na próxima versão do servidor (o `server.json` já está certo) |
| Server card e `robots.txt` no domínio do servidor MCP | Claude | pendente (há trabalho não commitado em `app/`) |

## Próximas frentes (levantadas em 2026-11-12, conferir cada página de envio antes)

| Ação | Responsável | Estado |
|---|---|---|
| Docker MCP Catalog: PR em `docker/mcp-registry` como servidor remoto (`server.yaml` + `tools.json` vazio + readme) | Claude | PR aberto: [docker/mcp-registry#7024](https://github.com/docker/mcp-registry/pull/7024) |
| mcp.so pela rota gratuita (issue no GitHub deles, não o plano de US$ 39) | Claude in Chrome | a conferir |
| Claude Market (claudemarket.ai/submit), mcp.directory/submit, mcpservers.org, MCP Market (fila grátis longa ou pausada) | Claude in Chrome | a conferir |
| Cline MCP Marketplace (issue em `cline/mcp-marketplace`) e cursor.directory | Claude in Chrome | a conferir |
| Post em inglês: r/mcp, r/ClaudeAI, Show HN, dev.to (demo do mapa no Claude) | Gustavo | a fazer |
| Post em português: TabNews, grupos e perfis de astrologia, parceria com astrólogos que usam IA | Gustavo | a fazer |
| Vídeo curto (30 s) pedindo o mapa ao ChatGPT/Claude com o conector, para o site e redes | Gustavo | a fazer |
| Pacote PyPI (`uvx ceu-natal` via stdio) e entrada `packages` no `server.json` | Claude | avaliar; pyswisseph é frágil em wheels |

## Fora do plano

- As páginas `/conectar/<ia>` saíram do ar por decisão em `28ce09b` e continuam redirecionando para a home.
- Domínio próprio (ex.: `ceunatal.com.br`) ajudaria a marca, mas troca as URLs já divulgadas. Decidir antes de divulgar em massa.
