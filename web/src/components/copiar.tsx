"use client";

import { useEffect, useRef, useState } from "react";
import { Button } from "@beeads/ui";

export function Copiar({ texto }: { texto: string }) {
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
    timer.current = setTimeout(() => setCopiado(false), 2000);
  }

  return (
    <Button type="button" variant="outline" size="sm" onClick={copiar} aria-live="polite">
      {copiado ? "Copiado" : "Copiar"}
    </Button>
  );
}
