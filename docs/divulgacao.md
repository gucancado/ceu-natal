# Plano de divulgação do Céu Natal

Prioridade: público brasileiro. Segundo plano: quem usa MCP em qualquer idioma.
Os passos de cada diretório estão em [distribuicao.md](distribuicao.md) e [diretorios/envio.md](diretorios/envio.md).

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
| Cadastro no Google Search Console (propriedade de domínio, TXT no Registro.br) e no Bing (importando do Google) | Claude in Chrome | pendente |
| Post no TabNews e em comunidades de astrologia mostrando o `/mapa` no ChatGPT | Gustavo | pendente |

## Frente 2: global (diretórios de MCP e inglês)

| Ação | Responsável | Estado |
|---|---|---|
| Página `/en` com o essencial em inglês e `hreflang` com a home | Claude | feito |
| Seção em inglês no `llms.txt` | Claude | feito |
| `/.well-known/mcp/server-card.json` no site | Claude | feito |
| Publicação no MCP Registry oficial | Claude | feito |
| Descrição e tópicos do GitHub em inglês e português, seção em inglês no README | Claude | feito |
| PR no `punkpeye/awesome-mcp-servers` | Claude | feito |
| Smithery, mcp.so, PulseMCP, reivindicação no Glama | Claude in Chrome | pendente |
| Diretório de conectores do Claude | Gustavo, com Claude in Chrome | pendente |
| Server card e `robots.txt` no domínio do servidor MCP | Claude | pendente (há trabalho não commitado em `app/`) |

## Fora do plano

- As páginas `/conectar/<ia>` saíram do ar por decisão em `28ce09b` e continuam redirecionando para a home.
- Domínio próprio (ex.: `ceunatal.com.br`) ajudaria a marca, mas troca as URLs já divulgadas. Decidir antes de divulgar em massa.
