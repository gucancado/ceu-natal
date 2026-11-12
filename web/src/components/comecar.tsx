import type { ReactNode } from "react";
import { BlocoCodigo } from "@/components/bloco-codigo";
import { MapaProgressivo } from "@/components/mapa-progressivo";
import { MarcaRotativa } from "@/components/marca-rotativa";
import type { Idioma } from "@/lib/idioma";
import { site } from "@/lib/site";

const tituloClasse =
  "max-w-[48rem] font-display text-[24px] font-medium leading-[1.25] tracking-tight md:text-[30px]";

// Moldura da segunda dobra: título, texto curto e o conteúdo (o mapa na home, as chamadas nas landings).
// `comoH2`: nas landings o H1 é a chamada da primeira dobra.
export function ComecarMoldura({
  titulo,
  texto,
  children,
  comoH2 = false,
}: {
  titulo: ReactNode;
  texto: ReactNode;
  children: ReactNode;
  comoH2?: boolean;
}) {
  const Titulo = comoH2 ? "h2" : "h1";
  return (
    <section aria-labelledby="comecar-titulo" className="mx-auto max-w-[72rem] px-6">
      <div className="py-16 md:py-24">
        <Titulo id="comecar-titulo" className={tituloClasse}>
          {titulo}
        </Titulo>
        <p className="mt-5 max-w-[34rem] text-lg leading-[1.5]">{texto}</p>
        <div className="mt-12">{children}</div>
      </div>
    </section>
  );
}

// Segunda dobra da home: o título com as marcas e o mapa que se revela conforme a pessoa preenche os dados.
// Em inglês, no lugar do mapa (que sai em português) fica a URL do servidor.
export function Comecar({ idioma = "pt" }: { idioma?: Idioma }) {
  const en = idioma === "en";
  return (
    <ComecarMoldura
      titulo={
        en ? (
          <>
            get accurate astrological analysis in your conversations with <MarcaRotativa emLinha idioma="en" />
          </>
        ) : (
          <>
            {/* Largura para "…com o chatgpt" caber na segunda linha no desktop; o "o" fica preso à marca
                para a quebra nunca cair logo antes dela. */}
            faça análises astrológicas precisas nas suas conversas com{" "}
            <span className="whitespace-nowrap">
              o <MarcaRotativa emLinha />
            </span>
          </>
        )
      }
      texto={en ? "free, no sign-up. I'm in beta and want to test it =]" : "grátis e sem cadastro. estou em fase beta e quero testar =]"}
    >
      {en ? (
        <div className="max-w-[48rem]">
          <p className="mb-4 text-muted-fg">server URL (Streamable HTTP, no authentication, no API key):</p>
          <BlocoCodigo codigo={site.mcpEndpoint} idioma="en" />
        </div>
      ) : (
        <MapaProgressivo />
      )}
    </ComecarMoldura>
  );
}
