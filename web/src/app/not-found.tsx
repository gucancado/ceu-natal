import type { Metadata } from "next";
import Link from "next/link";

export const metadata: Metadata = {
  title: "Página não encontrada",
};

export default function NaoEncontrada() {
  return (
    <article className="mx-auto max-w-[72rem] px-6 py-16 md:py-24">
      <h1 className="font-display text-4xl font-medium leading-[1.15] tracking-tight md:text-5xl">
        Página não encontrada
      </h1>
      <p className="mt-6 max-w-[36rem] text-muted-fg">
        O endereço que você abriu não existe ou mudou de lugar.
      </p>
      <ul className="mt-8 flex flex-wrap gap-6">
        <li>
          <Link href="/" className="text-honey underline underline-offset-4">
            Voltar ao início
          </Link>
        </li>
        <li>
          <Link href="/#conectar" className="text-honey underline underline-offset-4">
            Ver como conectar
          </Link>
        </li>
      </ul>
    </article>
  );
}
