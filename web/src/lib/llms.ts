// Texto de /llms.txt e /llms-full.txt (formato llmstxt.org). Só dados → string, sem React nem Next.
import fs from "node:fs";
import path from "node:path";
import { clientes } from "../content/clientes";
import { guiasEn } from "../content/clientes/en";
import { faq } from "../content/faq";
import { landings } from "../content/landings";
import { tools } from "../content/tools";
import { site } from "./site";

export function gerarLlmsTxt(): string {
  const { porSessaoPorMin, globalPorMin } = site.limites;
  const linhas = [
    `# ${site.nome}`,
    "",
    "> Servidor MCP gratuito que calcula mapa astral com efemérides suíças (Swiss Ephemeris) dentro do seu assistente de IA, sem login.",
    "",
    `Site: ${site.url}`,
    `Texto completo (guias de conexão, perguntas frequentes e política de privacidade): ${site.url}/llms-full.txt`,
    `Autor: ${site.autor} (${site.autorUrl}). Projeto independente, de código aberto.`,
    "",
    "## Conectar",
    "",
    `- Endpoint MCP (Streamable HTTP): ${site.mcpEndpoint}`,
    ...clientes.map((c) => `- [Como conectar no ${c.nome}](${site.url}/?cliente=${c.slug}#conectar): ${c.resumo}`),
    "",
    "## Mapa rápido",
    "",
    `- [Mapa natal sem cadastro](${site.url}/mapa): formulário que devolve as posições em texto, com o pedido de conexão incluído, para colar no assistente.`,
    "",
    "## Técnicas",
    "",
    ...landings.map((l) => `- [${l.titulo}](${site.url}/${l.slug}): ${l.descricao}`),
    "",
    "## Ferramentas",
    "",
    ...tools.map((t) => `- \`${t.nome}\`: ${t.descricao}`),
    "",
    "## Formato de entrada",
    "",
    "- data: DD/MM/AAAA, ex.: 12/03/1990 (obrigatória).",
    "- hora: HH:MM, ex.: 14:30. Sem hora, o cálculo usa 12:00 no horário local, a Lua vem marcada como incerta e não saem casas nem ângulos.",
    '- local: "Cidade, UF" ou "Cidade, País", ex.: "Belo Horizonte, MG" ou "Lisboa, Portugal". Qualquer cidade do mundo.',
    "- sistema_casas: opcional, padrão P (Placidus).",
    "",
    "## Limites",
    "",
    `- ${porSessaoPorMin} chamadas por sessão por minuto.`,
    `- ${globalPorMin} chamadas no total por minuto, somando todas as sessões.`,
    "- Ao passar do limite, a resposta vem com isError pedindo para aguardar e tentar de novo.",
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
    "## English",
    "",
    `- Free astrology MCP server (natal chart, synastry, composite, transits, progressions, solar and lunar returns) calculated with the Swiss Ephemeris. No login, no API key. Endpoint: ${site.mcpEndpoint}`,
    "- Tool names and results are in Portuguese; the assistant translates when answering. Dates as DD/MM/YYYY; any city in the world.",
    `- [English overview and setup](${site.url}/en)`,
    `- [llms.txt in English](${site.url}/en/llms.txt)`,
    "",
  ];
  return linhas.join("\n");
}

// Versão em inglês, servida em /en/llms.txt. Os nomes das ferramentas e os resultados continuam em
// português (é o que o servidor devolve); o texto em volta explica isso a quem lê em inglês.
export function gerarLlmsTxtEn(): string {
  const { porSessaoPorMin, globalPorMin } = site.limites;
  const linhas = [
    `# ${site.nome}`,
    "",
    "> Free, open-source MCP server that calculates astrology charts with the Swiss Ephemeris inside your AI assistant. No login, no API key.",
    "",
    `Site: ${site.url}/en`,
    `Portuguese version, with full connection guides, FAQ and privacy policy: ${site.url}/llms.txt and ${site.url}/llms-full.txt`,
    `Author: ${site.autor} (${site.autorUrl}/en). Independent, open-source project.`,
    "",
    "## Connect",
    "",
    `- MCP endpoint (Streamable HTTP, no authentication): ${site.mcpEndpoint}`,
    ...clientes.flatMap((c) => {
      const guia = guiasEn[c.slug];
      if (!guia) return [];
      // Os passos foram escritos para a página, onde o bloco para copiar vem logo abaixo.
      const passos = guia.passos.join(" ").replace(/\bthe (block|command) below\b/g, "the $1 shown on the linked page");
      return [`- [${c.nome}](${site.url}/en?cliente=${c.slug}#conectar): ${passos}`];
    }),
    "",
    "## What it calculates",
    "",
    "- Natal chart, synastry, composite chart, transits, secondary progressions, solar return and lunar return.",
    "- The birth city is converted into coordinates and historical time zone before the calculation.",
    "- It calculates and does not interpret: the assistant reads the calculated positions and writes the interpretation.",
    "",
    "## Tools",
    "",
    ...tools.map((t) => `- \`${t.nome}\`: ${t.descricaoEn}`),
    "",
    "## Input format",
    "",
    "- data (date): DD/MM/YYYY, e.g. 12/03/1990 (required).",
    "- hora (time): HH:MM, e.g. 14:30. Without a time, the calculation uses 12:00 local time, the Moon is flagged as uncertain and there are no houses or angles.",
    '- local (place): "City, Country", e.g. "Lisbon, Portugal" or "Tokyo, Japan". Any city in the world.',
    "- sistema_casas (house system): optional, default P (Placidus).",
    "",
    "## Language",
    "",
    "- Tool names and results are in Portuguese; the assistant translates when answering.",
    `- The quick chart form at ${site.url}/mapa is in Portuguese only.`,
    "",
    "## Limits",
    "",
    `- ${porSessaoPorMin} calls per session per minute.`,
    `- ${globalPorMin} calls per minute in total, across all sessions.`,
    "- Over the limit, the response comes with isError asking to wait and try again.",
    "",
    "## Privacy",
    "",
    `- Policy (in Portuguese): ${site.url}/privacidade`,
    "- Birth data sent through MCP is used only for the calculation and is not stored. Logs keep the tool name, status, duration and, when a city is given, the city and country; never the birth date or time. They are kept for up to 90 days.",
    "",
    "## Code",
    "",
    `- Repository: ${site.repoUrl}`,
    "- License: AGPL-3.0",
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
