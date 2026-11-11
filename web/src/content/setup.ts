// Mês da última verificação dos guias de conexão (aviso dos guias e rodapé da página de cada cliente).
export const verificadoEm = "novembro de 2026";

// Prompt que a pessoa cola no próprio assistente para ele guiar a conexão.
import { site } from "../lib/site";

// Passos de conexão: também entram no prompt do mapa da home (lib/prompt-mapa.ts).
export const passosConexao = {
  chatgpt: `No ChatGPT: abra https://chatgpt.com/plugins, clique em Adicionar > Adicionar servidor MCP personalizado, coloque o nome ${site.nome}, cole o endereço, escolha Sem autenticação, marque Entendo e quero continuar, clique em Criar como plugin e depois em Conectar ${site.nome}.`,
  claude: `No Claude: abra https://claude.ai/customize/connectors, clique em + Add > Add custom connector, coloque o nome ${site.nome}, cole o endereço, escolha No sign in e clique em Add. Depois ligue o conector na conversa em + > Connectors.`,
  outros: `Nos outros aplicativos, os passos estão em ${site.url}/conectar.`,
};

export const promptSetup = [
  `Quero usar o ${site.nome} aqui. É um servidor MCP gratuito que calcula mapa astral com as efemérides suíças. Endereço: ${site.mcpEndpoint} (sem login e sem chave).`,
  "Se as ferramentas dele já estiverem disponíveis nesta conversa, pule direto para o cálculo do mapa.",
  "Se não, me passe numa única mensagem todos os passos para adicionar o conector, com o link direto e os valores prontos para copiar. Não divida em várias mensagens e só me pergunte qual aplicativo eu uso se não souber.",
  passosConexao.chatgpt,
  passosConexao.claude,
  passosConexao.outros,
  "Peça para eu responder feito quando terminar. Aí rode a ferramenta healthcheck e, na mesma resposta, peça numa única pergunta minha data, hora e cidade de nascimento. Com isso, calcule meu mapa natal com calcular_mapa_natal, me dê uma leitura curta e sugira o que mais posso pedir, como trânsitos, sinastria ou revolução solar.",
  `Se este aplicativo ou plano não permitir adicionar conectores, me diga isso e me mande para ${site.url}/mapa, onde faço o mapa sem conectar nada.`,
].join(" ");
