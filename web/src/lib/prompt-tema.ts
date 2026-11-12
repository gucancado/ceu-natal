// Prompts dos formulários das landings (trânsitos, sinastria, revolução solar). Mesmo formato do prompt da
// home (lib/prompt-mapa.ts): os dados calculados primeiro, as instruções para a IA depois. Só dados → string.
import { passosConexao } from "../content/setup";
import { glifoPonto } from "./glifos";
import { aspecto, grauMinuto, nome, orientacoesIa, signo, type Ponto } from "./mapa-texto";
import { linhaPonto } from "./prompt-mapa";
import { site } from "./site";

export type Tema = "transitos" | "sinastria" | "revolucao_solar";

/** Dados de nascimento como a pessoa preencheu (texto para o prompt). */
export type Nascimento = { data: string; hora: string; cidade: string };

type AspectoComOrbe = { tipo: string; orbe: number; aplicando?: boolean };

export type ResultadoTransitos = {
  transito: { data: string };
  planetas_em_transito: Record<string, Ponto & { casa_natal?: number | null }>;
  aspectos_transito_natal: (AspectoComOrbe & { planeta_transito: string; planeta_natal: string })[];
  sintese: { transitos_lentos_destacados: { planeta_transito: string; planeta_natal: string; tipo: string; orbe: number }[] };
};

export type ResultadoSinastria = {
  pessoa_a: { sol: string; lua: string; asc: string | null };
  pessoa_b: { sol: string; lua: string; asc: string | null };
  aspectos_sinastria: (AspectoComOrbe & { planeta_a: string; planeta_b: string })[];
  ativacoes_de_casas: { planeta: string; pessoa: string; cai_na_casa: number; da_pessoa: string }[];
  sintese_sinastria: { aspectos_harmonicos: number; aspectos_tensao: number; aspectos_neutros: number };
  aviso?: string;
};

export type ResultadoRevolucao = {
  ano: number;
  revolucao: { instante_local: string; local: string; vigencia?: { fim_aproximado_utc?: string } };
  planetas: Record<string, Ponto>;
  angulos?: Record<string, Ponto>;
  aspectos_revolucao_natal: (AspectoComOrbe & { planeta_revolucao: string; planeta_natal: string; definicional?: boolean })[];
  destaques: {
    ascendente_revolucao: { signo: string; grau: string; regente_moderno: string; regente_tradicional: string; casa_natal_onde_cai: number | null };
    sol_revolucao: { casa_revolucao: number | null; casa_natal: number | null };
    lua_revolucao: { signo: string; grau: string; casa_revolucao: number | null; casa_natal: number | null };
    planetas_angulares: string[];
  };
};

// Orbe máximo dos aspectos listados: os mais largos pesam pouco e deixariam o prompt enorme.
const ORBE_MAX = 3;
// Os dois nodos estão sempre em oposição: um aspecto com o Nodo Sul repete o do Nodo Norte.
const semNodoSul = (...pontos: string[]) => !pontos.includes("nodo_sul_verdadeiro");

const AVISO_CALCULO = `> Calculado pelo ${site.nome} com as efemérides suíças. Use estes dados como estão: não recalcule nem estime outros.`;

function quando(n: Nascimento): string {
  return [n.data || "data ainda não informada", n.hora || "sem hora", n.cidade || "sem cidade"].join(", ");
}

function movimento(a: AspectoComOrbe): string {
  return a.aplicando === undefined ? "" : a.aplicando ? ", aplicando" : ", separando";
}

/** Data e hora de um ISO com fuso ("2026-03-12T08:05:25-03:00"), sem converter: é o horário local. */
function dataHoraLocal(iso: string): string {
  const m = /^(\d{4})-(\d{2})-(\d{2})T(\d{2}):(\d{2})/.exec(iso);
  return m ? `${m[3]}/${m[2]}/${m[1]} às ${m[4]}:${m[5]}` : iso;
}

function dataIso(iso: string): string {
  const m = /^(\d{4})-(\d{2})-(\d{2})/.exec(iso);
  return m ? `${m[3]}/${m[2]}/${m[1]}` : iso;
}

/** Instruções finais, iguais em todo tema: usar as tools se houver, senão conectar, e interpretar já. */
function instrucoes(tools: string, leitura: string, falta: string[], cobre: string): string[] {
  const linhas = [
    "",
    "---",
    "",
    "## Instruções para a IA",
    "",
    `Os dados acima foram calculados pelo ${site.nome}, um servidor MCP gratuito que calcula astrologia com as efemérides suíças. Endereço: ${site.mcpEndpoint} (sem login e sem chave).`,
    "",
    "### O que eu quero",
    `1. Se as ferramentas do ${site.nome} já estiverem disponíveis nesta conversa, use ${tools} para conferir e aprofundar.`,
    `2. Se não, me passe numa única mensagem todos os passos para conectar o ${site.nome} neste aplicativo, com o link direto e os valores prontos para copiar. ${passosConexao.chatgpt} ${passosConexao.claude} ${passosConexao.outros}`,
    `3. Enquanto isso, ${leitura}`,
  ];
  if (falta.length > 0) {
    linhas.push(`4. Ainda falta ${falta.join(", ").replace(/, ([^,]*)$/, " e $1")}. Me peça numa única pergunta.`);
  }
  linhas.push("", `### Sobre o ${site.nome}`, ...orientacoesIa(cobre).slice(1), "");
  return linhas;
}

