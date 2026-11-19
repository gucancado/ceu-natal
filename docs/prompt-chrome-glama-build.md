Refaça o build do Céu Natal no Glama, no meu navegador, com a conta GitHub `gucancado` já logada. A configuração já está salva (imagem `debian:trixie-slim`, Python 3.11, CMD `["mcp-proxy","--","python","-m","app.stdio"]`, commit fixo vazio, schema de ambiente vazio). O build anterior falhou no passo de instalação com `externally-managed-environment`: o Python da imagem é instalado pelo uv e recusa o `pip install` sem uma opção a mais. Só o passo de build muda.

Regras:
- Não pague nada. Não ligue o Boost.
- Não mude nenhum campo além do passo de build.
- Use só os dados abaixo. Não invente informação. Se o formulário pedir algo que não está aqui, anote o que ele pede e pare.

Dados:
- Página do servidor: https://glama.ai/mcp/servers/gucancado/ceu-natal
- Passo de build novo: `["python -m pip install --break-system-packages --require-hashes -r requirements.txt"]`
- Passo de build reserva: `["uv pip install --system --break-system-packages --require-hashes -r requirements.txt"]`
- Versão para a release: `2.2.6`

Passos:
1. Abra a página do servidor, entre na administração e abra a página Dockerfile.
2. Troque o passo de build pelo passo novo. Confira na pré-visualização que os outros campos continuam como descrito acima e salve.
3. Dispare **Build** (não "Build & Release"). Espere até 10 minutos, recarregando a página.
4. Se o build falhar no passo de instalação, troque pelo passo reserva, salve e dispare **Build** de novo, uma vez só. Se falhar outra vez, ou falhar em outro passo, copie as últimas 40 linhas do log e pare.
5. Com o build aprovado, clique em **Make Release** e use a versão `2.2.6`. Se a tela pedir notas da release, escreva `Céu Natal 2.2.6`. Se pedir qualquer outra coisa, anote e pare.
6. Abra a página pública do servidor e anote: a nota (score) e cada item que o Glama ainda pede para melhorar, se a release aparece, e se as 9 tools continuam listadas.

Relatório final: uma tabela com tarefa | estado (feito / travou) | o que ficou registrado ou o motivo. Depois da tabela, traga o passo de build que funcionou, o log se algum build falhou, e a nota com a lista de melhorias pedidas.
