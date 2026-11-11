import { site } from "../../lib/site";
import { confira, type Cliente } from "./tipos";

const config = {
  mcpServers: {
    "ceu-natal": {
      command: "npx",
      args: ["mcp-remote", site.mcpEndpoint, "--transport", "http-only"],
    },
  },
};

export const claudeDesktop: Cliente = {
  slug: "claude-desktop",
  nome: "Claude Desktop",
  resumo:
    "No Claude Desktop, o caminho é o mesmo conector do claude.ai. Se ele não servir, a ponte local mcp-remote resolve.",
  planoMinimo:
    "Conector: todos os planos, com limite de 1 conector personalizado no Free. Ponte mcp-remote: qualquer plano, com o Node.js instalado.",
  semLogin: true,
  confianca: "media",
  passos: [
    "Em **Customize** > **Connectors**, clique em **+ Add** > **Add custom connector**.",
    `Nome \`Céu Natal\`, URL \`${site.mcpEndpoint}\`, **No sign in**. Clique em **Add**.`,
    "Na conversa, ligue o Céu Natal em **+** > **Connectors**.",
  ],
  snippet: { linguagem: "json", codigo: JSON.stringify(config, null, 2) },
  limitacoes: [
    `Se o conector não servir (por exemplo, no Free com o único conector já usado), instale o Node.js, cole o bloco acima em **Settings** > **Developer** > **Edit Config** ${confira} e reabra o app.`,
    "Pelos relatos de 2026, o arquivo de configuração não aceita só a URL do servidor. Por isso o bloco usa a ponte `mcp-remote`.",
    "Para mudar o conector, remova e adicione de novo.",
    "No Windows, o log da conexão fica em `C:\\Users\\<usuário>\\AppData\\Local\\Claude\\Logs\\mcp.log`.",
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
    { titulo: "mcp-remote, README", url: "https://github.com/geelen/mcp-remote" },
  ],
};
