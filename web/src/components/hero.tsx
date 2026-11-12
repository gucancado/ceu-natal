import { Autor } from "@/components/autor";
import { Lua } from "@/components/lua";
import { MarcaRotativa } from "@/components/marca-rotativa";
import { RotadorPrompts } from "@/components/rotador-prompts";
import { Sol } from "@/components/sol";
import { prompts, promptsEn } from "@/content/prompts";
import type { Idioma } from "@/lib/idioma";

// Primeira dobra: só os pedidos de exemplo, com a Lua cruzando o céu no sentido contrário às estrelas.
export function Hero({ idioma = "pt" }: { idioma?: Idioma }) {
  const en = idioma === "en";
  return (
    <section aria-label={en ? "example requests" : "exemplos de pedidos"} className="relative overflow-hidden">
      {/* O Sol vem antes no DOM: fica atrás da Lua quando os dois se cruzam. */}
      <Sol className="absolute left-0 top-[3%] size-[16px] md:size-[22px]" />
      <Lua className="absolute left-0 top-[6%] size-[120px] md:size-[180px]" />
      {/* Ocupa a tela abaixo do cabeçalho (5rem), para a seção seguinte começar na segunda dobra. */}
      <div className="relative mx-auto grid min-h-[calc(100svh-5rem)] max-w-[72rem] place-items-center px-6 py-16">
        <div className="w-full max-w-[42rem]">
          <p className="mb-8 text-center text-sm text-muted-fg md:text-base">
            {en ? "free mcp for astrological calculations with" : "mcp grátis para cálculos astrológicos com"}{" "}
            <MarcaRotativa emLinha idioma={idioma} />
          </p>
          <RotadorPrompts prompts={en ? promptsEn : prompts} />
          <Autor className="mt-10" idioma={idioma} />
        </div>
      </div>
    </section>
  );
}
