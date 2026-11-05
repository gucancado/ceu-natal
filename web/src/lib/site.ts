// Fonte única de URLs e dados do site. Nenhum outro arquivo deve hardcodar essas URLs.
export function semBarraFinal(u: string): string {
  return u.replace(/\/+$/, "");
}

const mcpUrl = semBarraFinal(
  process.env.NEXT_PUBLIC_MCP_URL || "https://astrologia-mcp.gustavocancado.com.br",
);

export const site = {
  nome: "Céu Natal",
  url: semBarraFinal(process.env.NEXT_PUBLIC_SITE_URL || "https://mistico.gustavocancado.com.br"),
  mcpUrl,
  mcpEndpoint: `${mcpUrl}/mcp/`,
  sseEndpoint: `${mcpUrl}/sse`,
  repoUrl: semBarraFinal(process.env.NEXT_PUBLIC_REPO_URL || "https://github.com/gucancado/ceu-natal"),
  limites: { porSessaoPorMin: 30, globalPorMin: 600 },
} as const;

// Contato do controlador (LGPD): escrito em texto no rodapé e na política, sem depender de JavaScript.
export const contato = { email: "gustavo.azvd@gmail.com" } as const;

// Frase da home: vai no <title> e na imagem de compartilhamento (OG).
export const fraseHome = "mapa astral calculado dentro do seu chat";
export const tituloHome = `${site.nome}: ${fraseHome}`;

// Descrição padrão do site (metadata e schema.org).
export const descricaoSite = "Mapa astral calculado com efemérides suíças dentro do seu assistente de IA.";
