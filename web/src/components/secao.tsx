import type { ReactNode } from "react";

type SecaoProps = {
  id: string;
  titulo: string;
  simbolo?: string;
  children: ReactNode;
};

export function Secao({ id, titulo, simbolo, children }: SecaoProps) {
  return (
    <section id={id} aria-labelledby={`${id}-titulo`} className="mx-auto max-w-[72rem] px-6">
      <div className="py-24">
        <h2 id={`${id}-titulo`} className="flex items-baseline gap-4 font-display text-4xl font-normal italic">
          {simbolo ? (
            <span aria-hidden="true" className="glifo not-italic text-honey">
              {simbolo}
            </span>
          ) : null}
          {titulo}
        </h2>
        <div className="mt-10">{children}</div>
      </div>
    </section>
  );
}
