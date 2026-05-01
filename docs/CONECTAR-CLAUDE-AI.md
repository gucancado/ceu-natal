# Como conectar o `ceu-natal` no seu Claude.ai

Guia rápido pra usar o servidor MCP de astrologia (mapas natais, sinastria,
trânsitos, progressões, composto) direto do chat do Claude.ai. Tempo total
estimado: 3 minutos.

---

## Pré-requisitos

- Plano **Claude Pro, Team ou Enterprise** (a opção "Conectores personalizados"
  não aparece no plano Free).
- Acesso à web em `claude.ai`.

Se você só tem Free, dá pra usar via Claude Desktop também (instruções no
final).

---

## Passo a passo — Claude.ai web

### 1. Abrir as configurações de conectores

1. Entrar em `https://claude.ai`
2. Clicar no ícone de perfil (canto superior direito) → **Settings** /
   **Configurações**
3. Na barra lateral, escolher **Connectors** / **Conectores**
4. Clicar em **Add custom connector** / **Adicionar conector personalizado**

### 2. Preencher o formulário

| Campo | Valor |
|-------|-------|
| **Nome** | `ceu-natal` |
| **URL** | `https://ceu-natal-api.pu5h6p.easypanel.host/sse` |

Clicar em **Adicionar** / **Add**.

> **Sobre autenticação:** o servidor está em modo aberto no momento — você
> não precisa preencher nada em "Configurações avançadas" (OAuth Client ID /
> Secret). Pula esses campos.

### 3. Habilitar o conector na conversa

1. Abrir uma conversa nova
2. Clicar no ícone de **ferramentas / 🔧** (ou similar) no canto da caixa de
   mensagem
3. Marcar `ceu-natal` na lista de conectores ativos

A primeira vez que ativar, o Claude vai pedir confirmação para usar a
ferramenta — aceite.

### 4. Testar

No chat, mande:

```
Você consegue usar o MCP ceu-natal? Liste as tools disponíveis.
```

Esperado: o Claude responde listando as 7 tools (`calcular_mapa_natal`,
`calcular_sinastria`, `calcular_transitos`, `calcular_progressoes`,
`calcular_mapa_composto`, `listar_aspectos_tipos`, `healthcheck`).

---

## Como usar

Conversa exemplo (substitua pelos seus dados reais):

> Calcule meu mapa natal: nasci em 24/07/1989, às 09:20, em Belo Horizonte/MG.
> Comente os pontos principais.

> Quais trânsitos importantes estão acontecendo no meu mapa hoje?

> Faça uma sinastria entre eu (24/07/1989, 09:20, BH) e a Naiara (09/06/1989,
> 14:05, BH). Foca nos aspectos mais relevantes.

> Calcula o mapa composto entre nós dois.

> Como estão minhas progressões secundárias hoje? Onde a Lua progredida está?

### O que cada tool faz

| Tool | O que retorna |
|------|--------------|
| `calcular_mapa_natal` | Posições planetárias, casas, ângulos (ASC, MC), aspectos, síntese (elementos, hemisférios, stelliums) |
| `calcular_sinastria` | Aspectos cruzados entre duas pessoas + planetas de A nas casas de B |
| `calcular_transitos` | Posições atuais + aspectos com seu mapa natal + destaque de trânsitos lentos (Saturno, Plutão...) |
| `calcular_progressoes` | "Mapa progredido" pra uma data alvo (técnica 1 dia = 1 ano), com Lua e Sol progredidos em destaque |
| `calcular_mapa_composto` | Mapa da "relação como entidade" — midpoint dos planetas de duas pessoas |
| `listar_aspectos_tipos` | Tipos de aspectos suportados, ângulos e orbes |
| `healthcheck` | Status do servidor |

### Formato de entrada

Para qualquer tool que pede dados de nascimento:

- **`data`** (obrigatório): formato `DD/MM/YYYY`, ex: `24/07/1989`
- **`hora`** (opcional, mas recomendado): `HH:MM`, ex: `09:20` — sem hora,
  casas e ângulos não saem
- **`local`** (opcional, mas recomendado): `"Cidade, UF"` ou `"Cidade, País"`,
  ex: `"Belo Horizonte, MG"` ou `"Lisboa, Portugal"`
- **`nome`** (opcional): só pra identificar no retorno

---

## Caminho alternativo — Claude Desktop (Free, Pro, qualquer plano)

Se você está no Free ou prefere o Claude Desktop:

1. Abrir o arquivo de configuração:
   - **macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`
   - **Windows:** `%APPDATA%\Claude\claude_desktop_config.json`
   - **Linux:** `~/.config/Claude/claude_desktop_config.json`

2. Adicionar (ou completar) este conteúdo:

```json
{
  "mcpServers": {
    "ceu-natal": {
      "url": "https://ceu-natal-api.pu5h6p.easypanel.host/sse"
    }
  }
}
```

3. Reiniciar o Claude Desktop.
4. Numa conversa, clicar no ícone 🔌 — `ceu-natal` deve aparecer com 7
   ferramentas.

---

## Troubleshooting

### "No matching tools found" / "Nenhuma ferramenta encontrada"

- Verifica se o conector está **habilitado** na conversa (ícone de
  ferramentas/🔧 antes de mandar a mensagem).
- Confirma que a URL é exatamente `https://ceu-natal-api.pu5h6p.easypanel.host/sse`
  (sem espaços, sem barra no final).

### Erro de geocodificação ("Não foi possível geocodificar...")

- Confere se o nome da cidade está escrito corretamente.
- Tenta a forma `"Cidade, País"` em vez de só `"Cidade"`.
- Se for cidade pequena e pouco conhecida, tenta a cidade grande mais próxima.

### O servidor está fora do ar

Cola no chat: `chame healthcheck do ceu-natal`. Se der erro, me avisa
(@gucancado) que reinicio.

### Verificação direta (sem cliente MCP)

Se quiser bater diretamente no servidor:

```bash
curl https://ceu-natal-api.pu5h6p.easypanel.host/health
curl https://ceu-natal-api.pu5h6p.easypanel.host/tools
```

`/health` é público; `/tools` lista os schemas das 7 ferramentas.

---

## Privacidade

- O servidor **não armazena nada** sobre as pessoas que você consulta —
  cálculo é stateless por request.
- O **único cache** é de coordenadas de cidade (lat/lng/timezone), pra evitar
  bater repetido nas APIs de geocoding. Não tem informação pessoal aí.
- Logs do servidor registram apenas o nome da tool chamada, sem os argumentos.

---

## Reportar problemas

Issues, sugestões ou bugs: https://github.com/gucancado/ceu-natal/issues
