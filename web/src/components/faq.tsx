import Link from "next/link";
import { Accordion, AccordionContent, AccordionItem, AccordionTrigger } from "@beeads/ui";
import { Secao } from "@/components/secao";
import { faq } from "@/content/faq";

const rotaPrivacidade = "/privacidade";

// A resposta de LGPD cita a rota no texto; aqui ela vira link.
function Resposta({ texto }: { texto: string }) {
  const partes = texto.split(rotaPrivacidade);
  return (
    <p>
      {partes.map((parte, i) => (
        <span key={i}>
          {parte}
          {i < partes.length - 1 ? (
            <Link href={rotaPrivacidade} className="text-honey underline underline-offset-4">
              {rotaPrivacidade}
            </Link>
          ) : null}
        </span>
      ))}
    </p>
  );
}

export function Faq() {
  return (
    <Secao id="faq" titulo="Perguntas frequentes">
      <Accordion className="max-w-[48rem] border-t border-border">
        {faq.map((f, i) => (
          <AccordionItem key={f.pergunta} value={`faq-${i}`}>
            <AccordionTrigger className="text-left font-display text-lg font-medium">
              {f.pergunta}
            </AccordionTrigger>
            <AccordionContent className="max-w-[36rem] text-base leading-[1.6] text-muted-fg">
              <Resposta texto={f.resposta} />
            </AccordionContent>
          </AccordionItem>
        ))}
      </Accordion>
    </Secao>
  );
}
