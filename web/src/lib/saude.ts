// Lê o /health do servidor MCP para a página /status.
export type Saude =
  | { ok: true; versao: string; limites: { por_sessao_por_min: number; global_por_min: number } }
  | { ok: false; motivo: string };

/**
 * Versão do servidor para o schema.org, revista a cada hora (ISR): a página continua estática.
 * Fora do ar ou resposta estranha: null, e o JSON-LD sai sem `softwareVersion`.
 */
export async function versaoServidor(mcpUrl: string, fetchImpl: typeof fetch = fetch): Promise<string | null> {
  try {
    const r = await fetchImpl(`${mcpUrl}/health`, { signal: AbortSignal.timeout(3000), next: { revalidate: 3600 } });
    if (!r.ok) return null;
    const j = (await r.json()) as { versao?: unknown };
    return typeof j.versao === "string" ? j.versao : null;
  } catch {
    return null;
  }
}

export async function lerSaude(mcpUrl: string, fetchImpl: typeof fetch = fetch): Promise<Saude> {
  try {
    const r = await fetchImpl(`${mcpUrl}/health`, { signal: AbortSignal.timeout(5000), cache: "no-store" });
    if (!r.ok) return { ok: false, motivo: `o servidor respondeu ${r.status}` };
    const j = (await r.json()) as { versao?: unknown; limites?: { por_sessao_por_min?: unknown; global_por_min?: unknown } };
    const porSessao = j.limites?.por_sessao_por_min;
    const global = j.limites?.global_por_min;
    if (typeof j.versao !== "string" || typeof porSessao !== "number" || typeof global !== "number") {
      return { ok: false, motivo: "resposta inesperada do servidor" };
    }
    return { ok: true, versao: j.versao, limites: { por_sessao_por_min: porSessao, global_por_min: global } };
  } catch (e) {
    const nome = e instanceof Error ? e.name : "";
    return {
      ok: false,
      motivo: nome === "TimeoutError" ? "o servidor não respondeu em 5 segundos" : "não foi possível falar com o servidor",
    };
  }
}
