# Política de privacidade — Céu Natal

Versão 8 — 2026-11-12 — vale para o serviço gratuito sem conta; será revista quando houver contas

Este texto explica, em linguagem simples, o que o Céu Natal (o servidor MCP e
o site) faz com os seus dados. O serviço fica em https://astrologia-mcp.gustavocancado.com.br; o site, em https://mistico.gustavocancado.com.br.

## 1. Quem é o controlador

Quem decide como os dados são tratados (o "controlador", na LGPD) é:

- **Gustavo Cançado**, pessoa física, Belo Horizonte/MG.
- Contato: pelos canais em https://gustavocancado.com.br

## 2. O que o serviço faz com os dados que o seu assistente de IA envia

Quando você pede um mapa, o seu assistente de IA envia ao servidor a data, a
hora e a cidade de nascimento (e, em alguns casos, datas para trânsitos ou
revoluções).

- Esses dados são usados **só para calcular a resposta**.
- Eles **não são armazenados**. Cada pedido é calculado e esquecido.
- O serviço não tem conta, login nem cadastro. Para calcular, não pedimos
  nome, e-mail nem telefone.

## 3. Mapas feitos nos formulários do site

Os formulários do site (mapa natal, trânsitos, sinastria e revolução solar)
são diferentes: ali **os seus dados de nascimento ficam guardados**.

- O que fica guardado: data, hora e cidade de nascimento que você digitou, as
  coordenadas e o fuso da cidade (no mapa natal), e quando o mapa foi feito e
  atualizado.
- Na sinastria, os dados da outra pessoa são usados só para o cálculo e
  **não ficam guardados**. A data do trânsito, o ano e a cidade da revolução
  solar também não.
- O formulário não pede nome, e-mail nem conta. Para saber que vários mapas
  vieram do mesmo navegador, o site cria um código aleatório e o guarda no
  armazenamento local do seu navegador (`localStorage`). Esse código vai junto
  com cada mapa. Ele não identifica você sozinho, e você pode apagá-lo
  limpando os dados do site no navegador.
- O mapa feito só com a data e completado depois com hora e cidade é um mapa
  só; fica guardada a versão mais recente.
- Uso esses dados para entender como o Céu Natal é usado e para melhorá-lo.
  Eles não são vendidos nem compartilhados. A base legal é o legítimo
  interesse (LGPD, art. 7º, IX); você pode pedir para apagar a qualquer
  momento (seção 7).
- Eles ficam guardados até você pedir para apagar ou até o projeto acabar.

Para limitar abusos, o servidor conta os pedidos por endereço IP só na
memória, por alguns minutos; o IP não vai para os logs nem para o histórico de
mapas.

**Contato para novidades (opcional).** Na página inicial, você pode deixar um
e-mail ou um telefone para receber novidades do Céu Natal. Só faz isso quem
quiser, e o mapa funciona sem ele.

- O contato fica guardado com a data do cadastro e **fica ligado aos mapas
  que você fez no site** naquele navegador, antes ou depois de deixar o
  contato. Assim dá para saber quais mapas são seus.
- Uso o contato só para avisar novidades do Céu Natal e para entender o uso
  do site. Ele não é vendido nem compartilhado.
- A base legal é o seu consentimento (LGPD, art. 7º, I), dado ao deixar o
  contato. Para tirar o seu contato e os mapas ligados a ele, peça pelos
  canais em https://gustavocancado.com.br, e eles são apagados.
- O contato fica guardado até você pedir para tirar ou até o projeto acabar.

## 4. O que fica guardado

- **Cache de coordenadas.** Guardamos o nome de uma cidade e sua latitude,
  longitude e fuso horário, para não consultar de novo as bases de geocodificação.
  Isso não tem dado pessoal.
- **Logs do servidor.** Cada chamada registra o nome da ferramenta, o status e a
  duração. Quando a chamada traz uma cidade, o log também registra o nome da
  cidade, o país e se a coordenada veio do cache. Data e hora de nascimento
  nunca são registradas, e não há identificador de sessão nos logs. Os logs
  ficam guardados por no máximo **90 dias**. O contato para novidades não vai
  para os logs.
- **Estatísticas de uso.** Contagens por dia: quantas chamadas cada
  ferramenta recebeu, de qual app de IA (o nome que o app informa ao
  conectar), com qual resultado e em quanto tempo; quantos cálculos por país;
  e quantas cidades diferentes já foram calculadas. Para contar pessoas
  únicas por dia, o servidor guarda um resumo criptográfico (hash) do IP de
  quem usa o site, ou do identificador da conversa no MCP, misturado a um
  valor aleatório que vale só naquele dia. Ao virar o dia, os resumos e o
  valor aleatório são apagados e sobra só o número; não dá para voltar do
  resumo ao IP. Os totais, sem nomes de cidade, aparecem na página de
  status do site.
- **Mapas do site.** Data, hora, cidade e coordenadas de cada mapa feito no
  formulário do site, com o código aleatório do navegador (seção 3).
- **Contatos para novidades.** E-mail ou telefone e a data do cadastro, só de
  quem deixou o contato no site, ligados aos códigos dos navegadores em que a
  pessoa fez mapas (seção 3).
- **Cookies.** Não usamos nenhum. O site usa o armazenamento local do
  navegador só para o código aleatório descrito na seção 3.

## 5. Terceiros

- **GeoNames** e **Nominatim/OpenStreetMap** recebem apenas o nome da cidade,
  para descobrir as coordenadas.
- **Hetzner Cloud** hospeda o servidor.
- **O seu assistente de IA** (Anthropic, OpenAI, Google ou outro) tem política
  própria. É ele que guarda a sua conversa, incluindo o que você escreveu e o
  mapa devolvido. Consulte a política do assistente que você usa.

## 6. Transferência internacional

O servidor fica em Hillsboro, Oregon, nos Estados Unidos. Como os dados passam
por lá, há transferência internacional de dados (LGPD, art. 33). Na prática,
os dados de nascimento que chegam pelo assistente de IA só existem na
memória do servidor durante o cálculo e não ficam guardados. Os mapas feitos no
formulário do site e o contato para novidades, se você deixar, ficam guardados
lá.

## 7. Seus direitos

Pela LGPD, art. 18, você pode pedir:

- confirmação de que tratamos dados seus;
- acesso a esses dados;
- correção de dados incompletos, inexatos ou desatualizados;
- anonimização, bloqueio ou eliminação de dados desnecessários ou tratados em
  desacordo com a lei;
- portabilidade dos dados;
- informação sobre com quem os dados são compartilhados;
- revogação de consentimento, quando ele for a base do tratamento.

Para exercer qualquer direito, fale comigo pelos canais em https://gustavocancado.com.br. O que
pode estar guardado sobre você são os mapas que você fez no formulário do site
e o contato para novidades, se você o deixou. Pelo contato, encontro os mapas
ligados a ele. Para mapas feitos sem deixar contato, me diga a data, a hora e
a cidade que você digitou. Se não houver dado seu, responderemos explicando
isso.

## 8. Código aberto

O que roda no servidor é o código do repositório público, sob a licença
AGPL-3.0: https://github.com/gucancado/ceu-natal. Você pode conferir lá
exatamente o que é feito com os dados.

## 9. Mudanças nesta política

Se o serviço mudar (por exemplo, com a criação de contas), esta política será
revista e a versão e a data no topo serão atualizadas. Versões anteriores
ficam no histórico do repositório.
