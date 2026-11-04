import type { Metadata } from "next";
import Link from "next/link";
import { notFound } from "next/navigation";
import { GuiaCorpo } from "@/components/guia";
import { cliente, clientes } from "@/content/clientes";

type Props = { params: Promise<{ cliente: string }> };

export const dynamicParams = false;

export function generateStaticParams() {
  return clientes.map((c) => ({ cliente: c.slug }));
}

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const c = cliente((await params).cliente);
  if (!c) return {};
  return { title: `Como conectar no ${c.nome}`, description: c.resumo };
}

export default async function PaginaCliente({ params }: Props) {
  const c = cliente((await params).cliente);
  if (!c) notFound();
  return (
    <article className="mx-auto max-w-[72rem] px-6 py-16 md:py-24">
      <h1 className="font-display text-4xl font-medium leading-[1.15] tracking-tight md:text-5xl">
        Como conectar o Céu Natal no {c.nome}
      </h1>
      <div className="mt-10">
        <GuiaCorpo c={c} Titulo="h2" />
      </div>
      <div className="mt-10 max-w-[36rem]">
        <h2 className="font-display text-xl font-medium">Fontes</h2>
        <ul className="mt-3 space-y-2">
          {c.fontes.map((f) => (
            <li key={f.url}>
              <a
                href={f.url}
                target="_blank"
                rel="noopener noreferrer"
                className="text-honey underline underline-offset-4 [overflow-wrap:anywhere]"
              >
                {f.titulo}
              </a>
            </li>
          ))}
        </ul>
        <p className="mt-6 text-sm text-muted-fg">Verificado em novembro de 2026.</p>
        <Link href="/#conectar" className="mt-8 inline-block text-honey underline underline-offset-4">
          Voltar para todos os guias
        </Link>
      </div>
    </article>
  );
}
