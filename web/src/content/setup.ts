// Prompt que a pessoa cola no próprio assistente para ele guiar a conexão.
import { site } from "../lib/site";

export const promptSetup = [
  `Quero usar o ${site.nome} aqui. É um servidor MCP gratuito que calcula mapa astral com as efemérides suíças.`,
  `Endereço: ${site.mcpEndpoint} (sem login e sem chave).`,
  "Se você não souber qual aplicativo e plano eu uso, pergunte. Depois me guie, um passo por vez, para adicionar esse conector aqui.",
  `O passo a passo de cada aplicativo está em ${site.url}/conectar.`,
  "Quando estiver conectado, rode a ferramenta healthcheck para confirmar.",
].join(" ");
