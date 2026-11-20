import type { Metadata } from "next";
import { Suspense } from "react";
import { Comecar } from "@/components/comecar";
import { Ferramentas } from "@/components/ferramentas";
import { Hero } from "@/components/hero";
import { extrasApp, jsonLdScript } from "@/components/json-ld";
import { Plataformas, PlataformasGrade } from "@/components/plataformas";
import { Secao } from "@/components/secao";
import { versaoServidor } from "@/lib/saude";
import { alternativaLlmsEn, imagemOg, site } from "@/lib/site";

// A home em inglês: o mesmo layout e os mesmos componentes da home em português, com os textos traduzidos.
// O mapa pelo formulário fica só em português (o resultado sai em português). hreflang nos dois sentidos.
// O <html lang="en"> vem do layout raiz deste grupo.
const titulo = "Free astrology MCP server with the Swiss Ephemeris";
const descricao =
  "Céu Natal is a free, open-source MCP server that calculates natal charts, synastry, transits, progressions and solar and lunar returns with the Swiss Ephemeris. No login, no API key.";

export const metadata: Metadata = {
  title: { absolute: `${titulo} | ${site.nome}` },
  description: descricao,
  alternates: { canonical: "/en", languages: { "pt-BR": "/", en: "/en", "x-default": "/" }, types: alternativaLlmsEn },
  openGraph: {
    title: titulo,
    description: descricao,
    type: "website",
    locale: "en_US",
    siteName: site.nome,
    url: "/en",
    images: [imagemOg],
  },
  twitter: { card: "summary_large_image", title: titulo, description: descricao, images: [imagemOg] },
};

const jsonLd = {
  "@context": "https://schema.org",
  "@type": "SoftwareApplication",
  name: site.nome,
  alternateName: "Ceu Natal astrology MCP server",
  description: descricao,
  url: `${site.url}/en`,
  applicationCategory: "LifestyleApplication",
  operatingSystem: "Any (remote MCP server)",
  inLanguage: ["en", "pt-BR"],
  isAccessibleForFree: true,
  offers: { "@type": "Offer", price: "0", priceCurrency: "USD" },
  license: "https://www.gnu.org/licenses/agpl-3.0.html",
  sameAs: [site.repoUrl],
  author: { "@type": "Person", name: site.autor, url: site.autorUrl, sameAs: [...site.autorPerfis] },
};

export default async function HomeIngles() {
  const extras = extrasApp(await versaoServidor(site.mcpUrl));
  return (
    <>
      {jsonLdScript({ ...jsonLd, ...extras })}
      <Hero idioma="en" />
      <Comecar idioma="en" />
      <Secao id="conectar" titulo="how to connect">
        <Suspense fallback={<PlataformasGrade inicial={null} idioma="en" />}>
          <Plataformas idioma="en" />
        </Suspense>
      </Secao>
      <Ferramentas idioma="en" />
    </>
  );
}
