// Prompt em markdown do formulário da home: cresce conforme a pessoa preenche os dados.
// Só dados → string, sem React.
import { passosConexao } from "../content/setup";
import { aspecto, grauMinuto, nome, orientacoesIa, signo, type MapaRapido, type Ponto } from "./mapa-texto";
import { site } from "./site";

export type DadosPrompt = {
  dia: string;
  mes: string;
  ano: string;
  hora: string;
  cidade: string;
  /** Signo do Sol só pelo dia e mês, enquanto o servidor não calculou. */
  solPelaData: { signo: string; cuspide: boolean } | null;
  /** Mapa mais completo que o servidor já devolveu para os dados atuais. */
  mapa: MapaRapido | null;
};

const dois = (s: string) => s.padStart(2, "0");

function linhaPonto(chave: string, p: Ponto): string {
  const partes = [`${p.grau} ${signo(p.signo)}`];
  if (typeof p.casa === "number") partes.push(`casa ${p.casa}`);
  if (p.retrogrado) partes.push("retrógrado");
  return `- **${nome(chave)}:** ${partes.join(", ")}`;
}

const temItens = (o?: Record<string, unknown> | null): o is Record<string, Ponto> => !!o && Object.keys(o).length > 0;

function secoesMapa(m: MapaRapido): string[] {
  const linhas = ["### Planetas", ...Object.entries(m.planetas).map(([k, p]) => linhaPonto(k, p))];
  if (temItens(m.pontos_sensiveis)) {
    linhas.push("", "### Pontos sensíveis", ...Object.entries(m.pontos_sensiveis).map(([k, p]) => linhaPonto(k, p)));
  }
  if (temItens(m.angulos)) {
    linhas.push("", "### Ângulos", ...Object.entries(m.angulos).map(([k, p]) => linhaPonto(k, p)));
  }
  if (temItens(m.casas)) {
    linhas.push(
      "",
      `### Cúspides das casas${m.sistema_casas ? ` (${m.sistema_casas})` : ""}`,
      ...Object.entries(m.casas).map(([k, p]) => `- **Casa ${k.replace("casa_", "")}:** ${p.grau} ${signo(p.signo)}`),
    );
  }
  // Nodo Norte e Nodo Sul estão sempre em oposição exata: não informa nada.
  const aspectos = (m.aspectos ?? []).filter((a) => !(a.planeta_a.startsWith("nodo_") && a.planeta_b.startsWith("nodo_")));
  if (aspectos.length > 0) {
    linhas.push(
      "",
      "### Aspectos",
      ...aspectos.map((a) => `- ${nome(a.planeta_a)} ${aspecto(a.tipo)} ${nome(a.planeta_b)} (orbe ${grauMinuto(a.orbe)})`),
    );
  }
  return linhas;
}

export function promptMapa(d: DadosPrompt): string {
  const temData = d.dia && d.mes;
  const data = temData ? `${dois(d.dia)}/${dois(d.mes)}${d.ano.length === 4 ? `/${d.ano}` : ""}` : "";
  const cidade = d.cidade.trim();
  const temCasas = !!d.mapa && temItens(d.mapa.casas);
  const falta = [
    !(temData && d.ano.length === 4) && "a data completa",
    !d.hora && "a hora",
    !cidade && "a cidade",
  ].filter(Boolean) as string[];

  const linhas = [
    `# Meu mapa astral com o ${site.nome}`,
    "",
    `O ${site.nome} é um servidor MCP gratuito que calcula astrologia com as efemérides suíças. Endereço: ${site.mcpEndpoint} (sem login e sem chave).`,
    "",
    "## Meus dados de nascimento",
    `- **Data:** ${data || "ainda não informei"}${temData && d.ano.length !== 4 ? " (ainda sem o ano)" : ""}`,
    `- **Hora:** ${d.hora || "ainda não informei"}`,
    `- **Cidade:** ${cidade || "ainda não informei"}`,
    "",
    "## Meu mapa natal",
  ];

  if (d.mapa) {
    linhas.push(
      `> Calculado pelo ${site.nome} com as efemérides suíças. Use estas posições como estão: não recalcule nem estime outras.`,
      "",
    );
    if (!temCasas) linhas.push("_Sem hora e cidade, ainda não há ascendente nem casas._", "");
    linhas.push(...secoesMapa(d.mapa));
  } else if (d.solPelaData) {
    linhas.push(
      `- **Sol:** ${d.solPelaData.signo} (pelo dia e mês${d.solPelaData.cuspide ? "; a data está na troca de signo e o ano confirma" : ""})`,
    );
  } else {
    linhas.push("_Ainda não calculado._");
  }

  linhas.push(
    "",
    "## O que eu quero",
    `1. Se as ferramentas do ${site.nome} já estiverem disponíveis nesta conversa, use-as para conferir e completar o mapa.`,
    `2. Se não, me passe numa única mensagem todos os passos para conectar o ${site.nome} neste aplicativo, com o link direto e os valores prontos para copiar. ${passosConexao.chatgpt} ${passosConexao.claude} ${passosConexao.outros}`,
    "3. Enquanto isso, interprete o mapa acima: me dê uma leitura curta e sugira o que mais posso pedir, como trânsitos, sinastria ou revolução solar.",
  );
  if (falta.length > 0) {
    linhas.push(`4. Ainda falta ${falta.join(", ").replace(/, ([^,]*)$/, " e $1")}. Me peça numa única pergunta.`);
  }

  // O primeiro item de orientacoesIa() é o título em caixa alta do texto puro; aqui vira um ## próprio.
  linhas.push("", `## Para a IA: sobre o ${site.nome}`, ...orientacoesIa().slice(1), "");
  return linhas.join("\n");
}
