"use client";

import { useEffect, useState } from "react";
import { contato } from "@/lib/site";

// O endereço não vai no HTML: é montado no navegador depois de carregar, longe dos robôs de spam.
const montar = () => `${contato.usuario}@${contato.dominio}`;

export function EmailOculto({ className = "" }: { className?: string }) {
  const [email, setEmail] = useState<string | null>(null);
  useEffect(() => setEmail(montar()), []);
  return <span className={className}>{email ?? "carregando…"}</span>;
}

export function LinkEmail({ assunto, children, className = "" }: { assunto?: string; children: React.ReactNode; className?: string }) {
  function abrir(e: React.MouseEvent<HTMLAnchorElement>) {
    e.preventDefault();
    const q = assunto ? `?subject=${encodeURIComponent(assunto)}` : "";
    window.location.href = `mailto:${montar()}${q}`;
  }
  return (
    <a href="#" onClick={abrir} className={className}>
      {children}
    </a>
  );
}
