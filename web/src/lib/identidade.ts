// Ids anônimos que o formulário do site envia ao servidor.
// - visitante: um por navegador, guardado no localStorage; liga os mapas feitos
//   aqui ao contato, se a pessoa deixar um.
// - mapa: um por data de nascimento; o mapa feito só com a data e completado
//   depois com hora e cidade continua sendo o mesmo mapa.
const CHAVE_VISITANTE = "ceu-natal-visitante";

function novoId(): string {
  if (typeof crypto !== "undefined" && typeof crypto.randomUUID === "function") return crypto.randomUUID();
  // Navegador antigo: UUID v4 com Math.random.
  return "xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx".replace(/[xy]/g, (c) => {
    const r = (Math.random() * 16) | 0;
    return (c === "x" ? r : (r & 0x3) | 0x8).toString(16);
  });
}

let visitanteDaPagina: string | null = null;

export function idVisitante(armazenamento?: Pick<Storage, "getItem" | "setItem">): string {
  try {
    const s = armazenamento ?? window.localStorage;
    const salvo = s.getItem(CHAVE_VISITANTE);
    if (salvo) return salvo;
    const id = novoId();
    s.setItem(CHAVE_VISITANTE, id);
    return id;
  } catch {
    // Sem localStorage (aba anônima bloqueada etc.): vale só enquanto a página estiver aberta.
    visitanteDaPagina ??= novoId();
    return visitanteDaPagina;
  }
}

// Id do mapa por data de nascimento, estável enquanto a página está aberta.
export function criarIdsDeMapa(): (data: string) => string {
  const porData = new Map<string, string>();
  return (data) => {
    let id = porData.get(data);
    if (!id) {
      id = novoId();
      porData.set(data, id);
    }
    return id;
  };
}
