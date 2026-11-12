"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { logos } from "@/content/logos";
import { homeDo } from "@/lib/idioma";
import { site } from "@/lib/site";

const foco = "rounded-sm focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring";

// Na home em inglês o logo volta para /en e o seletor leva para o português; no resto, o contrário.
export function Cabecalho() {
  const en = usePathname() === homeDo.en;
  return (
    <header className="mx-auto max-w-[72rem] px-6">
      <div className="flex items-center justify-between gap-x-8 py-6">
        <Link href={en ? homeDo.en : homeDo.pt} className={`${foco} font-display text-2xl font-medium`}>
          Céu<span className="text-[#FFAA5A]">Natal</span>
        </Link>
        <div className="flex items-center gap-5">
          <Link
            href={en ? homeDo.pt : homeDo.en}
            hrefLang={en ? "pt-BR" : "en"}
            lang={en ? "pt-BR" : "en"}
            className={`${foco} font-mono text-sm text-muted-fg transition-colors hover:text-fg`}
          >
            {en ? "português" : "english"}
          </Link>
          <a href={site.repoUrl} aria-label="GitHub" className={`${foco} -m-2 p-2 text-muted-fg transition-colors hover:text-fg`}>
            <svg viewBox="0 0 24 24" aria-hidden="true" className="size-6 fill-current">
              <path d={logos.github.d} />
            </svg>
          </a>
        </div>
      </div>
    </header>
  );
}
