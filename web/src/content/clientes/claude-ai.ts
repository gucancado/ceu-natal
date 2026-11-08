import { site } from "../../lib/site";
import { confira, type Cliente } from "./tipos";

export const claudeAi: Cliente = {
  slug: "claude-ai",
  nome: "Claude.ai",
  resumo: "No claude.ai, o Céu Natal entra como conector personalizado, sem login e sem chave.",
  planoMinimo:
    "Funciona em todos os planos. No Free, o limite é de 1 conector personalizado. No Team e no Enterprise, quem adiciona o conector é o administrador.",
  semLogin: true,
  confianca: "alta",
  abrir: { rotulo: "Abrir os conectores do Claude", url: "https://claude.ai/customize/connectors" },
  passos: [
    "Abra `claude.ai/customize/connectors` (menu **Customize** > **Connectors**).",
    "Clique em **+ Add** e depois em **Add custom connector**.",
    `Dê um nome, por exemplo \`Céu Natal\`, e cole a URL do servidor: \`${site.mcpEndpoint}\`.`,
    "Em **Authentication**, escolha **No sign in** e clique em **Add**.",
    "Numa conversa, clique no **+** no canto inferior esquerdo da caixa de mensagem, abra **Connectors** e ligue o Céu Natal.",
  ],
  snippet: { linguagem: "text", codigo: site.mcpEndpoint },
  limitacoes: [
    "O conector se liga por conversa, pelo **+** > **Connectors**.",
    "Para mudar o conector, remova e adicione de novo.",
    `Com o Claude em português, os menus podem aparecer traduzidos ${confira}.`,
  ],
  fontes: [
    {
      titulo: "Anthropic, Getting started with custom connectors using remote MCP",
      url: "https://support.claude.com/en/articles/11175166-getting-started-with-custom-connectors-using-remote-mcp",
    },
    {
      titulo: "Model Context Protocol, Connect to remote MCP Servers",
      url: "https://modelcontextprotocol.io/docs/develop/connect-remote-servers",
    },
  ],
};
