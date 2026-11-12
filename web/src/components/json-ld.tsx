import { tecnicas } from "@/content/tecnicas";
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
  softwareHelp: `${site.url}/#conectar`,
  license: "https://www.gnu.org/licenses/agpl-3.0.html",
  inLanguage: "pt-BR",
  isAccessibleForFree: true,
  sameAs: [site.repoUrl, `${site.url}/en`],
  author: { "@type": "Person", name: "Gustavo Cançado", url: site.autorUrl },
  featureList: ["mapa natal", ...tecnicas.map((t) => t.nome)],
  keywords: "mapa astral, mapa natal, sinastria, trânsitos, revolução solar, astrologia, MCP, efemérides suíças",
};

// Script schema.org. "<" vira a sequência \u003c para o texto nunca fechar o <script> por acidente.
export function jsonLdScript(dados: object) {
  const json = JSON.stringify(dados).replace(/</g, "\\u003c");
  return <script type="application/ld+json" dangerouslySetInnerHTML={{ __html: json }} />;
}

// Schema.org da home.
export function JsonLd() {
  return jsonLdScript(dados);
}
