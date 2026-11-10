import Link from "next/link";
import { site } from "@/lib/site";

const linkRodape =
  "rounded-sm text-muted-fg underline-offset-4 transition-colors hover:text-fg hover:underline focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring";

const paginas = [
  { href: "/privacidade", rotulo: "Privacidade" },
  { href: "/termos", rotulo: "Termos" },
  { href: "/status", rotulo: "Status" },
];

export function Rodape() {
  return (
    <footer className="mx-auto max-w-[72rem] px-6">
      <div className="flex flex-col gap-6 border-t border-border py-12 md:flex-row md:items-start md:justify-between">
        <nav aria-label="Rodapé">
          <ul className="flex flex-wrap gap-x-6 gap-y-2">
            {paginas.map((p) => (
              <li key={p.href}>
                <Link href={p.href} className={linkRodape}>
                  {p.rotulo}
                </Link>
              </li>
            ))}
            <li>
              <a href={site.repoUrl} className={linkRodape}>
                GitHub
              </a>
            </li>
          </ul>
        </nav>
      </div>
    </footer>
  );
}
