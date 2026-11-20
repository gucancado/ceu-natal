import type { NextConfig } from "next";
import { redirecionadas } from "./src/content/landings";
import { site } from "./src/lib/site";
import { umami } from "./src/lib/umami";

// Fontes vêm do next/font (servidas pelo próprio site) e o único destino externo é o servidor MCP,
// chamado pelo formulário do /mapa, e o Umami (contagem de visitas sem cookie, no próprio servidor). 'unsafe-inline' fica por causa do runtime inline do Next e dos estilos.
const csp = [
  "default-src 'self'",
  // O next dev avalia código com eval (Fast Refresh); em produção isso não existe.
  `script-src 'self' 'unsafe-inline' ${umami.origem}${process.env.NODE_ENV !== "production" ? " 'unsafe-eval'" : ""}`,
  "style-src 'self' 'unsafe-inline'",
  "img-src 'self' data:",
  "font-src 'self'",
  `connect-src 'self' ${site.mcpUrl} ${umami.origem}`,
  "frame-ancestors 'none'",
  "object-src 'none'",
  "base-uri 'self'",
  "form-action 'self'",
].join("; ");

const nextConfig: NextConfig = {
  output: "standalone",
  poweredByHeader: false,
  // 404 único para o site todo (app/global-not-found.tsx): com um layout raiz por idioma, é o jeito de o
  // 404 sair com a moldura do site e o conteúdo já no HTML.
  experimental: { globalNotFound: true },
  // As páginas de guia (/conectar e /conectar/<ia>) saíram do ar. Links antigos, inclusive os que as IAs já
  // conhecem, caem na seção "como conectar" da home, com o guia daquela IA aberto.
  async redirects() {
    return [
      // Endereço antigo do site: tudo vai para o mesmo caminho no endereço atual. Vem antes das outras
      // regras para o visitante dar um salto só.
      // O filtro evita um laço se o site for publicado de novo num endereço antigo.
      ...site.hostsAntigos.filter((host) => host !== new URL(site.url).host).map((host) => ({
        source: "/:caminho*",
        has: [{ type: "host" as const, value: host }],
        destination: `${site.url}/:caminho*`,
        permanent: true,
      })),
      { source: "/conectar", destination: "/#conectar", permanent: true },
      { source: "/conectar/:cliente", destination: "/?cliente=:cliente#conectar", permanent: true },
      // Páginas antigas por técnica que viraram parte de uma landing por busca.
      ...redirecionadas.map((r) => ({ source: r.de, destination: r.para, permanent: true })),
    ];
  },
  async headers() {
    return [
      {
        source: "/:path*",
        headers: [
          // HSTS: o navegador passa a abrir sempre em https.
          { key: "Strict-Transport-Security", value: "max-age=31536000; includeSubDomains" },
          { key: "X-Content-Type-Options", value: "nosniff" },
          { key: "Referrer-Policy", value: "strict-origin-when-cross-origin" },
          { key: "Content-Security-Policy", value: csp },
        ],
      },
    ];
  },
};

export default nextConfig;
