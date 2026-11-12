import type { Metadata } from "next";
import Link from "next/link";
import { notFound } from "next/navigation";
import { BlocoCodigo } from "@/components/bloco-codigo";
import { jsonLdScript } from "@/components/json-ld";
import { buttonVariants } from "@/components/ui/button";
import { tecnica, tecnicas } from "@/content/tecnicas";
import { site } from "@/lib/site";

// Só as técnicas de content/tecnicas.ts; qualquer outro caminho de um segmento dá 404.
export const dynamicParams = false;

export function generateStaticParams() {
  return tecnicas.map((t) => ({ tecnica: t.slug }));
}

type Props = { params: Promise<{ tecnica: string }> };

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const t = tecnica((await params).tecnica);
  if (!t) return {};
  const url = `/${t.slug}`;
  return {
    title: { absolute: `${t.titulo} | ${site.nome}` },
    description: t.descricao,
    // Campo a campo: o Next não mescla `openGraph` com o do layout.
    openGraph: {
      title: t.titulo,
      description: t.descricao,
      type: "article",
      locale: "pt_BR",
      siteName: site.nome,
      url,
      images: ["/opengraph-image"],
    },
    twitter: { card: "summary_large_image", title: t.titulo, description: t.descricao, images: ["/opengraph-image"] },
  };
}

const link = "text-honey underline underline-offset-4";

export default async function PaginaTecnica({ params }: Props) {
  const t = tecnica((await params).tecnica);
  if (!t) notFound();

  const jsonLd = [
    {
      "@context": "https://schema.org",
      "@type": "WebPage",
      name: t.titulo,
      description: t.descricao,
      url: `${site.url}/${t.slug}`,
      inLanguage: "pt-BR",
      isPartOf: { "@type": "WebSite", name: site.nome, url: site.url },
    },
    {
      "@context": "https://schema.org",
      "@type": "FAQPage",
      mainEntity: t.perguntas.map((q) => ({
        "@type": "Question",
        name: q.p,
        acceptedAnswer: { "@type": "Answer", text: q.r },
      })),
    },
  ];
  const outras = tecnicas.filter((o) => o.slug !== t.slug);

  return (
    <article className="mx-auto max-w-[72rem] px-6 py-16 md:py-24">
      {jsonLdScript(jsonLd)}
      <p className="mb-6 font-mono text-sm text-muted-fg">{t.chamada}</p>
      <h1 className="max-w-[48rem] font-display text-4xl font-medium leading-[1.15] tracking-tight md:text-5xl">
        {t.titulo}
      </h1>
      <p className="mt-6 max-w-[40rem] text-lg leading-[1.6] text-muted-fg">{t.intro}</p>
      <div className="mt-8 flex flex-wrap gap-3">
        <Link href="/#conectar" className={buttonVariants({ variant: "default", size: "lg" })}>
          conectar na minha ia
        </Link>
        <Link href="/mapa" className={buttonVariants({ variant: "outline", size: "lg" })}>
          só o mapa natal, sem conectar
        </Link>
      </div>

      <div className="mt-20 grid max-w-[60rem] gap-12 md:grid-cols-2">
        <section aria-labelledby="calcula-titulo">
          <h2 id="calcula-titulo" className="font-display text-2xl font-normal italic">
            o que eu calculo
          </h2>
          <ul className="mt-6 list-disc space-y-2 pl-6 marker:text-honey">
            {t.calcula.map((c) => (
              <li key={c}>{c}</li>
            ))}
          </ul>
          <p className="mt-4 font-mono text-sm text-muted-fg">tool: {t.tool}</p>
        </section>
        <section aria-labelledby="precisa-titulo">
          <h2 id="precisa-titulo" className="font-display text-2xl font-normal italic">
            o que você precisa
          </h2>
          <ul className="mt-6 list-disc space-y-2 pl-6 marker:text-honey">
            {t.precisa.map((c) => (
              <li key={c}>{c}</li>
            ))}
          </ul>
        </section>
      </div>

      <section aria-labelledby="pedidos-titulo" className="mt-20 max-w-[48rem]">
        <h2 id="pedidos-titulo" className="font-display text-2xl font-normal italic">
          o que pedir para a ia
        </h2>
        <p className="mt-4 text-muted-fg">
          com o céu natal conectado, é só escrever. troque os dados de exemplo pelos seus.
        </p>
        <div className="mt-6 space-y-4">
          {t.pedidos.map((p) => (
            <BlocoCodigo key={p} codigo={p} />
          ))}
        </div>
      </section>

      <section aria-labelledby="perguntas-titulo" className="mt-20 max-w-[44rem]">
        <h2 id="perguntas-titulo" className="font-display text-2xl font-normal italic">
          perguntas sobre {t.nome}
        </h2>
        <dl className="mt-8 space-y-8">
          {t.perguntas.map((q) => (
            <div key={q.p}>
              <dt className="font-display text-xl font-medium">{q.p}</dt>
              <dd className="mt-2 text-muted-fg">{q.r}</dd>
            </div>
          ))}
        </dl>
      </section>

      <nav aria-labelledby="outras-titulo" className="mt-20">
        <h2 id="outras-titulo" className="font-display text-2xl font-normal italic">
          outras técnicas
        </h2>
        <ul className="mt-6 flex flex-wrap gap-x-6 gap-y-2">
          {outras.map((o) => (
            <li key={o.slug}>
              <Link href={`/${o.slug}`} className={link}>
                {o.nome}
              </Link>
            </li>
          ))}
          <li>
            <Link href="/mapa" className={link}>
              mapa natal
            </Link>
          </li>
        </ul>
      </nav>
    </article>
  );
}
