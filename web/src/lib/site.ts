// Fonte única de URLs e dados do site. Nenhum outro arquivo deve hardcodar essas URLs.
export function semBarraFinal(u: string): string {
  return u.replace(/\/+$/, "");
}

const mcpUrl = semBarraFinal(
  process.env.NEXT_PUBLIC_MCP_URL || "https://astrologia-mcp.gustavocancado.com.br",
);

export const site = {
  nome: "Céu Natal",
  url: semBarraFinal(process.env.NEXT_PUBLIC_SITE_URL || "https://ceunatal.gustavocancado.com.br"),
  // Endereços antigos do site: continuam respondendo, só para redirecionar para `url`.
  hostsAntigos: ["mistico.gustavocancado.com.br"],
  mcpUrl,
  mcpEndpoint: `${mcpUrl}/mcp/`,
  repoUrl: semBarraFinal(process.env.NEXT_PUBLIC_REPO_URL || "https://github.com/gucancado/ceu-natal"),
  autor: "Gustavo Cançado",
  autorUrl: "https://gustavocancado.com.br",
  // Perfis públicos do autor (schema.org sameAs).
  autorPerfis: ["https://www.linkedin.com/in/gustavocancado/", "https://github.com/gucancado"],
  limites: { porSessaoPorMin: 30, globalPorMin: 600 },
} as const;

// Frase da home: vai no <title> e na imagem de compartilhamento (OG).
export const fraseHome = "mapa astral calculado dentro do seu chat";
export const tituloHome = `${site.nome}: ${fraseHome}`;

// <link rel="alternate" type="text/plain"> para o /llms.txt. Página que define `alternates` repete este
// campo, porque o Next não mescla `alternates` com o do layout.
export const alternativaLlms = { "text/plain": [{ url: "/llms.txt", title: "llms.txt" }] };
export const alternativaLlmsEn = { "text/plain": [{ url: "/en/llms.txt", title: "llms.txt" }] };

// Imagem de compartilhamento das páginas que definem o próprio `openGraph` (o Next não mescla com o do
// layout, então a largura, a altura e o texto alternativo precisam vir junto).
export const imagemOg = { url: "/opengraph-image", width: 1200, height: 630, alt: tituloHome, type: "image/png" };

// Robôs de busca e de leitura das IAs, liberados pelo nome no robots.txt.
export const robosDeIa = [
  "GPTBot",
  "OAI-SearchBot",
  "ChatGPT-User",
  "ClaudeBot",
  "Claude-User",
  "Claude-SearchBot",
  "PerplexityBot",
  "Perplexity-User",
  "Google-Extended",
];

// Descrição padrão do site (metadata e schema.org).
export const descricaoSite = "Mapa astral calculado com efemérides suíças dentro do seu assistente de IA.";
