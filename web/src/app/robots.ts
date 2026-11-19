import type { MetadataRoute } from "next";
import { robosDeIa, site } from "@/lib/site";

// Os robôs das IAs entram pelo nome, com a mesma regra de todo mundo: quem tem grupo próprio ignora o "*".
export default function robots(): MetadataRoute.Robots {
  return {
    rules: [
      { userAgent: "*", allow: "/", disallow: "/status" },
      { userAgent: robosDeIa, allow: "/", disallow: "/status" },
    ],
    sitemap: `${site.url}/sitemap.xml`,
  };
}
