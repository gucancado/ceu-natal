import { site } from "@/lib/site";

// Ícones de traço, os mesmos de gustavocancado.com.br.
const perfis = [
  {
    rotulo: "Instagram",
    url: "https://www.instagram.com/gucancado/",
    icone: (
      <>
        <rect x="3" y="3" width="18" height="18" rx="5" />
        <circle cx="12" cy="12" r="4" />
        <circle cx="17.3" cy="6.7" r=".6" fill="currentColor" stroke="none" />
      </>
    ),
  },
  {
    rotulo: "LinkedIn",
    url: "https://www.linkedin.com/in/gustavocancado/",
    icone: (
      <>
        <rect x="3" y="3" width="18" height="18" rx="3" />
        <path d="M8 10.5V16M8 7.6v.1M11.5 16v-5.5M11.5 13c0-1.6 1-2.6 2.3-2.6s2.2.9 2.2 2.6V16" strokeLinecap="round" />
      </>
    ),
  },
  {
    rotulo: "GitHub",
    url: "https://github.com/gucancado",
    icone: (
      <path
        d="M9 19c-4.3 1.4-4.3-2.5-6-3m12 5v-3.5c0-1 .1-1.4-.5-2 2.8-.3 5.5-1.4 5.5-6a4.6 4.6 0 0 0-1.3-3.2 4.2 4.2 0 0 0-.1-3.2s-1.1-.3-3.5 1.3a12.3 12.3 0 0 0-6.2 0C6.5 2.8 5.4 3.1 5.4 3.1a4.2 4.2 0 0 0-.1 3.2A4.6 4.6 0 0 0 4 9.5c0 4.6 2.7 5.7 5.5 6-.6.6-.6 1.2-.5 2V21"
        strokeLinecap="round"
      />
    ),
  },
  {
    rotulo: "WhatsApp",
    url: "https://wa.me/5531996039118",
    icone: (
      <>
        <path d="M20.5 11.6a8.4 8.4 0 0 1-12.4 7.4L3.5 20.5l1.6-4.4a8.4 8.4 0 1 1 15.4-4.5z" />
        <path d="M9.1 8.2c-.4 2.9 2.6 6.3 5.8 6.6l1-1.3-1.7-1-.9.7c-1-.5-1.8-1.3-2.3-2.3l.7-.9-1-1.7z" strokeWidth="1.3" />
      </>
    ),
  },
];

const foco = "rounded-sm focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring";

export function Autor({ className = "" }: { className?: string }) {
  return (
    <div className={`flex flex-wrap items-center justify-center gap-x-4 gap-y-2 text-muted-fg ${className}`}>
      <p>
        autor:{" "}
        <a href={site.autorUrl} className={`${foco} transition-colors hover:text-fg`}>
          gustavo cançado
        </a>
      </p>
      <nav aria-label="Perfis do autor" className="flex items-center gap-3">
        {perfis.map((p) => (
          <a
            key={p.rotulo}
            href={p.url}
            target="_blank"
            rel="noopener"
            aria-label={p.rotulo}
            className={`${foco} -m-1 p-1 transition-colors hover:text-fg`}
          >
            <svg
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="1.6"
              strokeLinejoin="round"
              aria-hidden="true"
              className="size-[18px]"
            >
              {p.icone}
            </svg>
          </a>
        ))}
      </nav>
    </div>
  );
}