function faltaNascimento(n: Nascimento, rotulo = ""): string[] {
  return [!n.data && `a data${rotulo}`, !n.hora && `a hora${rotulo}`, !n.cidade && `a cidade${rotulo}`].filter(Boolean) as string[];
}

export function promptTransitos(n: Nascimento, dataTransito: string, r: ResultadoTransitos | null): string {
  const linhas = [`# Meus trânsitos de ${dataTransito}`, "", `**Nascimento:** ${quando(n)}`, ""];
  if (r) {
    linhas.push(AVISO_CALCULO, "");
    const lentos = r.sintese.transitos_lentos_destacados.filter((a) => semNodoSul(a.planeta_natal));
    const chave = (a: { planeta_transito: string; planeta_natal: string; tipo: string }) =>
      `${a.planeta_transito}|${a.planeta_natal}|${a.tipo}`;
    const jaListados = new Set(lentos.map(chave));
    const porChave = new Map(r.aspectos_transito_natal.map((a) => [chave(a), a]));
    if (lentos.length > 0) {
      linhas.push("### Trânsitos mais fortes (planetas lentos, orbe até 2°)");
      for (const a of lentos) {
        const completo = porChave.get(chave(a));
        linhas.push(
          `- ${nome(a.planeta_transito)} em trânsito ${aspecto(a.tipo)} ${nome(a.planeta_natal)} natal (orbe ${grauMinuto(a.orbe)}${completo ? movimento(completo) : ""})`,
        );
      }
      linhas.push("");
    }
    const outros = r.aspectos_transito_natal.filter(
      (a) => a.orbe <= ORBE_MAX && !jaListados.has(chave(a)) && semNodoSul(a.planeta_natal, a.planeta_transito),
    );
    if (outros.length > 0) {
      linhas.push(`### Outros aspectos com o mapa natal (orbe até ${ORBE_MAX}°)`);
      for (const a of outros) {
        linhas.push(
          `- ${nome(a.planeta_transito)} em trânsito ${aspecto(a.tipo)} ${nome(a.planeta_natal)} natal (orbe ${grauMinuto(a.orbe)}${movimento(a)})`,
        );
      }
      linhas.push("");
    }
    linhas.push("### Céu do dia");
    for (const [k, p] of Object.entries(r.planetas_em_transito)) {
      const partes = [`${p.grau} ${signo(p.signo)}`];
      if (typeof p.casa_natal === "number") partes.push(`na casa ${p.casa_natal} natal`);
      if (p.retrogrado) partes.push("retrógrado");
      const g = glifoPonto[k];
      linhas.push(`- ${g ? `${g} ` : ""}**${nome(k)}:** ${partes.join(", ")}`);
    }
    if (!n.hora || !n.cidade) linhas.push("", "_Sem hora e cidade de nascimento, ainda não dá para saber em que casa cada trânsito cai._");
  } else {
    linhas.push("_Ainda não calculado._");
  }
  linhas.push(
    ...instrucoes(
      "calcular_transitos e calcular_mapa_natal",
      "interprete a fase que estou vivendo: comece pelos trânsitos mais fortes, diga o que está começando (aplicando) e o que está passando (separando), e sugira o que mais posso pedir, como os trânsitos de outra data ou minha revolução solar.",
      faltaNascimento(n),
      "os trânsitos desta data sobre o mapa natal desta pessoa",
    ),
  );
  return linhas.join("\n");
}

