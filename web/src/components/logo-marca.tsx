import { logos, type Logo } from "@/content/logos";

// Logo monocromático na cor do texto. O do Manus é marcação SVG estática do repositório (content/logo-manus.ts).
export function LogoMarca({ logo, className = "size-7" }: { logo: Logo; className?: string }) {
  const l = logos[logo];
  if ("svg" in l)
    return <svg viewBox="0 0 24 24" aria-hidden="true" className={`shrink-0 ${className}`} dangerouslySetInnerHTML={{ __html: l.svg }} />;
  return (
    <svg viewBox="0 0 24 24" aria-hidden="true" className={`shrink-0 fill-current ${className}`}>
      <path d={l.d} />
    </svg>
  );
}
