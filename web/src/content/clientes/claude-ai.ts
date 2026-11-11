import { site } from "../../lib/site";
import { confira, type Cliente } from "./tipos";

export const claudeAi: Cliente = {
  slug: "claude-ai",
  nome: "Claude",
  resumo: "No claude.ai, o Céu Natal entra como conector personalizado, sem login e sem chave.",
  planoMinimo:
    "Funciona em todos os planos. No Free, o limite é de 1 conector personalizado. No Team e no Enterprise, quem adiciona o conector é o administrador.",
  semLogin: true,
  confianca: "alta",
  abrir: { rotulo: "Abrir os conectores do Claude", url: "https://claude.ai/customize/connectors" },
  passos: [
    "Em **Customize** > **Connectors**, clique em **+ Add** > **Add custom connector**.",
    `Nome \`Céu Natal\`, URL \`${site.mcpEndpoint}\`, **No sign in**. Clique em **Add**.`,
    "Na conversa, ligue o Céu Natal em **+** > **Connectors**.",
  ],
  snippet: { linguagem: "text", codigo: site.mcpEndpoint },
  limitacoes: [
    "No Claude Desktop, siga os mesmos passos em **Customize** > **Connectors**.",
    `No Claude Code, rode \`claude mcp add --transport http --scope user ceu-natal ${site.mcpEndpoint}\` no terminal.`,
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