export function promptSinastria(a: Nascimento, b: Nascimento, r: ResultadoSinastria | null): string {
  const resumo = (p: { sol: string; lua: string; asc: string | null }) =>
    ` (Sol em ${signo(p.sol)}, Lua em ${signo(p.lua)}${p.asc ? `, ascendente em ${signo(p.asc)}` : ""})`;
  const linhas = [
    "# Sinastria entre dois mapas",
    "",
    `**Pessoa 1 (eu):** ${quando(a)}${r ? resumo(r.pessoa_a) : ""}`,
    `**Pessoa 2:** ${quando(b)}${r ? resumo(r.pessoa_b) : ""}`,
    "",
  ];
  if (r) {
    const s = r.sintese_sinastria;
    linhas.push(
      AVISO_CALCULO,
      "",
      `**Aspectos entre os mapas:** ${s.aspectos_harmonicos} harmônicos, ${s.aspectos_tensao} tensos e ${s.aspectos_neutros} neutros.`,
      "",
    );
    const fortes = r.aspectos_sinastria.filter((x) => x.orbe <= ORBE_MAX && semNodoSul(x.planeta_a, x.planeta_b));
    if (fortes.length > 0) {
      linhas.push(`### Aspectos mais fortes (orbe até ${ORBE_MAX}°)`);
      for (const x of fortes) {
        linhas.push(`- ${nome(x.planeta_a)} da pessoa 1 ${aspecto(x.tipo)} ${nome(x.planeta_b)} da pessoa 2 (orbe ${grauMinuto(x.orbe)})`);
      }
      linhas.push("");
    }
    const casas = r.ativacoes_de_casas.filter((x) => semNodoSul(x.planeta));
    if (casas.length > 0) {
      linhas.push("### Planetas de um nas casas do outro");
      for (const x of casas) linhas.push(`- ${nome(x.planeta)} da ${x.pessoa} cai na casa ${x.cai_na_casa} da ${x.da_pessoa}`);
      linhas.push("");
    } else {
      linhas.push("_Sem hora e cidade das duas pessoas, ainda não dá para ver os planetas de um nas casas do outro._", "");
    }
  } else {
    linhas.push("_Ainda não calculado._");
  }
  linhas.push(
    ...instrucoes(
      "calcular_sinastria e calcular_mapa_composto",
      "interprete a relação a partir dos aspectos acima: onde as duas pessoas combinam, onde se estranham e o que isso pede de cada uma. Depois sugira o que mais posso pedir, como o mapa composto da relação.",
      [...faltaNascimento(a, " da pessoa 1"), ...faltaNascimento(b, " da pessoa 2")],
      "a sinastria entre estas duas pessoas",
    ),
  );
  return linhas.join("\n");
}

export function promptRevolucaoSolar(n: Nascimento, ano: string, cidadeAniversario: string, r: ResultadoRevolucao | null): string {
  const linhas = [`# Minha revolução solar de ${ano || "…"}`, "", `**Nascimento:** ${quando(n)}`];
  if (cidadeAniversario) linhas.push(`**Aniversário em:** ${cidadeAniversario}`);
  linhas.push("");
  if (r) {
    const fim = r.revolucao.vigencia?.fim_aproximado_utc;
    linhas.push(
      `**Revolução:** ${dataHoraLocal(r.revolucao.instante_local)} (horário local), em ${r.revolucao.local}${fim ? `; vale até por volta de ${dataIso(fim)}` : ""}`,
      "",
      AVISO_CALCULO,
      "",
    );
    const d = r.destaques;
    const asc = d.ascendente_revolucao;
    const regentes = asc.regente_moderno === asc.regente_tradicional
      ? `regente ${nome(asc.regente_moderno)}`
      : `regentes ${nome(asc.regente_moderno)} (moderno) e ${nome(asc.regente_tradicional)} (tradicional)`;
    linhas.push(
      "### Destaques do ano",
      `- **Ascendente da revolução:** ${asc.grau} ${signo(asc.signo)}, ${regentes}${asc.casa_natal_onde_cai ? `; cai na casa ${asc.casa_natal_onde_cai} natal` : ""}`,
      `- ${glifoPonto.sol} **Sol da revolução:** casa ${d.sol_revolucao.casa_revolucao ?? "?"} da revolução, casa ${d.sol_revolucao.casa_natal ?? "?"} natal`,
      `- ${glifoPonto.lua} **Lua da revolução:** ${d.lua_revolucao.grau} ${signo(d.lua_revolucao.signo)}, casa ${d.lua_revolucao.casa_revolucao ?? "?"} da revolução, casa ${d.lua_revolucao.casa_natal ?? "?"} natal`,
      `- **Planetas angulares:** ${d.planetas_angulares.length > 0 ? d.planetas_angulares.map(nome).join(", ") : "nenhum"}`,
      "",
    );
    if (r.angulos) linhas.push("### Ângulos da revolução", ...Object.entries(r.angulos).map(([k, p]) => linhaPonto(k, p)), "");
    linhas.push("### Planetas da revolução", ...Object.entries(r.planetas).map(([k, p]) => linhaPonto(k, p)), "");
    const aspectos = r.aspectos_revolucao_natal.filter(
      (x) => !x.definicional && x.orbe <= 2 && semNodoSul(x.planeta_revolucao, x.planeta_natal),
    );
    if (aspectos.length > 0) {
      linhas.push("### Aspectos da revolução com o mapa natal (orbe até 2°)");
      for (const x of aspectos) {
        linhas.push(`- ${nome(x.planeta_revolucao)} da revolução ${aspecto(x.tipo)} ${nome(x.planeta_natal)} natal (orbe ${grauMinuto(x.orbe)})`);
      }
    }
  } else {
    linhas.push("_Ainda não calculado. A revolução solar precisa da data, da hora e da cidade de nascimento._");
  }
  linhas.push(
    ...instrucoes(
      "calcular_revolucao_solar e calcular_mapa_natal",
      "interprete o meu ano a partir dos destaques acima: o tom do ascendente da revolução, a área de vida do Sol e da Lua, e os aspectos com o mapa natal. Depois sugira o que mais posso pedir, como comparar a revolução em outra cidade ou os trânsitos do ano.",
      faltaNascimento(n),
      "a revolução solar deste ano para esta pessoa",
    ),
  );
  return linhas.join("\n");
}
