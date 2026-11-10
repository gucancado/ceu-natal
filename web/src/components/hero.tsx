import Link from "next/link";
import { buttonVariants } from "@/components/ui/button";
import { Copiar } from "@/components/copiar";
import { AnelZodiacal } from "@/components/anel-zodiacal";
import { RotadorPrompts } from "@/components/rotador-prompts";
import { promptSetup } from "@/content/setup";
import { site } from "@/lib/site";

export function Hero() {
  return (
    <section aria-labelledby="hero-titulo" className="mx-auto max-w-[72rem] overflow-x-clip px-6">
      <div className="grid items-center gap-12 py-12 md:py-20 lg:grid-cols-12 lg:gap-12">
        <div className="lg:col-span-6">
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
            <Copiar texto={promptSetup} rotulo="Copiar prompt para começar" copiado="Copiado. Cole na sua IA" variant="outline" size="lg" />
            <Link href="/mapa" className={buttonVariants({ size: "lg", variant: "outline" })}>
              Fazer meu mapa astral grátis
            </Link>
          </div>
          <p className="mt-6 text-muted-fg">
            autor:{" "}
            <a
              href={site.autorUrl}
              className="rounded-sm underline underline-offset-4 transition-colors hover:text-fg focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
            >
              gustavo cançado
            </a>
          </p>
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
