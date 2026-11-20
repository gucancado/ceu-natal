Feche as pendências do Céu Natal no meu navegador, com as minhas contas já logadas (Google e Claude). Faça as tarefas na ordem. Se uma travar, anote o motivo e siga para a próxima.

Regras:
- Não pague nada e não crie nada novo.
- Apague só a chave indicada na tarefa 1, nada mais.
- Não clique em **Editar** no envio do diretório do Claude: editar devolve o envio para revisão.
- Pare e me pergunte antes de aceitar termos legais ou declarações em meu nome.
- Se uma proteção do navegador barrar um clique, não tente contornar: anote e siga.

## 1. Google Cloud: apagar a chave que nunca foi usada
1. Abra https://console.cloud.google.com/iam-admin/serviceaccounts?project=bloquim-integracao e entre na conta `ceu-natal-divulgacao@bloquim-integracao.iam.gserviceaccount.com` → aba **Chaves**.
2. A conta deve ter duas chaves. Apague só a de id começando com `44d7ed257207`. A outra, de id começando com `d2436df1d134`, está em uso: não mexa nela.
3. Se o id `44d7ed257207` não aparecer, não apague nada; anote os ids que aparecem.

## 2. Diretório de conectores do Claude: publicar
1. Abra https://claude.ai/directory/manage e abra o envio do Céu Natal.
2. Se o estado for "Aprovado" / "Ready to publish", clique em **Publicar**. Se aparecer só uma confirmação simples, confirme. Se aparecerem termos ou campos novos, pare e me pergunte.
3. Se o clique for barrado, deixe a página aberta nesse envio e anote; eu clico.
4. Anote o estado final e o endereço público do conector, se aparecer.

## 3. Gmail: pedido de troca de endereço ao diretório
Só faça esta tarefa se a tarefa 2 terminou com o conector publicado ("No ar" / "Live").
1. Abra https://mail.google.com/mail/u/0/#drafts e abra o rascunho para `directory@anthropic.com` com assunto "Céu Natal connector: website moved, please update the listing URLs".
2. Não mude o texto. Clique em **Enviar**.
3. Se o conector não foi publicado, não envie; anote que o rascunho continua esperando.

## Relatório final
Uma tabela: tarefa | estado (feito / travou / aguardando) | o que ficou registrado ou o motivo. Depois, à parte, tudo o que alguma tela pediu para eu fazer.
