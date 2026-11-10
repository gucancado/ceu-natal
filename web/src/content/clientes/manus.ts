import { site } from "../../lib/site";
import type { Cliente } from "./tipos";

export const manus: Cliente = {
  slug: "manus",
  nome: "Manus",
  resumo: "No Manus, o Céu Natal entra como servidor MCP personalizado, pela URL do servidor.",
  planoMinimo: "A documentação do Manus não informa se servidores personalizados dependem do plano.",
  semLogin: true,
  confianca: "baixa",
  passos: [
    "Abra **Settings** > **Integrations** > **Custom MCP Servers** e clique em **Add Server**. Se o menu estiver diferente, procure em **Connectors** a opção de adicionar um MCP por URL.",
    `Em **Server name**, coloque \`Céu Natal\`. Em **Server URL**, cole \`${site.mcpEndpoint}\`.`,
    "O Céu Natal não usa login nem chave. Se houver campo de autenticação, deixe vazio ou escolha a opção sem autenticação.",
    "Salve. O Manus testa a conexão e carrega a lista de ferramentas.",
    "Numa tarefa, peça o cálculo e cite o Céu Natal.",
  ],
  snippet: { linguagem: "text", codigo: site.mcpEndpoint },
  limitacoes: [
    "Este guia segue a documentação do Manus e ainda não foi testado numa conta.",
    "A documentação não diz se o formulário aceita servidor sem autenticação. Se ele exigir uma chave, o Céu Natal não conecta por aqui.",
  ],
  fontes: [
    { titulo: "Manus Docs, Custom MCP Servers", url: "https://manus.im/docs/integrations/custom-mcp" },
    { titulo: "Manus, Connectors", url: "https://manus.im/features/connectors" },
  ],
};
