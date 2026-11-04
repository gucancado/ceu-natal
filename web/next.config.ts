import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  output: "standalone",
  // As páginas legais leem o Markdown em runtime; o standalone precisa levar os arquivos.
  outputFileTracingIncludes: {
    "/privacidade": ["./src/content/legal/**/*"],
    "/termos": ["./src/content/legal/**/*"],
  },
};

export default nextConfig;
