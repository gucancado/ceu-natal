import type { Metadata } from "next";
import { Suspense } from "react";
import { Comecar } from "@/components/comecar";
import { Ferramentas } from "@/components/ferramentas";
import { Hero } from "@/components/hero";
import { JsonLd } from "@/components/json-ld";
import { Plataformas, PlataformasGrade } from "@/components/plataformas";
import { Secao } from "@/components/secao";
import { tituloHome } from "@/lib/site";

// A descrição continua a do layout.
export const metadata: Metadata = {
  title: { absolute: tituloHome },
};

export default function Home() {
  return (
    <>
      <JsonLd />
      <Hero />
      <Comecar />
      <Secao id="conectar" titulo="como conectar">
        {/* Sem JavaScript, cada cartão é um link para o guia completo. */}
        <Suspense fallback={<PlataformasGrade inicial={null} />}>
          <Plataformas />
        </Suspense>
      </Secao>
      <Ferramentas />
    </>
  );
}
