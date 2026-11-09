import type { ReactNode } from "react";
import { contato } from "@/lib/site";

// Sem JavaScript, o link leva à política de privacidade, que traz o contato por extenso.
export function LinkEmail({
  assunto,
  className,
  children,
}: {
  assunto?: string;
  className?: string;
  children: ReactNode;
}) {
  return (
    <a
      href="/privacidade"
      data-email-usuario={contato.usuario}
      data-email-dominio={contato.dominio}
      data-email-assunto={assunto}
      className={className}
    >
      {children}
    </a>
  );
}
