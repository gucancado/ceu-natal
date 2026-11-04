import type { MetadataRoute } from "next";
import { clientes } from "@/content/clientes";
import { site } from "@/lib/site";

export default function sitemap(): MetadataRoute.Sitemap {
  const caminhos = ["/", "/conectar", ...clientes.map((c) => `/conectar/${c.slug}`), "/privacidade", "/termos"];
  return caminhos.map((p) => ({ url: p === "/" ? `${site.url}/` : `${site.url}${p}` }));
}
