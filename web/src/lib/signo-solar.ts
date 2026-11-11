// Signo solar só pelo dia e mês, antes de o servidor calcular. A data exata da troca varia um dia de
// ano para ano, por isso o dia da troca e o anterior são marcados como cúspide.

// Dia em que o Sol entra no signo, mês a mês (janeiro → Aquário em 20/01).
const ENTRADA: { dia: number; signo: string }[] = [
  { dia: 20, signo: "Aquário" },
  { dia: 19, signo: "Peixes" },
  { dia: 21, signo: "Áries" },
  { dia: 20, signo: "Touro" },
  { dia: 21, signo: "Gêmeos" },
  { dia: 21, signo: "Câncer" },
  { dia: 23, signo: "Leão" },
  { dia: 23, signo: "Virgem" },
  { dia: 23, signo: "Libra" },
  { dia: 23, signo: "Escorpião" },
  { dia: 22, signo: "Sagitário" },
  { dia: 22, signo: "Capricórnio" },
];

const DIAS_NO_MES = [31, 29, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31];

export function diaMesValidos(dia: number, mes: number): boolean {
  return Number.isInteger(dia) && Number.isInteger(mes) && mes >= 1 && mes <= 12 && dia >= 1 && dia <= DIAS_NO_MES[mes - 1];
}

export function dataValida(dia: number, mes: number, ano: number): boolean {
  if (!diaMesValidos(dia, mes) || !Number.isInteger(ano) || ano < 1800 || ano > 2100) return false;
  if (mes === 2 && dia === 29) return (ano % 4 === 0 && ano % 100 !== 0) || ano % 400 === 0;
  return true;
}

export function signoSolar(dia: number, mes: number): { signo: string; cuspide: boolean } | null {
  if (!diaMesValidos(dia, mes)) return null;
  const entrada = ENTRADA[mes - 1];
  const signo = dia >= entrada.dia ? entrada.signo : ENTRADA[(mes + 10) % 12].signo;
  return { signo, cuspide: dia === entrada.dia || dia === entrada.dia - 1 };
}
