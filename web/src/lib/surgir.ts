import { useEffect, type RefObject } from "react";

// Marca a foto como carregada (data-carregada), para o CSS fazer o fade in (.surge, em globals.css).
// Se a foto já veio do cache antes da hidratação, marca na hora e o fade roda do mesmo jeito.
export function useSurgir(ref: RefObject<HTMLImageElement | null>) {
  useEffect(() => {
    const img = ref.current;
    if (!img) return;
    const marcar = () => img.setAttribute("data-carregada", "");
    if (img.complete && img.naturalWidth) marcar();
    else img.addEventListener("load", marcar, { once: true });
    return () => img.removeEventListener("load", marcar);
  }, [ref]);
}
