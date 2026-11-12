import type { Metadata } from "next";
import Link from "next/link";
import { BlocoCodigo } from "@/components/bloco-codigo";
import { jsonLdScript } from "@/components/json-ld";
import { buttonVariants } from "@/components/ui/button";
import { site } from "@/lib/site";

// Página em inglês para quem chega pelos diretórios de MCP. O site continua em português; esta página
// resume o essencial e aponta para a home (hreflang nos dois sentidos).
const titulo = "Free astrology MCP server with the Swiss Ephemeris";
const descricao =
  "Céu Natal is a free, open-source MCP server that calculates natal charts, synastry, transits, progressions and solar and lunar returns with the Swiss Ephemeris. No login, no API key.";

export const metadata: Metadata = {
  title: { absolute: `${titulo} | ${site.nome}` },
  description: descricao,
  alternates: { canonical: "/en", languages: { "pt-BR": "/", en: "/en", "x-default": "/" } },
  openGraph: {
    title: titulo,
    description: descricao,
    type: "website",
    locale: "en_US",
    siteName: site.nome,
    url: "/en",
    images: ["/opengraph-image"],
  },
  twitter: { card: "summary_large_image", title: titulo, description: descricao, images: ["/opengraph-image"] },
};

const ferramentas = [
  ["calcular_mapa_natal", "natal chart: 10 planets, nodes, Chiron, angles, 12 houses and aspects"],
  ["calcular_sinastria", "synastry: cross aspects between two charts and house overlays"],
  ["calcular_mapa_composto", "composite chart by midpoints"],
  ["calcular_transitos", "transits for any date over the natal chart, slow planets highlighted"],
  ["calcular_progressoes", "secondary progressions (a day for a year), progressed Moon and Sun"],
  ["calcular_revolucao_solar", "solar return for a year, cast for the place where you spend the birthday"],
  ["calcular_revolucao_lunar", "next lunar return from a given date"],
  ["listar_aspectos_tipos", "the 8 aspects used, with angle and orb"],
] as const;

const exemplos = [
  "Calculate my natal chart: born 12/03/1990 at 14:30 in Lisbon, Portugal.",
  "Which transits are hitting my chart today?",
  "Compare my chart with my partner's (25/07/1992, 09:15, New York) and tell me where we clash.",
  "Cast my 2027 solar return for Tokyo.",
];

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
  author: { "@type": "Person", name: "Gustavo Cançado", url: site.autorUrl },
};

const h2 = "font-display text-2xl font-normal italic";
const link = "text-honey underline underline-offset-4";

export default function PaginaIngles() {
  return (
    <article lang="en" className="mx-auto max-w-[72rem] px-6 py-16 md:py-24">
      {jsonLdScript(jsonLd)}
      <p className="mb-6 font-mono text-sm text-muted-fg">
        <Link href="/" hrefLang="pt-BR" className={link}>
          em português
        </Link>
      </p>
      <h1 className="max-w-[48rem] font-display text-4xl font-medium leading-[1.15] tracking-tight md:text-5xl">{titulo}</h1>
      <p className="mt-6 max-w-[40rem] text-lg leading-[1.6] text-muted-fg">
        Language models are good at talking about a chart and bad at calculating one. Céu Natal does the math with the
        Swiss Ephemeris, turns the birth city into coordinates and the historical time zone, and hands the positions to
        your assistant. Free, open source (AGPL-3.0), no account and no API key (
        <Link href="/privacidade" hrefLang="pt-BR" className={link}>
          privacy policy, in Portuguese
        </Link>
        ).
      </p>

      <section aria-labelledby="endpoint-titulo" className="mt-16 max-w-[48rem]">
        <h2 id="endpoint-titulo" className={h2}>
          server URL
        </h2>
        <p className="mt-4 text-muted-fg">Streamable HTTP, no authentication.</p>
        <div className="mt-4">
          <BlocoCodigo codigo={site.mcpEndpoint} />
        </div>
      </section>

      <section aria-labelledby="conectar-titulo" className="mt-16 max-w-[48rem]">
        <h2 id="conectar-titulo" className={h2}>
          connect
        </h2>
        <dl className="mt-6 space-y-8">
          <div>
            <dt className="font-display text-xl font-medium">Claude (web and desktop)</dt>
            <dd className="mt-2 text-muted-fg">
              <strong className="font-medium text-fg">Customize</strong> &gt;{" "}
              <strong className="font-medium text-fg">Connectors</strong> &gt;{" "}
              <strong className="font-medium text-fg">Add custom connector</strong>. Name it Céu Natal, paste the URL,
              choose <strong className="font-medium text-fg">No sign in</strong>. Then turn it on in a chat under{" "}
              <strong className="font-medium text-fg">+</strong> &gt; Connectors.
            </dd>
          </div>
          <div>
            <dt className="font-display text-xl font-medium">ChatGPT</dt>
            <dd className="mt-2 text-muted-fg">
              At chatgpt.com/plugins, <strong className="font-medium text-fg">Add custom MCP server</strong>, paste the
              URL, choose <strong className="font-medium text-fg">No authentication</strong> and{" "}
              <strong className="font-medium text-fg">Create as a plugin</strong>.
            </dd>
          </div>
          <div>
            <dt className="font-display text-xl font-medium">Claude Code</dt>
            <dd className="mt-3">
              <BlocoCodigo codigo={`claude mcp add --transport http --scope user ceu-natal ${site.mcpEndpoint}`} />
            </dd>
          </div>
          <div>
            <dt className="font-display text-xl font-medium">Cursor, VS Code and other MCP clients</dt>
            <dd className="mt-3">
              <BlocoCodigo
                codigo={JSON.stringify({ mcpServers: { "ceu-natal": { url: site.mcpEndpoint } } }, null, 2)}
              />
            </dd>
          </div>
        </dl>
      </section>

      <section aria-labelledby="tools-titulo" className="mt-16 max-w-[48rem]">
        <h2 id="tools-titulo" className={h2}>
          tools
        </h2>
        <dl className="mt-6 space-y-4">
          {ferramentas.map(([nome, desc]) => (
            <div key={nome}>
              <dt className="break-words font-mono text-sm">{nome}</dt>
              <dd className="mt-1 text-muted-fg">{desc}</dd>
            </div>
          ))}
        </dl>
        <p className="mt-6 text-muted-fg">
          Tool names and results are in Portuguese. Your assistant reads them and answers in your language. Dates go
          in as DD/MM/YYYY and any city in the world works.
        </p>
      </section>

      <section aria-labelledby="exemplos-titulo" className="mt-16 max-w-[48rem]">
        <h2 id="exemplos-titulo" className={h2}>
          try asking
        </h2>
        <div className="mt-6 space-y-4">
          {exemplos.map((e) => (
            <BlocoCodigo key={e} codigo={e} />
          ))}
        </div>
      </section>

      <div className="mt-16 flex flex-wrap gap-3">
        <a href={site.repoUrl} className={buttonVariants({ variant: "default", size: "lg" })}>
          source code on GitHub
        </a>
        <a href={`${site.url}/llms.txt`} className={buttonVariants({ variant: "outline", size: "lg" })}>
          llms.txt
        </a>
      </div>
    </article>
  );
}
