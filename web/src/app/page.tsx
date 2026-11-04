import { Suspense } from "react";
import { Faq } from "@/components/faq";
import { Ferramentas } from "@/components/ferramentas";
import { Guias, GuiasAbas } from "@/components/guias";
import { Hero } from "@/components/hero";
import { JsonLd } from "@/components/json-ld";
import { Passos } from "@/components/passos";
import { Planos } from "@/components/planos";
import { Profissionais } from "@/components/profissionais";
import { Prompts } from "@/components/prompts";
import { Prova } from "@/components/prova";
import { Secao } from "@/components/secao";

export default function Home() {
  return (
    <>
      <JsonLd />
      <Hero />
      <Prova />
      <Passos />
      <Secao id="conectar" titulo="Conectar">
        {/* O fallback já é o conteúdo completo: o HTML estático traz os guias mesmo sem JavaScript. */}
        <Suspense fallback={<GuiasAbas />}>
          <Guias />
        </Suspense>
      </Secao>
      <Ferramentas />
      <Prompts />
      <Planos />
      <Profissionais />
      <Faq />
    </>
  );
}
