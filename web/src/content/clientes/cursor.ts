import { site } from "../../lib/site";
import { confira, type Cliente } from "./tipos";

const config = { mcpServers: { "ceu-natal": { url: site.mcpEndpoint } } };

export const cursor: Cliente = {
  slug: "cursor",
  nome: "Cursor",
  resumo: "No Cursor, o Céu Natal entra pelo arquivo mcp.json, com a URL do servidor.",
  planoMinimo: "A documentação do Cursor não cita restrição de plano para MCP.",
  semLogin: true,
  confianca: "alta",
  passos: [
    "Abra ou crie o arquivo `~/.cursor/mcp.json`, que vale para todos os projetos. Para um projeto só, use `.cursor/mcp.json` na pasta do projeto.",
    "Cole o bloco abaixo e salve. Se o arquivo já tiver outros servidores, acrescente só a entrada `ceu-natal` dentro de `mcpServers`.",
    `Pela interface, os servidores ficam na página **Customize**, na barra lateral. Versões recentes também têm **Cursor Settings** > **Tools & MCP** > **New MCP Server**, que abre o mesmo arquivo ${confira}.`,
    "Confira em **Customize** se o Céu Natal aparece habilitado.",
  ],
  snippet: { linguagem: "json", codigo: JSON.stringify(config, null, 2) },
  limitacoes: [
    "Se não conectar, veja os logs no painel **Output** > **MCP Logs**.",
    "O Cursor reconhece o tipo de conexão pela chave `url`. Não precisa de campo `type`.",
  ],
  fontes: [
    { titulo: "Cursor Docs, Model Context Protocol", url: "https://cursor.com/docs/context/mcp" },
    {
      titulo: "DesignRevision, Add an MCP server to Cursor",
      url: "https://designrevision.com/blog/add-mcp-server-to-cursor",
    },
  ],
};
