import { Copiar } from "@/components/copiar";
import { Secao } from "@/components/secao";
import { prompts } from "@/content/prompts";

export function Prompts() {
  return (
    <Secao id="exemplos" titulo="Três pedidos para começar">
      <div className="grid gap-12 lg:grid-cols-3 lg:gap-10">
        {prompts.map((p) => (
          <figure key={p.titulo} className="flex flex-col items-start gap-4">
            <blockquote className="font-display text-xl italic leading-[1.5]">{p.texto}</blockquote>
            <figcaption className="font-mono text-sm text-muted-fg">usa {p.tool}</figcaption>
            <Copiar texto={p.texto} />
          </figure>
        ))}
      </div>
    </Secao>
  );
}
