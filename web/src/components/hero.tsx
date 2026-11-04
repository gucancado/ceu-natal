import Link from "next/link";
import { Button } from "@beeads/ui";
import { CaixaPrompt } from "@/components/caixa-prompt";
import { TabelaEfemeride } from "@/components/tabela-efemeride";
import { promptSetup } from "@/content/setup";

export function Hero() {
  return (
    <section aria-labelledby="hero-titulo" className="mx-auto max-w-[72rem] px-6">
      <div className="grid gap-16 py-12 md:py-20 lg:grid-cols-12 lg:gap-12">
        <div className="lg:col-span-7">
          <h1
            id="hero-titulo"
            className="font-display text-[40px] font-medium leading-[1.1] tracking-tight md:text-[48px]"
          >
            Mapa astral calculado, não inventado, no seu assistente de IA.
          </h1>
          <p className="mt-5 max-w-[36rem] text-lg leading-[1.5]">
            Cole este prompt no Claude, no ChatGPT, no Gemini ou no Cursor. O próprio assistente guia a conexão. Grátis,
            sem cadastro.
          </p>
          <div className="mt-6">
            <CaixaPrompt texto={promptSetup} rotulo="prompt de conexão" />
          </div>
          <div className="mt-6 flex flex-wrap gap-3">
            <Button asChild size="lg">
              <Link href="/mapa">Fazer meu mapa agora</Link>
            </Button>
            <Button asChild size="lg" variant="outline">
              <a href="#conectar">Conectar passo a passo</a>
            </Button>
          </div>
        </div>
        <div className="lg:col-span-5">
          <TabelaEfemeride />
        </div>
      </div>
    </section>
  );
}
