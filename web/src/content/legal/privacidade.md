# Política de privacidade — Céu Natal

Versão 3 — 2026-11-05 — vale para o serviço gratuito sem conta; será revista quando houver contas

Este texto explica, em linguagem simples, o que o servidor MCP do Céu Natal
faz com os seus dados. O serviço fica em https://astrologia-mcp.gustavocancado.com.br; o site, em https://mistico.gustavocancado.com.br.

## 1. Quem é o controlador

Quem decide como os dados são tratados (o "controlador", na LGPD) é:

- **Gustavo Cançado**, pessoa física, Belo Horizonte/MG.
- Contato: gustavo.azvd@gmail.com

## 2. O que o serviço faz com os dados que o seu assistente de IA envia

Quando você pede um mapa, o seu assistente de IA envia ao servidor a data, a
hora e a cidade de nascimento (e, em alguns casos, datas para trânsitos ou
revoluções).

- Esses dados são usados **só para calcular a resposta**.
- Eles **não são armazenados**. Cada pedido é calculado e esquecido.
- O serviço não tem conta, login nem cadastro. Não pedimos nome, e-mail nem
  telefone.

O formulário "mapa natal sem cadastro" do site envia os mesmos dados (data,
hora e cidade) direto do seu navegador para o servidor, com o mesmo
tratamento: o cálculo é feito, o resultado volta para a sua tela e nada é
guardado. Para limitar abusos, o servidor conta os pedidos por endereço IP
só na memória, por alguns minutos; o IP não vai para os logs.

## 3. O que fica guardado

- **Cache de coordenadas.** Guardamos o nome de uma cidade e sua latitude,
  longitude e fuso horário, para não consultar de novo as bases de geocodificação.
  Isso não tem dado pessoal.
- **Logs do servidor.** Cada chamada registra o nome da ferramenta, o status e a
  duração. Quando a chamada traz uma cidade, o log também registra o nome da
  cidade, o país e se a coordenada veio do cache. Data e hora de nascimento
  nunca são registradas, e não há identificador de sessão nos logs. Os logs
  ficam guardados por no máximo **90 dias**.
- **Cookies.** Não usamos nenhum.

## 4. Terceiros

- **GeoNames** e **Nominatim/OpenStreetMap** recebem apenas o nome da cidade,
  para descobrir as coordenadas.
- **Hetzner Cloud** hospeda o servidor.
- **O seu assistente de IA** (Anthropic, OpenAI, Google ou outro) tem política
  própria. É ele que guarda a sua conversa, incluindo o que você escreveu e o
  mapa devolvido. Consulte a política do assistente que você usa.

## 5. Transferência internacional

O servidor fica em Hillsboro, Oregon, nos Estados Unidos. Como os dados passam
por lá, há transferência internacional de dados (LGPD, art. 33). Na prática,
os dados de nascimento só existem na memória do servidor durante o cálculo e
não ficam guardados.

## 6. Seus direitos

Pela LGPD, art. 18, você pode pedir:

- confirmação de que tratamos dados seus;
- acesso a esses dados;
- correção de dados incompletos, inexatos ou desatualizados;
- anonimização, bloqueio ou eliminação de dados desnecessários ou tratados em
  desacordo com a lei;
- portabilidade dos dados;
- informação sobre com quem os dados são compartilhados;
- revogação de consentimento, quando ele for a base do tratamento.

Para exercer qualquer direito, escreva para gustavo.azvd@gmail.com. Como o
serviço não armazena dados de nascimento e não tem conta, talvez não haja
dado seu para localizar. Nesse caso, responderemos explicando isso.

## 7. Código aberto

O que roda no servidor é o código do repositório público, sob a licença
AGPL-3.0: https://github.com/gucancado/ceu-natal. Você pode conferir lá
exatamente o que é feito com os dados.

## 8. Mudanças nesta política

Se o serviço mudar (por exemplo, com a criação de contas), esta política será
revista e a versão e a data no topo serão atualizadas. Versões anteriores
ficam no histórico do repositório.
