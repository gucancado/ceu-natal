import { MapaProgressivo } from "@/components/mapa-progressivo";
import { MarcaRotativa } from "@/components/marca-rotativa";
import { site } from "@/lib/site";

// Segunda dobra: o título com as marcas e o mapa que se revela conforme a pessoa preenche os dados.
export function Comecar() {
  return (
    <section aria-labelledby="comecar-titulo" className="mx-auto max-w-[72rem] px-6">
      <div className="py-16 md:py-24">
        <h1 id="comecar-titulo" className="max-w-[48rem] font-display text-[30px] font-medium leading-[1.2] tracking-tight md:text-[40px]">
          faça análises astrológicas precisas direto nas suas conversas com o <MarcaRotativa />
        </h1>
        <p className="mt-5 max-w-[34rem] text-lg leading-[1.5]">
          grátis e sem cadastro. estou em fase beta e quero testar =]
        </p>
        <p className="mt-3 text-muted-fg">
          autor:{" "}
          <a
            href={site.autorUrl}
            className="rounded-sm underline underline-offset-4 transition-colors hover:text-fg focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
          >
            gustavo cançado
          </a>
        </p>
        <div className="mt-12">
          <MapaProgressivo />
        </div>
      </div>
    </section>
  );
}
