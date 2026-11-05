import Link from "next/link";
import { Button } from "@beeads/ui";
import { Copiar } from "@/components/copiar";
import { AnelZodiacal } from "@/components/anel-zodiacal";
import { RotadorPrompts } from "@/components/rotador-prompts";
import { planeta } from "@/lib/glifos";
import { promptSetup } from "@/content/setup";

export function Hero() {
  return (
    <section aria-labelledby="hero-titulo" className="caixa-baixa mx-auto max-w-[72rem] overflow-x-clip px-6">
      <div className="grid items-center gap-12 py-12 md:py-20 lg:grid-cols-12 lg:gap-12">
        <div className="lg:col-span-6">
          <p className="mb-6 font-mono text-sm text-muted-fg">
            <span aria-hidden="true" className="glifo mr-2 text-honey">
              {planeta.lua}
            </span>
            só entre nós
          </p>
          <h1
            id="hero-titulo"
            className="font-display text-[40px] font-medium leading-[1.1] tracking-tight md:text-[48px]"
          >
            conecte sua IA favorita e faça análises astrológicas muito mais precisas.
          </h1>
          <p className="mt-5 max-w-[34rem] text-lg leading-[1.5]">
            é grátis e sem cadastro. copie o prompt, cole no claude, no chatgpt, no gemini ou no cursor, e a própria ia
            te guia na conexão.
          </p>
          <div className="mt-8 flex flex-wrap gap-3">
            <Copiar texto={promptSetup} rotulo="Copiar prompt para começar" copiado="Copiado. Cole no seu assistente" variant="default" size="lg" />
            <Button asChild size="lg" variant="outline">
              <Link href="/mapa">Fazer meu mapa astral grátis</Link>
            </Button>
          </div>
        </div>
        <div className="relative isolate lg:col-span-6">
          <AnelZodiacal className="absolute left-1/2 top-1/2 -z-10 size-[26rem] -translate-x-1/2 -translate-y-1/2 text-fg/15 md:size-[32rem]" />
          <div className="px-2 py-16 sm:px-10">
            <RotadorPrompts />
          </div>
        </div>
      </div>
    </section>
  );
}
