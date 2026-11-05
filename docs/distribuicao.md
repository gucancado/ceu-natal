# Distribuição do Céu Natal

Guia dos canais onde o servidor MCP é listado. Todos os passos abaixo são feitos pelo **mantenedor**, porque cada canal exige login no navegador (GitHub ou conta própria). O servidor remoto já está no ar em `https://astrologia-mcp.gustavocancado.com.br/mcp/`.

## Bloco de texto reutilizável

- **Nome:** Céu Natal
- **Descrição curta (até 100 caracteres):** Mapa natal, sinastria, trânsitos, progressões e revoluções com efemérides suíças, em português.
- **Descrição longa:** O Céu Natal é um servidor MCP de astrologia que calcula mapas natais, sinastrias, mapas compostos, trânsitos, progressões e revoluções solares e lunares. Usa as efemérides suíças (Swiss Ephemeris) para posições precisas e aceita cidade, data e hora de nascimento em linguagem natural. As respostas vêm em português, prontas para o assistente interpretar.
- **Prompts de exemplo:**
  1. "Calcule meu mapa natal: nasci em 12/03/1990 às 14h30 em Belo Horizonte."
  2. "Quais são os trânsitos de hoje sobre o meu mapa natal?"
  3. "Faça a sinastria entre mim (12/03/1990, 14h30, Belo Horizonte) e minha parceira (25/07/1992, 9h15, São Paulo)."
- **URL do repositório:** https://github.com/gucancado/ceu-natal
- **URL do servidor:** https://astrologia-mcp.gustavocancado.com.br/mcp/
- **URL da política de privacidade:** https://mistico.gustavocancado.com.br/privacidade

## MCP Registry (oficial)

- **Quem faz:** o mantenedor.
- **Pré-requisito:** conta GitHub `gucancado`; `server.json` na raiz do repo (já existe, versão `2.2.1`); binário `mcp-publisher` baixado em https://github.com/modelcontextprotocol/registry/releases/latest (não versionar o binário).
- **Passos:**
  1. No diretório do repo: `mcp-publisher validate` (deve dizer que o `server.json` é válido).
  2. `mcp-publisher login github` abre o device flow no navegador; autorizar com a conta `gucancado`.
  3. `mcp-publisher publish`.
  4. Confirmar: `curl "https://registry.modelcontextprotocol.io/v0.1/servers?search=ceu-natal"`.
- **Atualizações:** subir `version` no `server.json` (e `MCP_SERVER_VERSION`) e rodar `mcp-publisher publish` de novo. Cada URL remota só pode pertencer a um nome de servidor.

## Smithery

- **Quem faz:** o mantenedor.
- **Pré-requisito:** conta no https://smithery.ai com login GitHub.
- **Passos:** entrar com GitHub, clicar em "Add server" (servidor remoto por URL), informar `https://astrologia-mcp.gustavocancado.com.br/mcp/`, preencher nome e descrições com o bloco acima e publicar.

## Glama

- **Quem faz:** o mantenedor.
- **Pré-requisito:** repositório público `gucancado/ceu-natal`; login GitHub em https://glama.ai.
- **Passos:** abrir https://glama.ai/mcp/servers, localizar o Céu Natal (indexado a partir do repo público) e reivindicar o servidor ("claim"), confirmando a propriedade pela conta GitHub. Revisar a descrição com o bloco acima.

## PulseMCP

- **Quem faz:** o mantenedor.
- **Pré-requisito:** nenhum além do bloco de texto; o servidor precisa estar no ar.
- **Passos:** abrir https://www.pulsemcp.com/submit e enviar a URL do repo ou do servidor e a descrição de 100 caracteres. Também costuma importar do MCP Registry, então a publicação lá ajuda.

## mcp.so

- **Quem faz:** o mantenedor.
- **Pré-requisito:** conta em https://mcp.so (login GitHub).
- **Passos:** usar o formulário de submissão ("Submit"), informando nome, URL do servidor `https://astrologia-mcp.gustavocancado.com.br/mcp/`, URL do repo e a descrição de 100 caracteres.

## Fora do escopo desta fase

O Claude Directory e a GPT Store ficam para a fase F7: exigem OAuth e uma fachada REST, que ainda não existem.
