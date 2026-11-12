Configure o build do Céu Natal no Glama, no meu navegador, com a conta GitHub `gucancado` já logada. O servidor já está reivindicado. Agora o repositório tem um modo stdio, que é o que o Glama exige.

Regras:
- Não pague nada.
- Use só os dados abaixo. Não invente informação.
- Se o formulário pedir algo que não está aqui, anote o que ele pede e pare.

Dados:
- Repositório: https://github.com/gucancado/ceu-natal (branch `main`, Python 3.11)
- Instalação: `python -m pip install --require-hashes -r requirements.txt`
- Comando do servidor (stdio): `python -m app.stdio`
- Nenhuma variável de ambiente é obrigatória e não há chave de API.

Passos:
1. Abra https://glama.ai/mcp/servers/gucancado/ceu-natal e confira o commit que o Glama mostra para o repositório. Se ainda for `cf0b385` (ou outro sem o arquivo `app/stdio.py`), o Glama não sincronizou: pare e me avise. Se for mais novo, entre na área de administração do servidor (Admin, Settings, Dockerfile ou Build).
2. Preencha:
   - Imagem base: `debian:trixie-slim` (a que o Glama oferece); Python 3.11.
   - Passos de build: `["python -m pip install --require-hashes -r requirements.txt"]`. Se o build falhar dizendo que não há `pip`, troque por `["uv pip install --system --require-hashes -r requirements.txt"]`.
   - Commit fixo (pinned commit): deixe vazio.
   - Comando de execução (CMD): `python -m app.stdio`. Se o formulário montar o comando como lista, use `["python", "-m", "app.stdio"]`. Se ele já puser um `mcp-proxy --` na frente, mantenha e acrescente o comando depois.
   - Variáveis de ambiente: nenhuma. Se pedir um JSON Schema de ambiente, use `{"type": "object", "properties": {}}`.
3. Salve e dispare o build ("Deploy", "Build" ou "Re-evaluate"). Espere até 10 minutos, recarregando a página.
4. Se o build falhar, copie as últimas 30 linhas do log.
5. Abra https://glama.ai/mcp/servers/gucancado/ceu-natal/score e anote a nota e o que o Glama pede para melhorar.
6. Confira se as 9 tools aparecem na página do servidor (calcular_mapa_natal, calcular_sinastria, calcular_transitos, calcular_progressoes, calcular_mapa_composto, calcular_revolucao_solar, calcular_revolucao_lunar, listar_aspectos_tipos, healthcheck).

Relatório final: estado do build (passou / falhou, com o log), a nota, as tools que apareceram e a lista de melhorias pedidas.
