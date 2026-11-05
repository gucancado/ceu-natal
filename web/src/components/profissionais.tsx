import { Badge } from "@beeads/ui";
import { Secao } from "@/components/secao";
import { planeta } from "@/lib/glifos";
import { contato, site } from "@/lib/site";

const assunto = `${site.nome} para astrólogos`;

export function Profissionais() {
  return (
    <Secao id="profissionais" titulo="se você é astrólogo" simbolo={planeta.sol}>
      <div className="max-w-[36rem] space-y-4 text-lg leading-[1.6]">
        <Badge variant="outline" className="border-border font-normal text-muted-fg">
          Em breve
        </Badge>
        <p>
          estou preparando uma coisa pra quem atende. antes da consulta, a ferramenta{" "}
          <span className="font-mono text-base">preparar_sessao</span> junta natal, trânsitos, progressões e
          revolução solar vigente numa chamada só.
        </p>
        <p>
          você entrega ao cliente a roda do mapa em svg ou pdf e um link de relatório, cada cliente com o
          consentimento lgpd registrado.
        </p>
        <p>
          <a
            href={`mailto:${contato.email}?subject=${encodeURIComponent(assunto)}`}
            className="text-honey underline underline-offset-4"
          >
            me escreve, quero ouvir como você trabalha
          </a>
        </p>
      </div>
    </Secao>
  );
}
