// Mapa natal (JSON do /mapa-rapido) → texto para colar no assistente. Só dados → string.
import { site } from "./site";

type Ponto = { signo: string; grau: string; retrogrado?: boolean; casa?: number | null };
type Aspecto = { planeta_a: string; planeta_b: string; tipo: string; orbe: number };

export type MapaRapido = {
  nascimento: { data: string; hora?: string | null; local?: string | null };
  sistema_casas?: string | null;
  planetas: Record<string, Ponto>;
  pontos_sensiveis?: Record<string, Ponto> | null;
  angulos?: Record<string, Ponto> | null;
  casas?: Record<string, Ponto> | null;
  aspectos?: Aspecto[] | null;
};

const SIGNOS: Record<string, string> = {
  Aries: "Áries", Gemeos: "Gêmeos", Cancer: "Câncer", Leao: "Leão", Escorpiao: "Escorpião",
  Sagitario: "Sagitário", Capricornio: "Capricórnio", Aquario: "Aquário",
};

const NOMES: Record<string, string> = {
  sol: "Sol", lua: "Lua", mercurio: "Mercúrio", venus: "Vênus", marte: "Marte",
  jupiter: "Júpiter", saturno: "Saturno", urano: "Urano", netuno: "Netuno", plutao: "Plutão",
  nodo_norte_verdadeiro: "Nodo Norte", nodo_sul_verdadeiro: "Nodo Sul", chiron: "Quíron",
  ascendente: "Ascendente", meio_do_ceu: "Meio do Céu", descendente: "Descendente",
  fundo_do_ceu: "Fundo do Céu",
};

const ASPECTOS: Record<string, string> = {
  conjuncao: "conjunção", oposicao: "oposição", trigono: "trígono", inconjuncao: "quincúncio",
  semi_sextil: "semissextil", semi_quadratura: "semiquadratura",
};

const signo = (s: string) => SIGNOS[s] ?? s;
const nome = (n: string) => NOMES[n] ?? n.replace(/_/g, " ");
const aspecto = (t: string) => ASPECTOS[t] ?? t.replace(/_/g, " ");

export function grauMinuto(decimal: number): string {
  const total = Math.round(Math.abs(decimal) * 60);
  return `${Math.floor(total / 60)}°${String(total % 60).padStart(2, "0")}'`;
}

function linhaPonto(chave: string, p: Ponto): string {
  const partes = [`${p.grau} ${signo(p.signo)}`];
  if (typeof p.casa === "number") partes.push(`casa ${p.casa}`);
  if (p.retrogrado) partes.push("retrógrado");
  return `- ${nome(chave)}: ${partes.join(", ")}`;
}

const temItens = (o?: Record<string, unknown> | null) => !!o && Object.keys(o).length > 0;

export function textoMapa(m: MapaRapido): string {
  const n = m.nascimento;
  const quando = [n.data, n.hora, n.local].filter(Boolean).join(", ");
  const temCasas = temItens(m.casas);
  const linhas = [
    `Este é o meu mapa natal, calculado pelo ${site.nome} com as efemérides suíças. Use estas posições como estão: não recalcule nem estime outras.`,
    "",
    `Antes de interpretar, quero conectar o ${site.nome} aqui para você calcular trânsitos, sinastria e revoluções com a mesma precisão. Me guie, um passo por vez, para adicionar o servidor MCP ${site.mcpEndpoint} (sem login e sem chave) neste aplicativo. O passo a passo de cada aplicativo está em ${site.url}/conectar. Se não der para conectar aqui, siga só com os dados abaixo. Depois, me pergunte o que eu quero saber do mapa.`,
    "",
    "MAPA NATAL",
    `Nascimento: ${quando}`,
  ];
  if (temCasas && m.sistema_casas) linhas.push(`Sistema de casas: ${m.sistema_casas}`);
  if (!temCasas) linhas.push("Sem hora ou cidade: sem casas nem ângulos.");
  linhas.push("", "Planetas", ...Object.entries(m.planetas).map(([k, p]) => linhaPonto(k, p)));
  if (temItens(m.pontos_sensiveis)) {
    linhas.push("", "Pontos sensíveis", ...Object.entries(m.pontos_sensiveis!).map(([k, p]) => linhaPonto(k, p)));
  }
  if (temItens(m.angulos)) {
    linhas.push("", "Ângulos", ...Object.entries(m.angulos!).map(([k, p]) => linhaPonto(k, p)));
  }
  if (temCasas) {
    linhas.push(
      "",
      "Cúspides das casas",
      ...Object.entries(m.casas!).map(([k, p]) => `- Casa ${k.replace("casa_", "")}: ${p.grau} ${signo(p.signo)}`),
    );
  }
  if (m.aspectos && m.aspectos.length > 0) {
    linhas.push(
      "",
      "Aspectos",
      ...m.aspectos.map(
        (a) => `- ${nome(a.planeta_a)} ${aspecto(a.tipo)} ${nome(a.planeta_b)} (orbe ${grauMinuto(a.orbe)})`,
      ),
    );
  }
  linhas.push("", `Calculado em ${site.url}`);
  return linhas.join("\n");
}
