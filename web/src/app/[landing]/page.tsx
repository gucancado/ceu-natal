import type { Metadata } from "next";
import { notFound } from "next/navigation";
import { Suspense } from "react";
import { CaixaPrompt } from "@/components/caixa-prompt";
import { ComecarMoldura } from "@/components/comecar";
import { FormTema } from "@/components/form-tema";
import { Hero } from "@/components/hero";
import { jsonLdScript } from "@/components/json-ld";
import { Plataformas, PlataformasGrade } from "@/components/plataformas";
import { Secao } from "@/components/secao";
import { landing, landings } from "@/content/landings";
import { tecnicaDa, type Tecnica } from "@/content/tecnicas";
import { site } from "@/lib/site";

// Landing por intenção de busca, com o layout da home. Só as de content/landings.ts; qualquer outro
// caminho de um segmento dá 404.
export const dynamicParams = false;

export function generateStaticParams() {
  return landings.map((l) => ({ landing: l.slug }));
}

type Props = { params: Promise<{ landing: string }> };

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const l = landing((await params).landing);
  if (!l) return {};
  const url = `/${l.slug}`;
  return {
    title: { absolute: `${l.titulo} | ${site.nome}` },
    description: l.descricao,
    // Campo a campo: o Next não mescla `openGraph` com o do layout.
    openGraph: {
      title: l.titulo,
      description: l.descricao,
      type: "website",
      locale: "pt_BR",
      siteName: site.nome,
      url,
      images: ["/opengraph-image"],
    },
    twitter: { card: "summary_large_image", title: l.titulo, description: l.descricao, images: ["/opengraph-image"] },
  };
}

function BlocoTecnica({ t }: { t: Tecnica }) {
  return (
    <div>
      <h3 className="font-display text-2xl font-medium">{t.nome}</h3>
      <p className="mt-3 max-w-[40rem] text-muted-fg">{t.intro}</p>
      <div className="mt-6 grid gap-8 md:grid-cols-2">
        <div>
          <h4 className="font-display text-lg font-medium italic">o que é calculado</h4>
          <ul className="mt-3 list-disc space-y-1 pl-6 marker:text-honey">
            {t.calcula.map((c) => (
              <li key={c}>{c}</li>
            ))}
          </ul>
        </div>
        <div>
          <h4 className="font-display text-lg font-medium italic">o que você precisa</h4>
          <ul className="mt-3 list-disc space-y-1 pl-6 marker:text-honey">
            {t.precisa.map((c) => (
              <li key={c}>{c}</li>
            ))}
          </ul>
        </div>
      </div>
      <h4 className="mt-8 font-display text-lg font-medium italic">o que pedir para a ia</h4>
      <div className="mt-3 space-y-3">
        {t.pedidos.map((p) => (
          <CaixaPrompt key={p} texto={p} rotulo="pedido" />
        ))}
      </div>
    </div>
  );
}

export default async function PaginaLanding({ params }: Props) {
  const l = landing((await params).landing);
  if (!l) notFound();
  const tecnicas = l.tools.map(tecnicaDa).filter((t): t is Tecnica => t !== undefined);
  const perguntas = tecnicas.flatMap((t) => t.perguntas);
  const base = `/${l.slug}`;

  const jsonLd = [
    {
      "@context": "https://schema.org",
      "@type": "WebPage",
      name: l.titulo,
      description: l.descricao,
      url: `${site.url}${base}`,
      inLanguage: "pt-BR",
      isPartOf: { "@type": "WebSite", name: site.nome, url: site.url },
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

  return (
    <>
      {jsonLdScript(jsonLd)}
      <Hero chamada={l.chamada} prompts={l.prompts} comoH1 />
      <ComecarMoldura comoH2 titulo={l.titulo2} texto={l.intro}>
        <FormTema tema={l.tema} />
      </ComecarMoldura>
      <Secao id="conectar" titulo="como conectar">
        {/* Sem JavaScript, cada cartão é um link para esta mesma página com o guia aberto. */}
        <Suspense fallback={<PlataformasGrade inicial={null} base={base} />}>
          <Plataformas base={base} />
        </Suspense>
      </Secao>
      <Secao id="calculo" titulo="o que o céu natal calcula">
        <div className="space-y-16">
          {tecnicas.map((t) => (
            <BlocoTecnica key={t.tool} t={t} />
          ))}
        </div>
      </Secao>
      {perguntas.length > 0 ? (
        <Secao id="perguntas" titulo="perguntas frequentes">
          <dl className="max-w-[44rem] space-y-8">
            {perguntas.map((q) => (
              <div key={q.p}>
                <dt className="font-display text-xl font-medium">{q.p}</dt>
                <dd className="mt-2 text-muted-fg">{q.r}</dd>
              </div>
            ))}
          </dl>
        </Secao>
      ) : null}
    </>
  );
}
