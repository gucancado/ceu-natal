import { AnelZodiacal } from "@/components/anel-zodiacal";
import { RotadorPrompts } from "@/components/rotador-prompts";
import { site } from "@/lib/site";

export function Hero() {
  return (
    <section aria-labelledby="hero-titulo" className="mx-auto max-w-[72rem] overflow-x-clip px-6">
      {/* Ocupa a tela abaixo do cabeçalho (5rem), para a seção seguinte começar na segunda dobra. */}
      <div className="grid min-h-[calc(100svh-5rem)] content-center items-center gap-12 py-12 md:py-20 lg:grid-cols-12 lg:gap-12">
        <div className="lg:col-span-6">
          <h1
            id="hero-titulo"
            className="font-display text-[30px] font-medium leading-[1.15] tracking-tight md:text-[40px]"
          >
            conecte sua IA favorita e faça análises astrológicas muito mais precisas.
          </h1>
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
