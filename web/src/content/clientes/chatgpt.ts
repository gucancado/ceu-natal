import { site } from "../../lib/site";
import type { Cliente } from "./tipos";

export const chatgpt: Cliente = {
  slug: "chatgpt",
  nome: "ChatGPT",
  resumo:
    "No ChatGPT, o Céu Natal entra como servidor MCP personalizado na página de plugins, sem autenticação.",
  planoMinimo:
    "Testado e funcionando no Plus. No Pro, só ferramentas de leitura (as do Céu Natal são todas de leitura). Em Business, Enterprise e Edu, depende do administrador.",
  semLogin: true,
  confianca: "media",
  abrir: { rotulo: "Abrir os plugins do ChatGPT", url: "https://chatgpt.com/plugins" },
  passos: [
    "Em `chatgpt.com/plugins`, clique em **Adicionar** > **Adicionar servidor MCP personalizado**.",
    `Nome \`Céu Natal\`, URL \`${site.mcpEndpoint}\`, **Sem autenticação**.`,
    "Marque **Entendo e quero continuar**, clique em **Criar como plugin** e em **Conectar Céu Natal**.",
  ],
  snippet: { linguagem: "text", codigo: site.mcpEndpoint },
  limitacoes: [
    "Se a conversa não enxergar o Céu Natal, abra uma conversa nova e digite `@` para escolhê-lo.",
    "Em Business, Enterprise e Edu, o administrador decide quem pode criar plugins com MCP. A permissão vem desligada.",
    "O ChatGPT pode pedir sua confirmação antes de usar uma ferramenta.",
    "Políticas do workspace podem bloquear servidores personalizados.",
    "Com o ChatGPT em inglês, os botões são **Add custom MCP server**, **No authentication** e **Create as a plugin**.",
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
