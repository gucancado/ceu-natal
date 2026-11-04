import { Faq } from "@/components/faq";
import { Ferramentas } from "@/components/ferramentas";
import { Hero } from "@/components/hero";
import { Passos } from "@/components/passos";
import { Planos } from "@/components/planos";
import { Profissionais } from "@/components/profissionais";
import { Prompts } from "@/components/prompts";
import { Prova } from "@/components/prova";
import { Secao } from "@/components/secao";

export default function Home() {
  return (
    <>
      <Hero />
      <Prova />
      <Passos />
      <Secao id="conectar" titulo="Conectar">
        <p />
      </Secao>
      <Ferramentas />
      <Prompts />
      <Planos />
      <Profissionais />
      <Faq />
    </>
  );
}
