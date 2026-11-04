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
  confianca: "alta",
  passos: [
    "Abra as configurações do app: `Ctrl+,` no Windows, ou **File** > **Settings**. Na versão nova, a área se chama **Customize** > **Connectors**.",
    "Em **Connectors**, clique em **+ Add** e depois em **Add custom connector**.",
    `Dê um nome, cole a URL \`${site.mcpEndpoint}\`, escolha **No sign in** e clique em **Add**.`,
    "Numa conversa, clique no **+**, abra **Connectors** e ligue o Céu Natal.",
    `Se o conector não servir (por exemplo, no Free com o único conector já usado), instale o Node.js e abra o arquivo \`claude_desktop_config.json\`. No Windows ele fica em \`%APPDATA%\\Claude\\\`; no macOS, em \`~/Library/Application Support/Claude/\`. No app, o atalho é **Settings** > **Developer** > **Edit Config** ${confira}.`,
    "Cole o bloco abaixo, salve e feche o Claude Desktop por completo. Depois abra de novo.",
  ],
  snippet: { linguagem: "json", codigo: JSON.stringify(config, null, 2) },
  limitacoes: [
    "O arquivo de configuração não aceita só a URL do servidor. Por isso o bloco usa a ponte `mcp-remote`.",
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
