"use client";

import { useEffect, useRef, useState } from "react";
import { Button } from "@beeads/ui";

type Props = {
  texto: string;
  rotulo?: string;
  copiado?: string;
  variant?: "default" | "outline";
  size?: "sm" | "lg";
};

export function Copiar({ texto, rotulo = "Copiar", copiado: rotuloCopiado = "Copiado", variant = "outline", size = "sm" }: Props) {
  const [copiado, setCopiado] = useState(false);
  const timer = useRef<ReturnType<typeof setTimeout> | null>(null);

  useEffect(
    () => () => {
      if (timer.current) clearTimeout(timer.current);
    },
    [],
  );

  async function copiar() {
    try {
      await navigator.clipboard.writeText(texto);
    } catch {
      return; // sem permissão de área de transferência: o rótulo não muda
    }
    setCopiado(true);
    if (timer.current) clearTimeout(timer.current);
    timer.current = setTimeout(() => setCopiado(false), 2500);
  }

  return (
    <Button type="button" variant={variant} size={size} onClick={copiar} aria-live="polite">
      {copiado ? rotuloCopiado : rotulo}
    </Button>
  );
}
