import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  output: "standalone",
  // HSTS: o navegador passa a abrir sempre em https, sem o "não seguro" do http.
  async headers() {
    return [
      {
        source: "/:path*",
        headers: [{ key: "Strict-Transport-Security", value: "max-age=31536000; includeSubDomains" }],
      },
    ];
  },
  // As páginas legais leem o Markdown em runtime; o standalone precisa levar os arquivos.
  outputFileTracingIncludes: {
    "/privacidade": ["./src/content/legal/**/*"],
    "/termos": ["./src/content/legal/**/*"],
    "/llms-full.txt": ["./src/content/legal/**/*"],
  },
};

export default nextConfig;
