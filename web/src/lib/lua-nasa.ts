// Foto da Lua na fase da hora atual, do Dial-A-Moon da NASA (Scientific Visualization Studio, domínio
// público, feita com dados da sonda LRO). Fica em memória por hora; se a NASA falhar, serve a última que deu certo.
const API = "https://svs.gsfc.nasa.gov/api/dialamoon/";
const ORIGEM_IMAGEM = "https://svs.gsfc.nasa.gov/";
const TEMPO_MAX_MS = 10000;

export type LuaDaHora = { hora: string; imagem: ArrayBuffer; fase: number; idade: number };

let guardada: LuaDaHora | null = null;

/** "2026-11-11T12:00": a hora cheia em UTC, no formato que a API aceita. */
export function horaUtc(agora: Date): string {
  return `${agora.toISOString().slice(0, 13)}:00`;
}

// Reserva para quando a NASA falha: as 8 fases da biblioteca de imagens da NASA (images.nasa.gov,
// domínio público, mesmo estilo e orientação do Dial-A-Moon) em public/lua/0.jpg (nova) a 7.jpg (minguante).
const MES_SINODICO = 29.530588853;
const LUA_NOVA_REF = Date.UTC(2000, 0, 6, 18, 14); // lua nova de 6/1/2000, 18h14 UTC

/** Idade da Lua em dias (0 = nova), pela média do mês sinódico; erra no máximo cerca de meio dia. */
export function idadeDaLua(agora: Date): number {
  const dias = (agora.getTime() - LUA_NOVA_REF) / 86400000;
  return ((dias % MES_SINODICO) + MES_SINODICO) % MES_SINODICO;
}

/** Caminho da foto de reserva com a fase mais próxima de agora. */
export function luaReserva(agora = new Date()): string {
  return `/lua/${Math.round((idadeDaLua(agora) / MES_SINODICO) * 8) % 8}.jpg`;
}

export async function luaDaHora(agora = new Date()): Promise<LuaDaHora | null> {
  const hora = horaUtc(agora);
  if (guardada?.hora === hora) return guardada;
  try {
    const r = await fetch(API + hora, { cache: "no-store", signal: AbortSignal.timeout(TEMPO_MAX_MS) });
    if (!r.ok) throw new Error(`dialamoon ${r.status}`);
    const info = await r.json();
    // A API devolve http://; a mesma imagem existe em https.
    const url = String(info?.image?.url ?? "").replace(/^http:\/\//, "https://");
    if (!url.startsWith(ORIGEM_IMAGEM)) throw new Error("imagem fora da NASA");
    const img = await fetch(url, { cache: "no-store", signal: AbortSignal.timeout(TEMPO_MAX_MS) });
    if (!img.ok) throw new Error(`imagem ${img.status}`);
    guardada = { hora, imagem: await img.arrayBuffer(), fase: Number(info.phase), idade: Number(info.age) };
  } catch {
    // Mantém a anterior, se houver.
  }
  return guardada;
}
