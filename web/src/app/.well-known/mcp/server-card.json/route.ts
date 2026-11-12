import { tools } from "@/content/tools";
import { descricaoSite, site } from "@/lib/site";

// Server card (proposta SEP-1649 do MCP): metadados para descobrir o servidor sem conectar.
// Sem versão aqui de propósito: ela mora no servidor (initialize) e no server.json, e não deve divergir.
export const dynamic = "force-static";

export function GET() {
  return Response.json({
    name: "io.github.gucancado/ceu-natal",
    title: site.nome,
    description: `${descricaoSite} Astrology MCP server: natal chart, synastry, composite, transits, progressions, solar and lunar returns (Swiss Ephemeris).`,
    websiteUrl: site.url,
    documentationUrl: `${site.url}/llms.txt`,
    repository: { url: site.repoUrl, source: "github" },
    iconUrl: `${site.url}/icon.svg`,
    remotes: [{ type: "streamable-http", url: site.mcpEndpoint }],
    authentication: { required: false },
    capabilities: { tools: { listChanged: false } },
    tools: tools.map((t) => ({ name: t.nome, description: t.descricao })),
    languages: ["pt-BR", "en"],
    license: "AGPL-3.0-or-later",
  });
}
