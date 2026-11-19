"use client";

import { useEffect, useRef } from "react";
import { usePathname } from "next/navigation";
import { site } from "@/lib/site";
import { corpoVisita } from "@/lib/visita";

// Avisa o servidor a cada página aberta (inclusive navegação interna). Sem cookie e sem id: o servidor
// guarda só a contagem por página e o domínio de origem. `sendBeacon` manda como text/plain, sem preflight.
export function ContadorVisita() {
  const pathname = usePathname();
  const primeira = useRef(true);

  useEffect(() => {
    if (!pathname || typeof navigator.sendBeacon !== "function") return;
    // Só a primeira página da visita tem referência externa; as seguintes vieram do próprio site.
    const referrer = primeira.current ? document.referrer : "";
    primeira.current = false;
    const nav = navigator as Navigator & { globalPrivacyControl?: boolean };
    const corpo = corpoVisita(pathname, referrer, window.location.hostname, {
      webdriver: nav.webdriver,
      doNotTrack: nav.doNotTrack,
      gpc: nav.globalPrivacyControl,
    });
    if (corpo) navigator.sendBeacon(`${site.mcpUrl}/visita`, corpo);
  }, [pathname]);

  return null;
}
