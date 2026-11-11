// Foto da Lua de agora, servida pelo próprio site (a CSP só libera imagens de 'self').
import { luaDaHora } from "@/lib/lua-nasa";

export const dynamic = "force-dynamic";

export async function GET() {
  const lua = await luaDaHora();
  if (!lua) return new Response("Lua indisponível.", { status: 503, headers: { "Cache-Control": "no-store" } });
  return new Response(lua.imagem, {
    headers: {
      "Content-Type": "image/jpeg",
      // 10 minutos no navegador: a fase muda devagar, e a hora seguinte traz a foto nova.
      "Cache-Control": "public, max-age=600",
      "X-Fase-Lua": `${lua.fase.toFixed(1)}% iluminada, ${lua.idade.toFixed(1)} dias`,
    },
  });
}
