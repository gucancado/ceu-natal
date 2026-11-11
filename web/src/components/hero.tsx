import { Autor } from "@/components/autor";
import { Lua } from "@/components/lua";
import { MarcaRotativa } from "@/components/marca-rotativa";
import { RotadorPrompts } from "@/components/rotador-prompts";
import { Sol } from "@/components/sol";

// Primeira dobra: só os pedidos de exemplo, com a Lua cruzando o céu no sentido contrário às estrelas.
export function Hero() {
  return (
    // Sem `isolate`: o mix-blend-mode da Lua precisa misturar com o céu da página, não com um grupo vazio.
    <section aria-label="exemplos de pedidos" className="relative overflow-hidden">
      {/* O Sol vem antes no DOM: fica atrás da Lua quando os dois se cruzam. */}
      <Sol className="absolute left-0 top-[3%] size-[56px] md:size-[84px]" />
      <Lua className="absolute left-0 top-[6%] size-[120px] md:size-[180px]" />
      {/* Ocupa a tela abaixo do cabeçalho (5rem), para a seção seguinte começar na segunda dobra. */}
      <div className="relative mx-auto grid min-h-[calc(100svh-5rem)] max-w-[72rem] place-items-center px-6 py-16">
        <div className="w-full max-w-[42rem]">
          <p className="mb-8 text-center text-sm text-muted-fg md:text-base">
            mcp grátis para cálculos astrológicos com <MarcaRotativa emLinha />
          </p>
          <RotadorPrompts />
          <Autor className="mt-10" />
        </div>
      </div>
    </section>
  );
}
