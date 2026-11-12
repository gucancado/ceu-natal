Você vai cadastrar o Céu Natal em buscadores e diretórios de servidores MCP, no meu navegador, com as minhas contas já logadas (Google e GitHub `gucancado`). Faça as tarefas na ordem. Ao terminar cada uma, anote o resultado (feito, URL final, ou o que travou) e passe para a próxima. Se uma tarefa travar, registre o motivo e siga em frente.

Regras:
- Não crie conta com senha. Entre sempre com "Continue with GitHub" ou com o Google já logado.
- Pare e me pergunte antes de: pagar qualquer coisa, aceitar termos legais ou declarações em meu nome, apagar ou alterar registro DNS existente.
- Não publique post em rede social nem em fórum.
- Use só os dados abaixo. Não invente informação.

Dados do projeto:
- Nome: Céu Natal
- URL do servidor MCP (Streamable HTTP, sem autenticação): https://astrologia-mcp.gustavocancado.com.br/mcp/
- Site: https://mistico.gustavocancado.com.br (inglês: https://mistico.gustavocancado.com.br/en)
- Repositório: https://github.com/gucancado/ceu-natal (AGPL-3.0, Python)
- Privacidade: https://mistico.gustavocancado.com.br/privacidade · Termos: https://mistico.gustavocancado.com.br/termos
- Ícone: https://mistico.gustavocancado.com.br/icon.svg
- Descrição curta (PT): Mapa natal, sinastria, trânsitos, progressões e revoluções com efemérides suíças, em português.
- Short description (EN): Free astrology MCP server: natal chart, synastry, transits, progressions and solar/lunar returns with the Swiss Ephemeris. No login, no API key.
- Long description (EN): Céu Natal gives your AI assistant calculated astrology charts instead of estimated ones. It computes natal charts, synastry, composite charts, transits, secondary progressions and solar and lunar returns with the Swiss Ephemeris, and converts the birth city into coordinates and historical time zone before calculating. Tool results are in Portuguese; the assistant translates when answering. Free, open source, no account and no API key.
- Exemplos: "Calculate my natal chart: born 12/03/1990 at 14:30 in Lisbon, Portugal." · "Which transits are hitting my chart today?" · "Cast my 2027 solar return for Tokyo."
- Categorias: Lifestyle / Entertainment / Astrology (a que existir mais próxima).

## 1. Google Search Console
1. Abra https://search.google.com/search-console e adicione uma propriedade do tipo **Domínio** para `gustavocancado.com.br`.
2. Copie o registro TXT de verificação que o Google mostrar.
3. Abra https://registro.br, entre na conta, abra o domínio `gustavocancado.com.br` > DNS > editar zona. **Acrescente** um registro TXT na raiz (nome vazio ou `@`) com o valor copiado. Não mexa nos registros que já existem. Salve.
4. Volte ao Search Console e clique em Verificar. Se ainda não propagou, espere alguns minutos e tente de novo (até 3 vezes).
5. Em Sitemaps, envie `https://mistico.gustavocancado.com.br/sitemap.xml`.
6. Em Inspeção de URL, peça indexação de: `/`, `/mapa`, `/en`, `/sinastria`, `/transitos`, `/revolucao-solar` (todos em https://mistico.gustavocancado.com.br).

## 2. Bing Webmaster Tools
1. Abra https://www.bing.com/webmasters e entre com a conta Google.
2. Escolha **Importar do Google Search Console** e importe o site `mistico.gustavocancado.com.br` (se o domínio ainda não aparecer verificado no Google, adicione o site manualmente e verifique pelo mesmo método de DNS).
3. Confirme que o sitemap foi importado; se não, envie `https://mistico.gustavocancado.com.br/sitemap.xml`.

## 3. Smithery
1. Abra https://smithery.ai e entre com GitHub.
2. Adicione um servidor remoto por URL ("Add server" / "Publish" / "New"), informando a URL do servidor MCP.
3. Preencha nome, descrição curta EN, descrição longa EN, repositório e site. Publique e anote a URL da página do servidor.

## 4. mcp.so
1. Abra https://mcp.so, entre com GitHub e use "Submit".
2. Informe nome, URL do repositório, URL do servidor e a descrição curta EN. Envie e anote a URL.

## 5. PulseMCP
1. Abra https://www.pulsemcp.com/submit.
2. Envie a URL do repositório (ou do servidor) e a descrição curta EN. Anote a confirmação.

## 6. Glama
1. Abra https://glama.ai/mcp/servers/gucancado/ceu-natal e entre com GitHub.
2. Se aparecer "Claim" (reivindicar), faça a reivindicação pela conta `gucancado`.
3. Revise a descrição para a descrição curta EN e confira se o servidor aparece como remoto, com a URL do servidor. Anote a nota (score) que o Glama mostra e o que ele pede para melhorar.

## 7. PR no awesome-mcp-servers
1. Abra https://github.com/punkpeye/awesome-mcp-servers e leia o CONTRIBUTING e o README para ver o formato da linha e a categoria certa (procure onde estão outros servidores de astrologia; se não houver, use a categoria mais próxima, como "Other Tools and Integrations").
2. Edite o README pelo GitHub (ícone de lápis; isso cria um fork na conta `gucancado`) e acrescente uma linha no formato do repositório, em ordem alfabética na categoria, por exemplo:
   `- [gucancado/ceu-natal](https://github.com/gucancado/ceu-natal) 🐍 ☁️ - Astrology calculations (natal chart, synastry, transits, progressions, solar/lunar returns) with the Swiss Ephemeris. Free hosted endpoint, results in Portuguese.`
   Ajuste os emojis ao que a legenda do repositório definir (Python, remoto/cloud).
3. Abra o pull request com título `Add Céu Natal (astrology)` e descrição curta em inglês. Se o repositório pedir badge do Glama ou outro requisito, cumpra se for simples; se não, registre. Anote a URL do PR.

## 8. Diretório de conectores do Claude (só preparar)
1. Abra https://claude.ai/directory/manage > Submit new > MCP connector.
2. Preencha com os dados acima: conexão pela URL do servidor, nome `Céu Natal`, slug `ceu-natal`, one-liner `Accurate astrology charts for Claude, calculated with the Swiss Ephemeris instead of estimated.`, descrição longa EN, sem autenticação, e os exemplos.
3. **Pare antes de aceitar as declarações de compliance e de enviar.** Me avise que está pronto para eu revisar e enviar.

## Relatório final
Ao fim, me devolva uma tabela: tarefa | estado (feito / travou / aguardando) | URL ou motivo.
