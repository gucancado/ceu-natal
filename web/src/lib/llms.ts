// Texto de /llms.txt e /llms-full.txt (formato llmstxt.org). Só dados → string, sem React nem Next.
import fs from "node:fs";
import path from "node:path";
import { clientes } from "../content/clientes";
import { faq } from "../content/faq";
import { tools } from "../content/tools";
import { site } from "./site";

export function gerarLlmsTxt(): string {
  const { porSessaoPorMin, globalPorMin } = site.limites;
  const linhas = [
    `# ${site.nome}`,
    "",
    "> Servidor MCP gratuito que calcula mapa astral com efemérides suíças (Swiss Ephemeris) dentro do seu assistente de IA, sem login.",
    "",
    "## Conectar",
    "",
    `- Endpoint MCP (Streamable HTTP): ${site.mcpEndpoint}`,
    `- Endpoint legado (SSE): ${site.sseEndpoint}`,
    ...clientes.map((c) => `- [Como conectar no ${c.nome}](${site.url}/conectar/${c.slug}): ${c.resumo}`),
    "",
    "## Mapa rápido",
    "",
    `- [Mapa natal sem cadastro](${site.url}/mapa): formulário que devolve as posições em texto, com o pedido de conexão incluído, para colar no assistente.`,
    "",
    "## Ferramentas",
    "",
    ...tools.map((t) => `- \`${t.nome}\`: ${t.descricao}`),
    "",
    "## Limites",
    "",
    `- ${porSessaoPorMin} chamadas por sessão por minuto.`,
    `- ${globalPorMin} chamadas no total por minuto, somando todas as sessões.`,
    "",
    "## Privacidade",
    "",
    `- Política: ${site.url}/privacidade`,
    "- Os logs registram o nome da tool, o status, a duração e, quando há cidade, a cidade e o país; nunca a data ou a hora de nascimento. Ficam guardados por até 90 dias.",
    "",
    "## Código",
    "",
    `- Repositório: ${site.repoUrl}`,
    "- Licença: AGPL-3.0",
    "",
  ];
  return linhas.join("\n");
}

export function gerarLlmsFull(): string {
  const bruta = fs.readFileSync(path.join(process.cwd(), "src/content/legal/privacidade.md"), "utf8").trim();
  // O H1 do arquivo sai: a seção "## Política de privacidade" já faz de título.
  const politica = bruta.replace(/^# .*(\r?\n|$)/, "").trim();
  const partes = [gerarLlmsTxt(), "## Guias de conexão", ""];
  for (const c of clientes) {
    partes.push(`### ${c.nome}`, "", ...c.passos.map((p, i) => `${i + 1}. ${p}`), "");
    if (c.limitacoes.length > 0) {
      partes.push("Limitações:", "", ...c.limitacoes.map((l) => `- ${l}`), "");
    }
  }
  partes.push("## Perguntas frequentes", "");
  for (const item of faq) partes.push(`**${item.pergunta}**`, "", item.resposta, "");
  partes.push("## Política de privacidade", "", politica, "");
  return partes.join("\n");
}
