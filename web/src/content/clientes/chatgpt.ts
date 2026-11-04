import { site } from "../../lib/site";
import { confira, type Cliente } from "./tipos";

export const chatgpt: Cliente = {
  slug: "chatgpt",
  nome: "ChatGPT",
  resumo:
    "No ChatGPT, o Céu Natal entra como servidor MCP personalizado na página de plugins, sem autenticação.",
  planoMinimo:
    "Disponível nos planos Business, Enterprise e Edu; no Pro, só ferramentas de leitura (as do Céu Natal são todas de leitura); no Plus, confira na sua conta.",
  semLogin: true,
  confianca: "media",
  passos: [
    "No navegador, abra `chatgpt.com/plugins`.",
    "Clique no **+** e depois em **Add custom MCP server**.",
    "Dê um nome, por exemplo `Céu Natal`. A descrição é opcional.",
    `Em **Connection**, cole a URL \`${site.mcpEndpoint}\`.`,
    "Na autenticação, escolha **No authentication**.",
    "Leia o aviso de risco, marque **I understand and want to continue** e clique em **Create as a plugin**.",
    "Revise as ferramentas encontradas e instale o plugin.",
    "Numa conversa nova, digite `@` e escolha o Céu Natal.",
  ],
  snippet: { linguagem: "text", codigo: site.mcpEndpoint },
  limitacoes: [
    "Em Business, Enterprise e Edu, o administrador decide quem pode criar plugins com MCP. A permissão vem desligada.",
    "O ChatGPT pode pedir sua confirmação antes de usar uma ferramenta.",
    "Políticas do workspace podem bloquear servidores personalizados.",
    `Com o ChatGPT em português, os menus podem aparecer traduzidos ${confira}.`,
  ],
  fontes: [
    {
      titulo: "OpenAI, Add custom MCP server",
      url: "https://developers.openai.com/api/docs/guides/custom-mcp-server",
    },
    {
      titulo: "OpenAI, Connect and test your plugin",
      url: "https://developers.openai.com/plugins/deploy/connect-chatgpt",
    },
    { titulo: "OpenAI, MCP", url: "https://learn.chatgpt.com/docs/extend/mcp" },
    {
      titulo: "OpenAI Help, Connecting custom MCP servers in ChatGPT",
      url: "https://help.openai.com/en/articles/12584461-connecting-custom-mcp-servers-in-chatgpt",
    },
  ],
};
