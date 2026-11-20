Gere três acessos de API para o Céu Natal, no meu navegador, com a conta Google e a conta GitHub `gucancado` já logadas. Com eles, o Claude Code passa a enviar sitemap e páginas aos buscadores e a consultar o Glama sem abrir o navegador. Faça as tarefas na ordem. Se uma travar, anote o motivo e siga para a próxima.

Regras:
- Não crie conta nova, não pague nada e não apague nada.
- Não crie projeto novo no Google Cloud: use o projeto `bloquim-integracao`.
- Não ative faturamento. Se alguma tela pedir cartão ou faturamento, pare essa tarefa.
- Pare e me pergunte antes de aceitar termos legais ou declarações em meu nome.
- Use só os dados abaixo. Não invente informação.

Dados:
- Site: https://ceunatal.gustavocancado.com.br
- Propriedade do Search Console: domínio `gustavocancado.com.br`
- Projeto do Google Cloud: `bloquim-integracao`
- Nome da conta de serviço: `ceu-natal-divulgacao`

## 1. Glama: chave de API
1. Abra https://glama.ai/settings/api-keys (entre com GitHub se pedir).
2. Crie uma chave com o nome `ceu-natal-claude-code`. Se a tela oferecer escopos, escolha só leitura.
3. Copie a chave inteira. Ela costuma aparecer uma vez só.

## 2. Bing Webmaster Tools: chave de API
1. Abra https://www.bing.com/webmasters e escolha o site `ceunatal.gustavocancado.com.br`.
2. Abra Settings (engrenagem) → **API access** → **API Key**. Se ainda não existir chave, clique em **Generate**. Se já existir, só copie a existente; não gere outra, porque a nova invalida a anterior.
3. Copie a chave inteira.

## 3. Google: conta de serviço com acesso ao Search Console
1. Abra https://console.cloud.google.com/apis/library/searchconsole.googleapis.com?project=bloquim-integracao e clique em **Ativar** (Enable). Se já estiver ativada, siga.
2. Abra https://console.cloud.google.com/iam-admin/serviceaccounts?project=bloquim-integracao. Se já existir uma conta `ceu-natal-divulgacao`, use ela. Se não, clique em **Criar conta de serviço**, use o nome `ceu-natal-divulgacao`, pule as etapas de papéis e de acesso de usuários (não dê nenhum papel no projeto) e conclua.
3. Anote o e-mail da conta de serviço (termina em `@bloquim-integracao.iam.gserviceaccount.com`).
4. Abra a conta → aba **Chaves** → **Adicionar chave** → **Criar nova chave** → **JSON** → **Criar**. O arquivo vai para a pasta Downloads. Anote o nome do arquivo baixado. Não abra nem copie o conteúdo dele aqui.
5. Se a criação de chave estiver bloqueada por política da organização, anote a mensagem exata e pare esta tarefa.
6. Abra https://search.google.com/search-console, escolha a propriedade de domínio `gustavocancado.com.br` → **Configurações** → **Usuários e permissões** → **Adicionar usuário**. Cole o e-mail da conta de serviço e escolha a permissão **Completo** (não Proprietário). Salve.

## Relatório final
Me devolva uma tabela: tarefa | estado (feito / travou) | o que ficou registrado ou o motivo. Depois da tabela, traga à parte, cada um numa linha:
- `GLAMA_API_KEY=` seguida da chave do Glama
- `BING_API_KEY=` seguida da chave do Bing
- o e-mail da conta de serviço
- o nome do arquivo JSON baixado na pasta Downloads
