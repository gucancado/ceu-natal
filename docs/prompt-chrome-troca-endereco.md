O site do Céu Natal mudou de endereço. Era `https://mistico.gustavocancado.com.br` e agora é `https://ceunatal.gustavocancado.com.br`. O endereço antigo continua no ar e redireciona para o novo, página por página. Sua tarefa é avisar os buscadores e trocar o endereço nos cadastros que já existem, no meu navegador, com as minhas contas já logadas (Google e GitHub `gucancado`). Faça as tarefas na ordem. Ao terminar cada uma, anote o resultado (feito, o que viu na tela, ou o que travou) e passe para a próxima. Se uma tarefa travar, registre o motivo e siga em frente.

Regras:
- Não crie conta nova em lugar nenhum. Entre sempre com o Google já logado ou com "Continue with GitHub".
- Não pague nada.
- Não apague nada: nem propriedade, nem site, nem sitemap antigo, nem registro DNS. O endereço antigo precisa continuar cadastrado enquanto os buscadores acompanham o redirecionamento.
- Não mexa no DNS. Se alguma tela pedir um registro DNS novo ou um código de verificação para colocar no site, copie o que ela pede, não conclua esse passo e me traga no relatório.
- Pare e me pergunte antes de aceitar termos legais ou declarações em meu nome, e antes de retirar ou reenviar qualquer cadastro que esteja em revisão.
- Use só os dados abaixo. Não invente informação.

Dados:
- Site novo: https://ceunatal.gustavocancado.com.br (inglês: https://ceunatal.gustavocancado.com.br/en)
- Site antigo, que redireciona: https://mistico.gustavocancado.com.br
- Sitemap novo: https://ceunatal.gustavocancado.com.br/sitemap.xml
- Páginas para pedir indexação, nesta ordem: `/`, `/mapa`, `/sinastria`, `/transitos`, `/revolucao-solar`, `/en` (todas em https://ceunatal.gustavocancado.com.br)
- Privacidade: https://ceunatal.gustavocancado.com.br/privacidade · Termos: https://ceunatal.gustavocancado.com.br/termos
- Ícone: https://ceunatal.gustavocancado.com.br/icon.svg
- Servidor MCP (não mudou): https://astrologia-mcp.gustavocancado.com.br/mcp/
- Repositório (não mudou): https://github.com/gucancado/ceu-natal

## 1. Google Search Console
1. Abra https://search.google.com/search-console e escolha a propriedade de domínio `gustavocancado.com.br`. Ela já está verificada e cobre o endereço novo, então não crie outra propriedade.
2. Em Sitemaps, envie `https://ceunatal.gustavocancado.com.br/sitemap.xml`. Anote o status que aparecer (Sucesso, Não foi possível buscar, etc.). Não remova o sitemap do endereço antigo.
3. Em Inspeção de URL, inspecione cada uma das seis páginas da lista acima e clique em **Solicitar indexação**. Espere o teste de cada uma terminar antes de ir para a próxima. Se o Google avisar que o limite diário foi atingido, pare esta etapa e anote quais páginas ficaram faltando.
4. Inspecione também `https://mistico.gustavocancado.com.br/` e anote o que o Google mostra (o esperado é "Página com redirecionamento"). Não peça indexação dela.
5. Não use a ferramenta "Mudança de endereço": ela serve para troca de domínio inteiro, e aqui só mudou o subdomínio.

## 2. Bing Webmaster Tools
1. Abra https://www.bing.com/webmasters e entre com a conta Google.
2. Veja quais sites estão cadastrados. Anote os nomes exatamente como aparecem.
3. Se `ceunatal.gustavocancado.com.br` não estiver na lista, adicione pelo caminho **Importar do Google Search Console**. Se a importação não oferecer esse endereço, tente adicionar manualmente `https://ceunatal.gustavocancado.com.br`; se o Bing pedir verificação por meta tag, arquivo XML ou CNAME, copie o que ele pede e pare esta etapa sem concluir.
4. Com o site novo cadastrado, abra Sitemaps e envie `https://ceunatal.gustavocancado.com.br/sitemap.xml`.
5. Em Envio de URL (URL Submission), envie as seis páginas da lista.
6. Não remova o site antigo.

## 3. Glama
1. Abra https://glama.ai/mcp/servers/gucancado/ceu-natal e entre com GitHub, se não estiver logado.
2. Procure na página pública e na administração do servidor onde aparece o endereço do site (campos como Website, Homepage ou Documentation). Se houver um campo editável com `mistico.gustavocancado.com.br`, troque para `https://ceunatal.gustavocancado.com.br` e salve.
3. Se o endereço vier do repositório do GitHub e não for editável, só anote onde ele aparece e qual valor está mostrando.
4. Anote a nota (score) atual e se o Glama já sincronizou um commit mais recente que `cf0b385`.

## 4. Diretório de conectores do Claude
1. Abra https://claude.ai/directory/manage e localize o envio do Céu Natal (estava "Em revisão").
2. Só olhe: anote o estado atual do envio e quais endereços do site antigo aparecem nele (site, documentação, privacidade, termos, ícone).
3. Se existir um botão de editar que deixe trocar esses endereços sem retirar o envio da revisão e sem reenviar, me diga que existe e pare. Não clique em editar, retirar nem reenviar.

## Relatório final
Ao fim, me devolva uma tabela: tarefa | estado (feito / travou / aguardando) | o que ficou registrado ou o motivo. Depois da tabela, liste à parte tudo o que alguma tela pediu para eu fazer (códigos de verificação, registros DNS, confirmações).
