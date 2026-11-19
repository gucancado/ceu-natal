import type { MetadataRoute } from "next";
import { landings } from "@/content/landings";
import { site } from "@/lib/site";

// Home e /en se apontam como versões de idioma uma da outra (hreflang). O sitemap é gerado no build, então
// a data de modificação é a da publicação. Os llms.txt entram para os robôs das IAs acharem.
export default function sitemap(): MetadataRoute.Sitemap {
  const idiomas = { languages: { "pt-BR": site.url, en: `${site.url}/en`, "x-default": site.url } };
  const paginas = ["/mapa", ...landings.map((l) => `/${l.slug}`), "/privacidade", "/termos"];
  const lastModified = new Date();
  return [
    { url: site.url, alternates: idiomas, priority: 1, lastModified },
    { url: `${site.url}/en`, alternates: idiomas, priority: 0.8, lastModified },
    ...paginas.map((p) => ({
      url: `${site.url}${p}`,
      priority: p === "/privacidade" || p === "/termos" ? 0.3 : 0.8,
      lastModified,
    })),
    { url: `${site.url}/llms.txt`, priority: 0.5, lastModified },
    { url: `${site.url}/llms-full.txt`, priority: 0.5, lastModified },
    { url: `${site.url}/en/llms.txt`, priority: 0.5, lastModified },
  ];
}
