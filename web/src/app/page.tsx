import { Hero } from "@/components/hero";
import { Passos } from "@/components/passos";
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
      <Secao id="ferramentas" titulo="Nove ferramentas">
        <p />
      </Secao>
      <Secao id="exemplos" titulo="Três pedidos para começar">
        <p />
      </Secao>
      <Secao id="planos" titulo="Planos">
        <p />
      </Secao>
      <Secao id="profissionais" titulo="Para quem atende">
        <p />
      </Secao>
      <Secao id="faq" titulo="Perguntas frequentes">
        <p />
      </Secao>
    </>
  );
}
