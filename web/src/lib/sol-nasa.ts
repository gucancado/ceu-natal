// Foto do Sol de hoje, do satélite SDO da NASA (instrumento HMI, luz visível, domínio público): o disco
// com as manchas solares do dia. A NASA atualiza a cada ~15 minutos; aqui fica em memória por meia hora e,
// se a NASA falhar, serve a última que deu certo.
const URL_SOL = "https://sdo.gsfc.nasa.gov/assets/img/latest/latest_512_HMIIC.jpg";
const TEMPO_MAX_MS = 10000;
const VALIDADE_MS = 30 * 60 * 1000;

let guardada: { em: number; imagem: ArrayBuffer } | null = null;

export async function solDeHoje(agora = Date.now()): Promise<ArrayBuffer | null> {
  if (guardada && agora - guardada.em < VALIDADE_MS) return guardada.imagem;
  try {
    const r = await fetch(URL_SOL, { cache: "no-store", signal: AbortSignal.timeout(TEMPO_MAX_MS) });
    if (!r.ok) throw new Error(`sdo ${r.status}`);
    guardada = { em: agora, imagem: await r.arrayBuffer() };
  } catch {
    // Mantém a anterior, se houver.
  }
  return guardada?.imagem ?? null;
}
