Faça duas tarefas do Céu Natal no meu navegador, com as minhas contas já logadas (Claude e GitHub `gucancado`): publicar o conector no diretório do Claude, que já está aprovado, e configurar o build no Glama. Faça na ordem. Se uma tarefa travar, anote o motivo e siga para a outra.

Regras:
- Não crie conta nova e não pague nada.
- Não apague nada e não retire nenhum envio.
- Pare e me pergunte antes de aceitar termos legais ou declarações em meu nome.
- Use só os dados abaixo. Não invente informação. Se um formulário pedir algo que não está aqui, anote o que ele pede e pare essa tarefa.

Dados:
- Site: https://ceunatal.gustavocancado.com.br (inglês: https://ceunatal.gustavocancado.com.br/en)
- Servidor MCP: https://astrologia-mcp.gustavocancado.com.br/mcp/
- Repositório: https://github.com/gucancado/ceu-natal (branch `main`, Python 3.11)
- Instalação: `python -m pip install --require-hashes -r requirements.txt`
- Comando do servidor (stdio): `python -m app.stdio`
- Nenhuma variável de ambiente é obrigatória e não há chave de API.

## 1. Diretório de conectores do Claude: publicar
1. Abra https://claude.ai/directory/manage e abra o envio do Céu Natal. O estado esperado é aprovado, pronto para publicar ("Ready to publish").
2. Se o estado for outro (em revisão, rascunho, rejeitado), não clique em nada: anote o estado e o que a página diz, e passe para a tarefa 2.
3. Não clique em **Editar** e não mude nenhum campo. A documentação do envio aponta para `https://mistico.gustavocancado.com.br/en`, que redireciona para o endereço novo; isso fica como está por enquanto, porque editar antes de publicar devolve o envio para revisão.
4. Clique em **Publicar**. Se aparecer uma confirmação simples (do tipo "publicar agora?"), confirme. Se aparecerem termos legais, declarações ou campos novos para preencher, pare e me pergunte.
5. Depois de publicar, anote o estado que a página mostra e o endereço público do conector no diretório, se houver.
6. Procure, sem clicar em editar, o que a página diz sobre mudar dados de um conector já publicado. Copie o texto exato e o e-mail ou formulário indicado.

## 2. Glama: build pelo modo stdio
1. Abra https://glama.ai/mcp/servers/gucancado/ceu-natal e confira o commit que o Glama mostra para o repositório. O esperado é `7c00de2` ou mais novo. Se for `cf0b385` ou outro sem o arquivo `app/stdio.py`, pare esta tarefa e me avise.
2. Entre na área de administração do servidor (Admin, Settings, Dockerfile ou Build) e preencha:
   - Imagem base: `debian:trixie-slim` (a que o Glama oferece); Python 3.11.
   - Passos de build: `["python -m pip install --require-hashes -r requirements.txt"]`. Se o build falhar dizendo que não há `pip`, troque por `["uv pip install --system --require-hashes -r requirements.txt"]`.
   - Commit fixo (pinned commit): deixe vazio.
   - Comando de execução (CMD): `python -m app.stdio`. Se o formulário montar o comando como lista, use `["python", "-m", "app.stdio"]`. Se ele já puser um `mcp-proxy --` na frente, mantenha e acrescente o comando depois.
   - Variáveis de ambiente: nenhuma. Se pedir um JSON Schema de ambiente, use `{"type": "object", "properties": {}}`.
3. Salve e dispare o build ("Deploy", "Build" ou "Re-evaluate"). Espere até 10 minutos, recarregando a página.
4. Se o build falhar, copie as últimas 30 linhas do log.
5. Abra https://glama.ai/mcp/servers/gucancado/ceu-natal/score e anote a nota e o que o Glama pede para melhorar.
6. Confira se as 9 tools aparecem na página do servidor: calcular_mapa_natal, calcular_sinastria, calcular_transitos, calcular_progressoes, calcular_mapa_composto, calcular_revolucao_solar, calcular_revolucao_lunar, listar_aspectos_tipos, healthcheck.
7. Anote se a página pública ainda mostra `mistico.gustavocancado.com.br` em algum lugar.

## Relatório final
Me devolva uma tabela: tarefa | estado (feito / travou / aguardando) | o que ficou registrado ou o motivo. Depois da tabela, traga à parte: o texto sobre mudança de dados de conector publicado, o log do build se ele falhou, a nota do Glama com as melhorias pedidas, e tudo o que alguma tela pediu para eu fazer.
