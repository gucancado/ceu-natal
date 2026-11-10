// Guias de conexão por cliente. Fonte: pesquisa de 2026-11-03 (fluxos verificados em novembro de 2026).
import { chatgpt } from "./chatgpt";
import { claudeAi } from "./claude-ai";
import { claudeCode } from "./claude-code";
import { claudeDesktop } from "./claude-desktop";
import { cursor } from "./cursor";
import { gemini } from "./gemini";
import { manus } from "./manus";
import { n8n } from "./n8n";
import type { Cliente } from "./tipos";

export type { Cliente } from "./tipos";

export const clientes: Cliente[] = [claudeAi, claudeDesktop, claudeCode, chatgpt, gemini, manus, cursor, n8n];

// Botões da home: um só para o Claude. Os guias do Desktop e do Code seguem em /conectar.
export const clientesDaGrade = clientes.filter((c) => c !== claudeDesktop && c !== claudeCode);

export function cliente(slug: string): Cliente | undefined {
  return clientes.find((c) => c.slug === slug);
}
