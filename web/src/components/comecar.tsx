import { BlocoCodigo } from "@/components/bloco-codigo";
import { MapaProgressivo } from "@/components/mapa-progressivo";
import { MarcaRotativa } from "@/components/marca-rotativa";
import type { Idioma } from "@/lib/idioma";
import { site } from "@/lib/site";

// Segunda dobra: o título com as marcas e o mapa que se revela conforme a pessoa preenche os dados.
// Em inglês, no lugar do mapa (que sai em português) fica a URL do servidor.
export function Comecar({ idioma = "pt" }: { idioma?: Idioma }) {
  const en = idioma === "en";
  return (
    <section aria-labelledby="comecar-titulo" className="mx-auto max-w-[72rem] px-6">
      <div className="py-16 md:py-24">
        {/* Largura para "…com o chatgpt" caber na segunda linha no desktop; o "o" fica preso à marca para a
            quebra nunca cair logo antes dela. */}
        <h1 id="comecar-titulo" className="max-w-[48rem] font-display text-[24px] font-medium leading-[1.25] tracking-tight md:text-[30px]">
          {en ? (
            <>
              get accurate astrological analysis in your conversations with <MarcaRotativa emLinha idioma="en" />
            </>
          ) : (
            <>
              faça análises astrológicas precisas nas suas conversas com{" "}
              <span className="whitespace-nowrap">
                o <MarcaRotativa emLinha />
              </span>
            </>
          )}
        </h1>
        <p className="mt-5 max-w-[34rem] text-lg leading-[1.5]">
          {en ? "free, no sign-up. I'm in beta and want to test it =]" : "grátis e sem cadastro. estou em fase beta e quero testar =]"}
        </p>
        <div className="mt-12">
          {en ? (
            <div className="max-w-[48rem]">
              <p className="mb-4 text-muted-fg">server URL (Streamable HTTP, no authentication, no API key):</p>
              <BlocoCodigo codigo={site.mcpEndpoint} idioma="en" />
            </div>
          ) : (
            <MapaProgressivo />
          )}
        </div>
      </div>
    </section>
  );
}
