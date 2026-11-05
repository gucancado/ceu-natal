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

// Email em partes: nunca aparece inteiro no HTML (ver components/email-oculto.tsx).
export const contato = { usuario: "gustavo.azvd", dominio: "gmail.com" } as const;

// Descrição padrão do site (metadata e schema.org).
export const descricaoSite = "Mapa astral calculado com efemérides suíças dentro do seu assistente de IA.";
