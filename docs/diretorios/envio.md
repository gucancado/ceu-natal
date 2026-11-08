# Envio aos diretórios oficiais

Roteiro para publicar o Céu Natal no diretório de conectores do Claude e no de plugins do ChatGPT. Os dois exigem login e aceite de termos pelo responsável, por isso o envio é feito no navegador.

Dados comuns:

| Campo | Valor |
|---|---|
| URL do servidor | `https://astrologia-mcp.gustavocancado.com.br/mcp/` |
| Autenticação | nenhuma |
| Site | `https://mistico.gustavocancado.com.br` |
| Documentação | `https://mistico.gustavocancado.com.br/conectar` |
| Privacidade | `https://mistico.gustavocancado.com.br/privacidade` |
| Termos | `https://mistico.gustavocancado.com.br/termos` |
| Suporte | `https://github.com/gucancado/ceu-natal/issues` |
| Ícone | `docs/diretorios/icone.png` (512 × 512) |

## Claude

Portal: <https://claude.ai/directory/manage>, **Submit new**, **MCP connector**. Precisa de plano pago do Claude.

| Etapa | O que preencher |
|---|---|
| Connection | a URL do servidor |
| Tools | sincroniza sozinho; as 9 têm título e `readOnlyHint` |
| Listing, nome | `Céu Natal` |
| Listing, one-liner | `Accurate astrology charts for Claude, calculated with the Swiss Ephemeris instead of estimated.` |
| Listing, descrição | o texto de "Descrição" abaixo |
| Listing, categoria | a mais próxima de lifestyle ou entretenimento |
| Listing, slug | `ceu-natal` (permanente depois de publicado) |
| Use cases | "Calculate natal charts, synastry, composite charts, transits, progressions and solar and lunar returns." Nada é necessário para conectar. Só lê dados |
| Company | Gustavo Cançado, site acima, seu contato |
| Authentication | sem autenticação |
| Data handling | API própria; a cidade é geocodificada pelo GeoNames; sem dado de saúde; sem conteúdo patrocinado |
| Test & launch | "No account or login is needed. Add the server URL and run the example prompts." Use os exemplos abaixo |
| Compliance | as 7 declarações são suas |

## ChatGPT

Portal: <https://platform.openai.com/plugins>, **Upload new or existing plugin**.

1. Conclua a verificação **individual** em Organization settings. O diretório mostra o nome verificado, que deve ser o mesmo do site.
2. Envie `docs/diretorios/ceu-natal-plugin.zip` pelo caminho **With MCP**.
3. Em **MCPs**, clique em **Connect** com a URL do servidor e sem autenticação.
4. Na verificação de domínio, copie o token do portal. Ele precisa ser servido em `/.well-known/openai-apps-challenge`, pela env `OPENAI_APPS_CHALLENGE` do servidor. Depois de aplicada, clique em verificar.
5. Clique em **Scan Tools** e resolva o que aparecer.
6. Em **Review details**, informe a URL do vídeo: 1 a 3 minutos mostrando os 5 casos positivos e os 3 negativos do `plugin.json`, em link que abra sem login.
7. Escolha **Submit for review** e aceite as declarações. Aprovado, clique em **Publish plugin**.

## Descrição

Céu Natal gives Claude calculated astrology charts instead of estimated ones. It computes natal charts, synastry, composite charts, transits, secondary progressions and solar and lunar returns with the Swiss Ephemeris, and converts the birth city into coordinates and historical time zone before calculating.

The tools only calculate and return positions, houses and aspects. Interpretation is symbolic, for entertainment and self-reflection, and is not medical, legal, financial or psychological advice.

Free, with no account and no API key. Birth data is used only for the calculation and is not stored.

## Exemplos de pedido

1. Calculate the natal chart for someone born on 12/03/1990 at 14:30 in Belo Horizonte, MG, Brazil.
2. Compare two charts: person A born 12/03/1990 at 14:30 in Belo Horizonte, MG; person B born 25/07/1992 at 09:15 in São Paulo, SP.
3. For someone born 12/03/1990 at 14:30 in Belo Horizonte, MG, what are the transits on 01/01/2027?

## Refazer o pacote

Depois de alterar `docs/diretorios/plugin/`, gere o ZIP de novo com os arquivos na raiz, sem pasta de topo.
