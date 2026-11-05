import type { Metadata } from "next";
import { Suspense } from "react";
import { Carta } from "@/components/carta";
import { Comparacao } from "@/components/comparacao";
import { Ferramentas } from "@/components/ferramentas";
import { Hero } from "@/components/hero";
import { JsonLd } from "@/components/json-ld";
import { Planos } from "@/components/planos";
import { Plataformas, PlataformasGrade } from "@/components/plataformas";
import { Profissionais } from "@/components/profissionais";
import { Prova } from "@/components/prova";
import { Secao } from "@/components/secao";
import { planeta } from "@/lib/glifos";

// A descrição continua a do layout.
export const metadata: Metadata = {
  title: { absolute: "Céu Natal: mapa astral calculado dentro do seu chat" },
};

export default function Home() {
  return (
    <>
      <JsonLd />
      <Hero />
      <Carta />
      <Prova />
      <Comparacao />
      <Secao id="conectar" titulo="como conectar" simbolo={planeta.jupiter}>
        {/* Sem JavaScript, cada cartão é um link para o guia completo. */}
        <Suspense fallback={<PlataformasGrade inicial={null} />}>
          <Plataformas />
        </Suspense>
      </Secao>
      <Ferramentas />
      <Planos />
      <Profissionais />
    </>
  );
}
