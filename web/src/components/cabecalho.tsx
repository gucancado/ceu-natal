import Link from "next/link";
import { logos } from "@/content/logos";
import { site } from "@/lib/site";

const foco = "rounded-sm focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring";

export function Cabecalho() {
  return (
    <header className="mx-auto max-w-[72rem] px-6">
      <div className="flex items-center justify-between gap-x-8 py-6">
        <Link href="/" className={`${foco} font-display text-2xl font-medium`}>
          Céu<span className="text-[#FFAA5A]">Natal</span>
        </Link>
        <a href={site.repoUrl} aria-label="GitHub" className={`${foco} -m-2 p-2 text-muted-fg transition-colors hover:text-fg`}>
          <svg viewBox="0 0 24 24" aria-hidden="true" className="size-6 fill-current">
            <path d={logos.github.d} />
          </svg>
        </a>
      </div>
    </header>
  );
}
