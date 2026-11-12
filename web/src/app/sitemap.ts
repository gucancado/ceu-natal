import type { MetadataRoute } from "next";
import { site } from "@/lib/site";

export default function sitemap(): MetadataRoute.Sitemap {
  const caminhos = ["/", "/mapa", "/privacidade", "/termos"];
  return caminhos.map((p) => ({ url: p === "/" ? site.url : `${site.url}${p}` }));
}
