import type { NextConfig } from "next";
import { site } from "./src/lib/site";

// Fontes vêm do next/font (servidas pelo próprio site) e o único destino externo é o servidor MCP,
// chamado pelo formulário do /mapa. 'unsafe-inline' fica por causa do runtime inline do Next e dos estilos.
const csp = [
  "default-src 'self'",
  // O next dev avalia código com eval (Fast Refresh); em produção isso não existe.
  `script-src 'self' 'unsafe-inline'${process.env.NODE_ENV !== "production" ? " 'unsafe-eval'" : ""}`,
  "style-src 'self' 'unsafe-inline'",
  "img-src 'self' data:",
  "font-src 'self'",
  `connect-src 'self' ${site.mcpUrl}`,
  "frame-ancestors 'none'",
].join("; ");

const nextConfig: NextConfig = {
  output: "standalone",
  poweredByHeader: false,
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
