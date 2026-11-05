import { planeta, signos } from "@/lib/glifos";

export function Carta() {
  return (
    <section aria-labelledby="carta-titulo" className="mx-auto max-w-[72rem] px-6">
      <div className="border-t border-border py-24">
        <p aria-hidden="true" className="glifo flex flex-wrap gap-x-4 font-mono text-sm tracking-[0.3em] text-muted-fg">
          {signos.join(" ")}
        </p>
        <h2 id="carta-titulo" className="sr-only">
          um recado meu
        </h2>
        <div className="relative mt-12 max-w-[40rem] md:ml-[8.333%]">
          <span aria-hidden="true" className="glifo absolute -left-10 top-1 hidden text-2xl text-honey md:block">
            {planeta.lua}
          </span>
          <div className="space-y-6 font-display text-2xl leading-[1.5] md:text-[28px]">
            <p>
              eu adoro conversar com a ia sobre meu mapa astral e também de amigos e família. como as ias são boas
              para gerar textos mas péssimas pra calcular os mapas, criei essa ferramenta para dar mais poder de
              análise para as ias.
            </p>
            <p>acho bizarro como é preciso.</p>
            <p>espero que você aproveite, se divirta e reflita muito com esse sisteminha que criei.</p>
          </div>
          <p className="mt-10 font-display text-2xl italic text-muted-fg md:text-[28px]">
            um abraço,
            <br />
            <span className="text-fg">gustavo.</span>
          </p>
        </div>
      </div>
    </section>
  );
}
