import type { Metadata } from "next";
import { Suspense } from "react";
import { Carta } from "@/components/carta";
import { Comparacao } from "@/components/comparacao";
import { Ferramentas } from "@/components/ferramentas";
import { Hero } from "@/components/hero";
import { JsonLd } from "@/components/json-ld";
import { Plataformas, PlataformasGrade } from "@/components/plataformas";
import { Profissionais } from "@/components/profissionais";
import { Secao } from "@/components/secao";
import { planeta } from "@/lib/glifos";
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
      <Carta />
      <Comparacao />
      <Secao id="conectar" titulo="como conectar" simbolo={planeta.jupiter}>
        {/* Sem JavaScript, cada cartão é um link para o guia completo. */}
        <Suspense fallback={<PlataformasGrade inicial={null} />}>
          <Plataformas />
        </Suspense>
      </Secao>
      <Ferramentas />
      <Profissionais />
    </>
  );
}
