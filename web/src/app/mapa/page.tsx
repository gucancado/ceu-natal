import type { Metadata } from "next";
import Link from "next/link";
import { FormMapa } from "@/components/form-mapa";

export const metadata: Metadata = {
  title: "Mapa natal grátis",
  description: "Calcule seu mapa natal em segundos, sem cadastro, e cole no seu assistente de IA.",
};

export default function PaginaMapa() {
  return (
    <article className="mx-auto max-w-[72rem] px-6 py-16 md:py-24">
      <h1 className="font-display text-4xl font-medium leading-[1.15] tracking-tight md:text-5xl">
        Seu mapa natal, sem cadastro
      </h1>
      <p className="mt-6 max-w-[36rem] text-lg leading-[1.6] text-muted-fg">
        Só as posições calculadas, sem interpretação. Você copia e cola no Claude, no ChatGPT ou no Gemini, e ele lê o
        mapa a partir delas. Os dados são usados só para o cálculo e não ficam guardados (
        <Link href="/privacidade" className="text-honey underline underline-offset-4">
          privacidade
        </Link>
        ).
      </p>
      <div className="mt-12">
        <FormMapa />
      </div>
    </article>
  );
}
