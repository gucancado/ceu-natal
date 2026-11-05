"use client";

import { useEffect, useRef, useState } from "react";
import { buttonVariants } from "@/components/ui/button";

type Props = {
  texto: string;
  rotulo?: string;
  copiado?: string;
  variant?: "default" | "outline";
  size?: "sm" | "lg";
  /** id do elemento que mostra o texto; se a cópia falhar, ele fica selecionado para copiar à mão. */
  alvoId?: string;
};

type Resultado = "nada" | "copiado" | "falhou";

// Sem a API de área de transferência (http, permissão negada): tenta o caminho antigo com um textarea temporário.
function copiarAntigo(texto: string): boolean {
  const area = document.createElement("textarea");
  area.value = texto;
  area.setAttribute("readonly", "");
  area.style.position = "fixed";
  area.style.opacity = "0";
  document.body.appendChild(area);
  area.select();
  let ok = false;
  try {
    ok = document.execCommand("copy");
  } catch {
    ok = false;
  }
  area.remove();
  return ok;
}

function selecionar(id: string) {
  const el = document.getElementById(id);
  if (!el) return;
  if (el instanceof HTMLInputElement || el instanceof HTMLTextAreaElement) {
    el.select();
    return;
  }
  window.getSelection()?.selectAllChildren(el);
}

export function Copiar({
  texto,
  rotulo = "Copiar",
  copiado: rotuloCopiado = "Copiado",
  variant = "outline",
  size = "sm",
  alvoId,
}: Props) {
  const [resultado, setResultado] = useState<Resultado>("nada");
  const timer = useRef<ReturnType<typeof setTimeout> | null>(null);

  useEffect(
    () => () => {
      if (timer.current) clearTimeout(timer.current);
    },
    [],
  );

  async function copiar() {
    let ok = false;
    try {
      await navigator.clipboard.writeText(texto);
      ok = true;
    } catch {
      ok = copiarAntigo(texto);
    }
    if (!ok && alvoId) selecionar(alvoId);
    setResultado(ok ? "copiado" : "falhou");
    if (timer.current) clearTimeout(timer.current);
    timer.current = setTimeout(() => setResultado("nada"), ok ? 2500 : 6000);
  }

  const visivel = resultado === "copiado" ? rotuloCopiado : resultado === "falhou" ? "Selecione e copie" : rotulo;
  const aviso =
    resultado === "copiado"
      ? "Copiado para a área de transferência."
      : resultado === "falhou"
        ? "Não foi possível copiar sozinho. Selecione o texto e copie."
        : "";

  return (
    <>
      <button type="button" onClick={copiar} className={buttonVariants({ variant, size })}>
        {visivel}
      </button>
      <span className="sr-only" aria-live="polite">
        {aviso}
      </span>
    </>
  );
}
