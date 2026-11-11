import { site } from "../../lib/site";
import type { Cliente } from "./tipos";

export const n8n: Cliente = {
  slug: "n8n",
  nome: "n8n",
  resumo: "No n8n, o nó MCP Client Tool liga as ferramentas do Céu Natal a um AI Agent.",
  planoMinimo: "n8n 1.104.0 ou mais novo, no self-hosted ou no n8n Cloud.",
  semLogin: true,
  confianca: "alta",
  passos: [
    "Num nó **AI Agent**, adicione a ferramenta **MCP Client Tool**.",
    `**Endpoint** \`${site.mcpEndpoint}\`, **Server Transport** **HTTP Streamable**, **Authentication** **None**.`,
  ],
  snippet: { linguagem: "text", codigo: site.mcpEndpoint },
  limitacoes: [
    "Antes da versão 1.104.0 só existe o modo SSE, que o Céu Natal não aceita. Atualize o n8n.",
    "Workflows antigos guardam a versão velha do nó, com SSE como padrão. Recrie o nó para pegar o padrão novo.",
    "A documentação oficial do nó ainda descreve só o modo SSE. A interface atual tem os campos acima.",
  ],
  fontes: [
    {
      titulo: "n8n, código-fonte do MCP Client Tool",
      url: "https://github.com/n8n-io/n8n/blob/master/packages/@n8n/nodes-langchain/nodes/mcp/McpClientTool/McpClientTool.node.ts",
    },
    { titulo: "n8n, PR #15454 (HTTP Streamable)", url: "https://github.com/n8n-io/n8n/pull/15454" },
    {
      titulo: "n8n Docs, MCP Client Tool",
      url: "https://docs.n8n.io/integrations/builtin/cluster-nodes/sub-nodes/n8n-nodes-langchain.toolmcp/",
    },
  ],
};
