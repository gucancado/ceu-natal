import { tecnicas } from "@/content/tecnicas";
import { versaoServidor } from "@/lib/saude";
import { descricaoSite, imagemOg, site } from "@/lib/site";

// O autor, o site e o aplicativo ficam num grafo só, ligados por @id. O @id do autor é o mesmo que
// gustavocancado.com.br e o pulsobh usam, para os buscadores e as IAs juntarem tudo na mesma pessoa.
const idAutor = `${site.autorUrl}/#pessoa`;
const idSite = `${site.url}/#site`;

const dados = {
  "@context": "https://schema.org",
  "@graph": [
    {
      "@type": "WebSite",
      "@id": idSite,
      name: site.nome,
      alternateName: ["Ceu Natal", "ceunatal"],
      description: descricaoSite,
      url: site.url,
      inLanguage: ["pt-BR", "en"],
      publisher: { "@id": idAutor },
    },
    {
      "@type": "SoftwareApplication",
      "@id": `${site.url}/#app`,
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
      isPartOf: { "@id": idSite },
      sameAs: [site.repoUrl, `${site.url}/en`],
      author: { "@id": idAutor },
      featureList: tecnicas.map((t) => t.nome),
      keywords: "mapa astral, mapa natal, sinastria, trânsitos, revolução solar, astrologia, MCP, efemérides suíças",
    },
    {
      "@type": "Person",
      "@id": idAutor,
      name: site.autor,
      url: site.autorUrl,
      sameAs: [...site.autorPerfis],
    },
  ],
};

// Script schema.org. "<" vira a sequência \u003c para o texto nunca fechar o <script> por acidente.
export function jsonLdScript(dados: object) {
  const json = JSON.stringify(dados).replace(/</g, "\\u003c");
  return <script type="application/ld+json" dangerouslySetInnerHTML={{ __html: json }} />;
}

/** Versão do servidor e a imagem OG como screenshot, para o SoftwareApplication. */
export function extrasApp(versao: string | null) {
  return {
    ...(versao ? { softwareVersion: versao } : {}),
    screenshot: `${site.url}${imagemOg.url}`,
  };
}

// Schema.org da home.
export async function JsonLd() {
  const extras = extrasApp(await versaoServidor(site.mcpUrl));
  const grafo = dados["@graph"].map((no) => (no["@type"] === "SoftwareApplication" ? { ...no, ...extras } : no));
  return jsonLdScript({ ...dados, "@graph": grafo });
}
