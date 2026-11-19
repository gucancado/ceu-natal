// Contador de páginas abertas, sem cookie: o site manda ao servidor só o caminho da página e o domínio
// de onde a pessoa veio. O servidor soma por dia (ver `POST /visita` em app/server.py). Só dados → string.

export type Visita = { pagina: string; referencia: string };

/** Host de `document.referrer` quando é outro site; vazio se for o próprio site ou não houver. */
export function hostReferencia(referrer: string, hostSite: string): string {
  if (!referrer) return "";
  try {
    const host = new URL(referrer).hostname.toLowerCase();
    return host === hostSite.toLowerCase() ? "" : host;
  } catch {
    return "";
  }
}

/** Corpo do `POST /visita`, ou null quando a visita não deve contar (robô ou pedido de não rastrear). */
export function corpoVisita(
  pagina: string,
  referrer: string,
  hostSite: string,
  sinais: { webdriver?: boolean; doNotTrack?: string | null; gpc?: boolean } = {},
): string | null {
  if (sinais.webdriver || sinais.doNotTrack === "1" || sinais.gpc) return null;
  const visita: Visita = { pagina, referencia: hostReferencia(referrer, hostSite) };
  return JSON.stringify(visita);
}
