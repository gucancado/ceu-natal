# Como conectar o `ceu-natal` no seu Claude.ai

O guia canônico, mantido em dia com a interface e com os limites de cada plano,
é a versão web: https://mistico.gustavocancado.com.br/conectar/claude-ai. Para os
outros clientes da Anthropic, veja
https://mistico.gustavocancado.com.br/conectar/claude-desktop e
https://mistico.gustavocancado.com.br/conectar/claude-code. Este arquivo só
resume o endpoint, as ferramentas e o diagnóstico.

Endpoint MCP (Streamable HTTP): `https://astrologia-mcp.gustavocancado.com.br/mcp/`

---

## As 9 ferramentas

| Tool | O que faz |
|------|-----------|
| `calcular_mapa_natal` | Posições, casas, ângulos, aspectos e síntese de um mapa natal. |
| `calcular_sinastria` | Aspectos cruzados entre duas pessoas e planetas de A nas casas de B. |
| `calcular_transitos` | Posições em uma data, aspectos com o mapa natal e destaque de trânsitos lentos. |
| `calcular_progressoes` | Progressões secundárias (1 dia = 1 ano) para uma data alvo, com Lua e Sol progredidos. |
| `calcular_mapa_composto` | Mapa composto por midpoints de duas pessoas. |
| `calcular_revolucao_solar` | Revolução solar de um ano (natal com hora e local, ano, local da revolução). |
| `calcular_revolucao_lunar` | Próxima revolução lunar a partir de uma data (natal, data de referência, local da revolução). |
| `listar_aspectos_tipos` | Tipos de aspectos suportados, ângulos e orbes. |
| `healthcheck` | Status do servidor. |

---

## Diagnóstico

### "No matching tools found" / "Nenhuma ferramenta encontrada"

- Confira se o conector está ligado nesta conversa (o conector se liga por
  conversa; veja o guia web).
- Confira se a URL é exatamente `https://astrologia-mcp.gustavocancado.com.br/mcp/`.
- Peça ao Claude para listar as ferramentas do `ceu-natal`: devem aparecer as 9
  da tabela acima.

### Verificação direta (sem cliente MCP)

```bash
curl https://astrologia-mcp.gustavocancado.com.br/health
curl https://astrologia-mcp.gustavocancado.com.br/tools
```

`/health` mostra se o servidor está no ar; `/tools` lista os schemas das 9
ferramentas.

---

Política de privacidade: [docs/legal/privacidade.md](legal/privacidade.md).
Problemas e sugestões: https://github.com/gucancado/ceu-natal/issues
