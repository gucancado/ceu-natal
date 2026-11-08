import { gerarLlmsTxt } from "@/lib/llms";

// Pré-renderizado no build: nenhuma leitura de arquivo em runtime.
export const dynamic = "force-static";

export function GET() {
  return new Response(gerarLlmsTxt(), {
    headers: {
      "Content-Type": "text/plain; charset=utf-8",
      "Cache-Control": "public, max-age=3600",
    },
  });
}
