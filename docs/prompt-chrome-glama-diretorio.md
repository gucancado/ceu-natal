Continue o cadastro do Céu Natal no meu navegador, com as minhas contas já logadas (Google e GitHub `gucancado`). São duas tarefas: Glama e diretório de conectores do Claude. Ao terminar cada uma, anote o resultado e passe para a próxima. Se travar, registre o motivo e siga em frente.

Regras:
- Pode criar conta no Glama entrando com GitHub e aceitar os termos de uso do Glama. Não crie conta com senha em nenhum outro lugar.
- Não pague nada.
- No diretório do Claude, preencha tudo, mas pare antes do clique final de enviar (Submit) e me mostre o resumo.
- Use só os dados abaixo. Não invente informação.

Dados do projeto:
- Nome: Céu Natal
- Autor e responsável: Gustavo Cançado, https://gustavocancado.com.br
- URL do servidor MCP (Streamable HTTP, sem autenticação): https://astrologia-mcp.gustavocancado.com.br/mcp/
- Site: https://mistico.gustavocancado.com.br (inglês: https://mistico.gustavocancado.com.br/en)
- Repositório: https://github.com/gucancado/ceu-natal (AGPL-3.0, Python). Na raiz há `Dockerfile` e `glama.json` (mantenedor `gucancado`).
- Suporte: https://github.com/gucancado/ceu-natal/issues
- Privacidade: https://mistico.gustavocancado.com.br/privacidade · Termos: https://mistico.gustavocancado.com.br/termos
- Descrição curta (EN): Free astrology MCP server: natal chart, synastry, transits, progressions and solar/lunar returns with the Swiss Ephemeris. No login, no API key.

## 1. Glama: reivindicar e conseguir a nota
1. Abra https://glama.ai/mcp/servers/gucancado/ceu-natal. Entre com GitHub (conta `gucancado`) e crie a conta se for pedido, aceitando os termos do Glama.
2. Reivindique o servidor ("Claim"). O repositório tem `glama.json` com o mantenedor `gucancado`, o que deve permitir a reivindicação direta.
3. Na administração do servidor no Glama, configure o build para que ele consiga rodar e inspecionar o servidor:
   - Use o `Dockerfile` da raiz do repositório.
   - O servidor sobe com `uvicorn app.server:app --host 0.0.0.0 --port 8000` e fala MCP por Streamable HTTP em `/mcp/`. Nenhuma variável de ambiente é obrigatória.
   - Se o Glama só aceitar servidor por stdio, procure a opção de servidor remoto/HTTP ou de proxy. Se não houver, registre o que o formulário pede e pare esta tarefa.
4. Dispare o build ("Deploy", "Build" ou "Re-evaluate") e espere até 10 minutos, recarregando a página.
5. Abra https://glama.ai/mcp/servers/gucancado/ceu-natal/score e anote a nota e a lista do que o Glama pede para melhorar.

## 2. Diretório de conectores do Claude: terminar e parar antes de enviar
1. Abra https://claude.ai/directory/manage e retome o rascunho do Céu Natal (parado na etapa 7, Tratamento de dados).
2. Corrija as etapas anteriores, se precisar:
   - Empresa: `Gustavo Cançado`, site `https://gustavocancado.com.br`.
   - Nome do autor: `Gustavo Cançado`; URL do autor: `https://gustavocancado.com.br`.
   - Slug: `ceu-natal`.
3. Etapa 7 (Tratamento de dados):
   - Propriedade da API: a API é nossa. Se houver campo de observação, escreva: "Birth city is geocoded with GeoNames, with Nominatim (OpenStreetMap) as fallback. No other third-party API."
   - Dados pessoais de saúde: Não.
   - Conteúdo patrocinado: Não.
   - Se houver pergunta sobre armazenamento: "Birth data sent through MCP is used only for the calculation and is not stored. Logs keep tool name, status, duration and, when given, city and country, for up to 90 days."
4. Siga as etapas restantes até a revisão. Nas declarações de compliance, leia cada uma e anote o texto. Não marque nenhuma que diga algo que você não consegue confirmar com os dados acima.
5. Pare antes de clicar em enviar. Me devolva o resumo de todos os campos e o texto das declarações para eu revisar e enviar.

## Relatório final
Me devolva uma tabela: tarefa | estado (feito / travou / aguardando) | URL, nota do Glama ou motivo.
