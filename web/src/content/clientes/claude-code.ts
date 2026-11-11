import { site } from "../../lib/site";
import type { Cliente } from "./tipos";

export const claudeCode: Cliente = {
  slug: "claude-code",
  nome: "Claude Code",
  resumo: "No Claude Code, um comando no terminal adiciona o Céu Natal para todos os seus projetos.",
  planoMinimo: "Qualquer conta que use o Claude Code.",
  semLogin: true,
  confianca: "alta",
  passos: ["Rode o comando abaixo no terminal.", "Confira com `claude mcp list`."],
  snippet: {
    linguagem: "bash",
    codigo: `claude mcp add --transport http --scope user ceu-natal ${site.mcpEndpoint}`,
  },
  limitacoes: [
    "A mensagem `Added ...` só confirma que a configuração foi gravada. Quem confirma a conexão é o `claude mcp list`.",
    "Sem `--scope user`, o servidor só vale na pasta onde você rodou o comando.",
  ],
  fontes: [
    {
      titulo: "Claude Code Docs, Connect Claude Code to tools via MCP",
      url: "https://code.claude.com/docs/en/mcp",
    },
  ],
};
