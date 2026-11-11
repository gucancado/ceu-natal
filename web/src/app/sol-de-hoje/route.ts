// Foto do Sol de hoje, servida pelo próprio site (a CSP só libera imagens de 'self').
import { solDeHoje } from "@/lib/sol-nasa";

export const dynamic = "force-dynamic";

export async function GET() {
  const imagem = await solDeHoje();
  if (!imagem) return new Response("Sol indisponível.", { status: 503, headers: { "Cache-Control": "no-store" } });
  return new Response(imagem, {
    headers: { "Content-Type": "image/jpeg", "Cache-Control": "public, max-age=900" },
  });
}
