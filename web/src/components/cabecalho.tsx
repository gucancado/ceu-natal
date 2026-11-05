import Link from "next/link";
import { site } from "@/lib/site";

const foco = "rounded-sm focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring";
const linkNav = `${foco} text-muted-fg transition-colors hover:text-fg`;

const ancoras = [
  { href: "/mapa", rotulo: "Mapa astral grátis" },
  { href: "/#conectar", rotulo: "Conectar" },
  { href: "/#planos", rotulo: "Planos" },
];

export function Cabecalho() {
  return (
    <header className="mx-auto max-w-[72rem] px-6">
      <div className="flex flex-wrap items-center justify-between gap-x-8 gap-y-3 py-6">
        <Link href="/" className={`${foco} font-display text-2xl font-medium`}>
          {site.nome}
        </Link>
        <div className="flex items-center gap-4">
          <nav aria-label="Principal">
            <ul className="flex flex-wrap items-center gap-x-5 gap-y-2">
              {ancoras.map((a) => (
                <li key={a.href}>
                  <Link href={a.href} className={linkNav}>
                    {a.rotulo}
                  </Link>
                </li>
              ))}
              <li>
                <a href={site.repoUrl} rel="noopener" className={linkNav}>
                  GitHub
                </a>
              </li>
            </ul>
          </nav>
        </div>
      </div>
    </header>
  );
}
