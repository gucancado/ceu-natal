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
    "Abra o Antigravity (app, IDE ou o CLI `agy`). Ele substituiu o Gemini CLI, que parou de atender contas individuais em junho de 2026.",
    "Abra o arquivo de configuração global `~/.gemini/config/mcp_config.json`. No IDE, o caminho até ele é o menu **…** do painel do Agent > **MCP Servers** > **Manage MCP Servers** > **View raw config**. No app, **Settings** > **Customizations** > **Installed MCP Servers** mostra os servidores instalados; para um servidor próprio, edite o arquivo de configuração direto.",
    "Cole o bloco abaixo e salve. O campo da URL é `serverUrl`.",
    "No CLI, `/mcp` abre o MCP Manager, que mostra o status e recarrega os servidores.",
  ],
  snippet: { linguagem: "json", codigo: JSON.stringify(config, null, 2) },
  limitacoes: [
    "O app do Gemini (gemini.google.com) aceita servidores por URL só nos Estados Unidos, para maiores de 18 anos, com conta Google pessoal e interface em inglês.",
    "O Antigravity só aceita Streamable HTTP. O endpoint SSE e o campo `httpUrl` do Gemini CLI não funcionam.",
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
