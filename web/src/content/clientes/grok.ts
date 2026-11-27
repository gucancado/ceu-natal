import { site } from "../../lib/site";
import type { Cliente } from "./tipos";

export const grok: Cliente = {
  slug: "grok",
  nome: "Grok",
  resumo: "No Grok, o Céu Natal entra como conector personalizado, pela URL do servidor.",
  planoMinimo: "A xAI diz que os conectores valem para todos os usuários do Grok. Em contas Business e Enterprise, o administrador libera o conector antes.",
  semLogin: true,
  confianca: "baixa",
  abrir: { rotulo: "Abrir conectores do Grok", url: "https://grok.com/connectors" },
  passos: [
    "Em `grok.com/connectors`, clique em **New Connector** > **Custom**.",
    `Nome \`Céu Natal\`, URL \`${site.mcpEndpoint}\`, sem autenticação. Clique em **Add Connector**.`,
  ],
  snippet: { linguagem: "text", codigo: site.mcpEndpoint },
  limitacoes: [
    "Este guia segue a documentação da xAI e ainda não foi testado numa conta.",
    "A documentação não diz se os conectores funcionam nos apps de celular. No navegador, em grok.com, funcionam.",
  ],
  fontes: [
    { titulo: "xAI Docs, Connectors", url: "https://docs.x.ai/grok/connectors" },
  ],
};
