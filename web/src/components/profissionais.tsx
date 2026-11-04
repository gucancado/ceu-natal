import { Badge } from "@beeads/ui";
import { Secao } from "@/components/secao";
import { site } from "@/lib/site";

const assunto = encodeURIComponent(`${site.nome} para astrólogos`);

export function Profissionais() {
  return (
    <Secao id="profissionais" titulo="Para quem atende">
      <div className="max-w-[36rem] space-y-4 text-lg leading-[1.6]">
        <Badge variant="outline" className="border-border font-normal text-muted-fg">
          Em breve
        </Badge>
        <p>
          Antes da consulta, a ferramenta <span className="font-mono text-base">preparar_sessao</span>{" "}
          junta natal, trânsitos, progressões e revolução solar vigente numa chamada só.
        </p>
        <p>
          Você entrega ao cliente a roda do mapa em SVG ou PDF e um link de relatório, com o
          consentimento LGPD de cada cliente registrado.
        </p>
        <p>
          <a
            href={`mailto:${site.contato}?subject=${assunto}`}
            className="text-honey underline underline-offset-4"
          >
            Quero ser entrevistado como astrólogo parceiro
          </a>
        </p>
      </div>
    </Secao>
  );
}
