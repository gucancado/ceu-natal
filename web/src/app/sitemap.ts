import type { MetadataRoute } from "next";
import { tecnicas } from "@/content/tecnicas";
import { site } from "@/lib/site";

// Home e /en se apontam como versões de idioma uma da outra (hreflang).
export default function sitemap(): MetadataRoute.Sitemap {
  const idiomas = { languages: { "pt-BR": site.url, en: `${site.url}/en` } };
  const paginas = ["/mapa", ...tecnicas.map((t) => `/${t.slug}`), "/privacidade", "/termos"];
  return [
    { url: site.url, alternates: idiomas, priority: 1 },
    { url: `${site.url}/en`, alternates: idiomas, priority: 0.8 },
    ...paginas.map((p) => ({ url: `${site.url}${p}`, priority: p === "/privacidade" || p === "/termos" ? 0.3 : 0.8 })),
  ];
}
