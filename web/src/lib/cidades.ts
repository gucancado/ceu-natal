// Sugestões de cidade para o campo do formulário da home. A lista (public/municipios.json, gerada por
// scripts/gerar_municipios.py) vem do IBGE, do município mais populoso para o menos.
export type Municipio = [nome: string, uf: string];

// Apelidos que não saem das iniciais do nome.
const APELIDOS: Record<string, string> = {
  sampa: "São Paulo|SP",
  rio: "Rio de Janeiro|RJ",
  poa: "Porto Alegre|RS",
  bsb: "Brasília|DF",
  df: "Brasília|DF",
  cwb: "Curitiba|PR",
  floripa: "Florianópolis|SC",
  fln: "Florianópolis|SC",
  ssa: "Salvador|BA",
  rec: "Recife|PE",
  bhz: "Belo Horizonte|MG",
  bel: "Belém|PA",
  vix: "Vitória|ES",
};

const LIGACOES = new Set(["de", "da", "do", "das", "dos", "e", "d"]);

export function normalizar(s: string): string {
  return s
    .normalize("NFD")
    .replace(/[̀-ͯ]/g, "")
    .toLowerCase()
    .replace(/[^a-z0-9, ]+/g, " ")
    .replace(/\s+/g, " ")
    .trim();
}

type Indice = { m: Municipio; nome: string; palavras: string[]; iniciais: string; uf: string }[];
const indices = new WeakMap<Municipio[], Indice>();

function indice(lista: Municipio[]): Indice {
  let i = indices.get(lista);
  if (!i) {
    i = lista.map((m) => {
      const nome = normalizar(m[0]);
      const palavras = nome.split(" ");
      const iniciais = palavras
        .filter((p) => !LIGACOES.has(p))
        .map((p) => p[0])
        .join("");
      return { m, nome, palavras, iniciais, uf: m[1].toLowerCase() };
    });
    indices.set(lista, i);
  }
  return i;
}

export const rotuloCidade = (m: Municipio) => `${m[0]}, ${m[1]}`;

// Ordem: apelido, começo do nome, começo de uma palavra, iniciais. Dentro de cada grupo, a mais populosa primeiro.
export function sugerirCidades(lista: Municipio[], consulta: string, max = 6): Municipio[] {
  const [q = "", ufQ = ""] = normalizar(consulta).split(",").map((s) => s.trim());
  if (q.length < 2) return [];
  const grupos: Municipio[][] = [[], [], [], []];
  const apelido = APELIDOS[q];
  for (const c of indice(lista)) {
    if (ufQ && !c.uf.startsWith(ufQ)) continue;
    if (apelido && `${c.m[0]}|${c.m[1]}` === apelido) grupos[0].push(c.m);
    else if (c.nome.startsWith(q)) grupos[1].push(c.m);
    else if (c.palavras.some((p) => p.startsWith(q))) grupos[2].push(c.m);
    else if (!q.includes(" ") && c.iniciais.startsWith(q)) grupos[3].push(c.m);
    if (grupos[0].length + grupos[1].length >= max) break;
  }
  return grupos.flat().slice(0, max);
}
