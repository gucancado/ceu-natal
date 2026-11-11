import { site } from "../../lib/site";
import type { Cliente } from "./tipos";

const config = { mcpServers: { "ceu-natal": { serverUrl: site.mcpEndpoint } } };

export const gemini: Cliente = {
  slug: "gemini",
  nome: "Gemini",
  resumo:
    "O app do Gemini só aceita servidor MCP por URL nos Estados Unidos e não está disponível no Brasil hoje. Aqui, o caminho é o Antigravity, que substituiu o Gemini CLI.",
  planoMinimo:
    "App do Gemini: só nos Estados Unidos. Antigravity: o plano exigido não está documentado.",
  semLogin: true,
  confianca: "media",
  passos: [
    "O app do Gemini ainda não aceita conectores no Brasil. Use o Antigravity, do Google (app, IDE ou CLI `agy`).",
    "Cole o bloco abaixo em `~/.gemini/config/mcp_config.json` e salve.",
  ],
  snippet: { linguagem: "json", codigo: JSON.stringify(config, null, 2) },
  limitacoes: [
    "O Antigravity substituiu o Gemini CLI, que parou de atender contas individuais em junho de 2026.",
    "No IDE, o arquivo abre pelo menu **…** do painel do Agent > **MCP Servers** > **Manage MCP Servers** > **View raw config**. No CLI, `/mcp` mostra o status e recarrega os servidores.",
    "O app do Gemini (gemini.google.com) aceita servidores por URL só nos Estados Unidos, para maiores de 18 anos, com conta Google pessoal e interface em inglês.",
    "O campo `httpUrl` do Gemini CLI não funciona no Antigravity.",
    "Não reaproveite a chave `url` do Gemini CLI. Use `serverUrl`.",
    "Para um projeto só, o arquivo é `.agents/mcp_config.json` dentro da pasta do projeto.",
  ],
  fontes: [
    {
      titulo: "Google Antigravity, Model Context Protocol (MCP)",
      url: "https://antigravity.google/docs/mcp",
    },
    {
      titulo: "Google, Connect & manage custom apps for Gemini Apps",
      url: "https://support.google.com/gemini/answer/17209137?hl=en&co=GENIE.Platform%3DDesktop",
    },
    {
      titulo: "Gemini CLI, discussão sobre a migração para o Antigravity",
      url: "https://github.com/google-gemini/gemini-cli/discussions/28017",
    },
    {
      titulo: "Digital Applied, Gemini CLI to Antigravity CLI migration",
      url: "https://www.digitalapplied.com/blog/gemini-cli-to-antigravity-cli-migration-june-18-2026-guide",
    },
  ],
};
