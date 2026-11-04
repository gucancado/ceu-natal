import { descricaoSite, site } from "@/lib/site";

const dados = {
  "@context": "https://schema.org",
  "@type": "SoftwareApplication",
  name: site.nome,
  description: descricaoSite,
  applicationCategory: "UtilitiesApplication",
  operatingSystem: "Web",
  offers: { "@type": "Offer", price: "0", priceCurrency: "BRL" },
  url: site.url,
  softwareHelp: `${site.url}/conectar`,
  license: "https://www.gnu.org/licenses/agpl-3.0.html",
  inLanguage: "pt-BR",
};

// Schema.org da home. "<" escapado para nunca fechar o <script> por acidente.
export function JsonLd() {
  const json = JSON.stringify(dados).replace(/</g, "\\u003c");
  return <script type="application/ld+json" dangerouslySetInnerHTML={{ __html: json }} />;
}
