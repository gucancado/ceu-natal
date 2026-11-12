// Passos dos guias de conexão em inglês, para a home em /en. Os menus seguem o app em inglês.
import { site } from "../../lib/site";

export type GuiaEn = { passos: string[]; abrir?: string };

const conectorClaude = [
  "In **Customize** > **Connectors**, click **+ Add** > **Add custom connector**.",
  `Name \`Céu Natal\`, URL \`${site.mcpEndpoint}\`, **No sign in**. Click **Add**.`,
  "In a chat, turn Céu Natal on under **+** > **Connectors**.",
];

export const guiasEn: Record<string, GuiaEn> = {
  "claude-ai": { passos: conectorClaude, abrir: "Open Claude connectors" },
  "claude-desktop": { passos: conectorClaude },
  "claude-code": { passos: ["Run the command below in a terminal.", "Check it with `claude mcp list`."] },
  chatgpt: {
    passos: [
      "At `chatgpt.com/plugins`, click **Add** > **Add custom MCP server**.",
      `Name \`Céu Natal\`, URL \`${site.mcpEndpoint}\`, **No authentication**.`,
      "Tick **I understand and want to continue**, click **Create as plugin** and **Connect Céu Natal**.",
    ],
    abrir: "Open ChatGPT plugins",
  },
  gemini: {
    passos: [
      "The Gemini app doesn't take connectors in every country yet. Use Google's Antigravity (app, IDE or the `agy` CLI).",
      "Paste the block below into `~/.gemini/config/mcp_config.json` and save.",
    ],
  },
  manus: {
    passos: [
      "In **Settings** > **Integrations** > **Custom MCP Servers**, click **Add Server**.",
      `Name \`Céu Natal\`, URL \`${site.mcpEndpoint}\`, no authentication. Save.`,
    ],
  },
  cursor: {
    passos: [
      "Paste the block below into `~/.cursor/mcp.json` and save.",
      "Check under **Customize** that Céu Natal shows as enabled.",
    ],
  },
  n8n: {
    passos: [
      "In an **AI Agent** node, add the **MCP Client Tool**.",
      `**Endpoint** \`${site.mcpEndpoint}\`, **Server Transport** **HTTP Streamable**, **Authentication** **None**.`,
    ],
  },
};
