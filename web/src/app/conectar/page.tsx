import type { Metadata } from "next";
import Link from "next/link";
import { clientes } from "@/content/clientes";

export const metadata: Metadata = {
  title: "Como conectar",
  description: "Guias passo a passo para conectar o Céu Natal no Claude, no ChatGPT, no Gemini, no Cursor e no n8n.",
};

export default function PaginaConectar() {
  return (
    <article className="mx-auto max-w-[72rem] px-6 py-16 md:py-24">
      <h1 className="font-display text-4xl font-medium leading-[1.15] tracking-tight md:text-5xl">
        Como conectar o Céu Natal
      </h1>
      <ul className="mt-10 max-w-[36rem]">
        {clientes.map((c) => (
          <li key={c.slug} className="py-5">
            <Link
              href={`/conectar/${c.slug}`}
              className="font-display text-xl font-medium text-honey underline underline-offset-4"
            >
              {c.nome}
            </Link>
            <p className="mt-1 text-muted-fg">{c.resumo}</p>
          </li>
        ))}
      </ul>
    </article>
  );
}
