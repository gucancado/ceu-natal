import type { Metadata } from "next";
import Link from "next/link";
import { FormMapa } from "@/components/form-mapa";
import { jsonLdScript } from "@/components/json-ld";
import { planeta } from "@/lib/glifos";
import { site } from "@/lib/site";

const titulo = "Mapa astral grátis e sem cadastro";
const descricao =
  "Calcule seu mapa astral completo em segundos, grátis e sem cadastro: planetas, ascendente, casas e aspectos com as efemérides suíças. Copie e cole no ChatGPT, no Claude ou no Gemini.";

export const metadata: Metadata = {
  title: { absolute: `${titulo} | ${site.nome}` },
  description: descricao,
  // Campo a campo: o Next não mescla `openGraph` com o do layout.
  openGraph: {
    title: titulo,
    description: descricao,
    type: "website",
    locale: "pt_BR",
    siteName: site.nome,
    url: "/mapa",
    images: ["/opengraph-image"],
  },
  twitter: {
    card: "summary_large_image",
    title: titulo,
    description: descricao,
    images: ["/opengraph-image"],
  },
};

const perguntas = [
  {
    p: "precisa de cadastro?",
    r: "não. você digita a data, e se souber, a hora e a cidade. o mapa sai na hora. os dados do mapa ficam guardados para melhorar o céu natal, sem nome nem conta.",
  },
  {
    p: "e se eu não souber a hora em que nasci?",
    r: "dá para calcular só com a data. você recebe os planetas, os signos e os aspectos, mas sem ascendente e sem casas, que dependem da hora.",
  },
  {
    p: "o que vem no mapa astral?",
    r: "sol, lua e planetas com signo, grau e casa, ascendente, meio do céu, nodos lunares, quíron, as cúspides das doze casas e os aspectos entre eles com o orbe.",
  },
  {
    p: "é preciso mesmo?",
    r: "o cálculo usa as efemérides suíças, a mesma base dos programas profissionais de astrologia. a cidade vira coordenada e fuso histórico antes do cálculo.",
  },
  {
    p: "posso fazer o mapa astral de outra pessoa?",
    r: "pode. é só preencher com os dados de nascimento dela. para comparar dois mapas (sinastria), conecte o céu natal na sua ia.",
  },
  {
    p: "por que colar na ia?",
    r: "porque a ia é ótima para conversar sobre o mapa e péssima para calcular. com as posições já calculadas, ela interpreta em cima de números certos.",
  },
];

const jsonLd = [
  {
    "@context": "https://schema.org",
    "@type": "WebApplication",
    name: `${titulo} · ${site.nome}`,
    url: `${site.url}/mapa`,
    description: descricao,
    applicationCategory: "LifestyleApplication",
    operatingSystem: "Web",
    inLanguage: "pt-BR",
    offers: { "@type": "Offer", price: "0", priceCurrency: "BRL" },
  },
  {
    "@context": "https://schema.org",
    "@type": "FAQPage",
    mainEntity: perguntas.map((q) => ({
      "@type": "Question",
      name: q.p,
      acceptedAnswer: { "@type": "Answer", text: q.r },
    })),
  },
];

export default function PaginaMapa() {
  return (
    <article className="mx-auto max-w-[72rem] px-6 py-16 md:py-24">
      {jsonLdScript(jsonLd)}
      <p className="mb-6 font-mono text-sm text-muted-fg">
        <span aria-hidden="true" className="glifo mr-2 text-honey">
          {planeta.sol}
        </span>
        em segundos
      </p>
      <h1 className="font-display text-4xl font-medium leading-[1.15] tracking-tight md:text-5xl">{titulo}</h1>
      <p className="mt-6 max-w-[36rem] text-lg leading-[1.6] text-muted-fg">
        eu calculo as posições, sem interpretação. você copia e cola no chatgpt, no claude ou no gemini, e a ia lê o
        seu mapa a partir delas.
      </p>
      <div className="mt-12">
        <FormMapa />
      </div>

      <section aria-labelledby="perguntas-titulo" className="mt-24 max-w-[44rem] pt-16">
        <h2 id="perguntas-titulo" className="flex items-baseline gap-4 font-display text-3xl font-normal italic">
          <span aria-hidden="true" className="glifo not-italic text-honey">
            {planeta.lua}
          </span>
          sobre o mapa astral grátis
        </h2>
        <dl className="mt-10 space-y-8">
          {perguntas.map((q) => (
            <div key={q.p}>
              <dt className="font-display text-xl font-medium">{q.p}</dt>
              <dd className="mt-2 text-muted-fg">{q.r}</dd>
            </div>
          ))}
        </dl>
        <p className="mt-12 text-lg">
          quer trânsitos, revolução solar ou sinastria?{" "}
          <Link href="/#conectar" className="text-honey underline underline-offset-4">
            conecte o céu natal na sua ia
          </Link>
          .
        </p>
      </section>
    </article>
  );
}
