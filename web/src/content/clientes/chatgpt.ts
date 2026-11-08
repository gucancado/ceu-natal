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
    "No navegador, abra `chatgpt.com/plugins`.",
    "Clique em **Adicionar**, no canto superior direito, e depois em **Adicionar servidor MCP personalizado**.",
    "Em **Nome**, escreva `Céu Natal`. Ícone e descrição podem ficar em branco.",
    `Em **Conexão**, deixe **URL do servidor** e cole \`${site.mcpEndpoint}\`.`,
    "Em **Autenticação**, escolha **Sem autenticação**.",
    "Marque **Entendo e quero continuar** e clique em **Criar como plugin**.",
    "Na janela seguinte, clique em **Conectar Céu Natal**.",
    "Volte à conversa e peça seu mapa. Se ela não enxergar o Céu Natal, abra uma conversa nova e digite `@` para escolhê-lo.",
  ],
  snippet: { linguagem: "text", codigo: site.mcpEndpoint },
  limitacoes: [
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
