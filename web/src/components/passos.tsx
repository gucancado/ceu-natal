import { Badge } from "@beeads/ui";
import { Secao } from "@/components/secao";
import { site } from "@/lib/site";

type Passo = { titulo: string; frase: string; emBreve?: boolean };

const passos: Passo[] = [
  { titulo: "Conectar", frase: "Cole o endereço do servidor no seu assistente: leva 2 minutos." },
  { titulo: "Pedir", frase: "Escreva data, hora e cidade de nascimento como numa conversa." },
  {
    titulo: "Lembrar",
    frase: `Com conta, o ${site.nome} guarda as pessoas e as leituras para você não repetir dados.`,
    emBreve: true,
  },
];

export function Passos() {
  return (
    <Secao id="como-funciona" titulo="Em três passos">
      <ol className="grid max-w-[36rem] gap-8">
        {passos.map((p, i) => (
          <li key={p.titulo} className="grid grid-cols-[2.5rem_1fr] items-baseline">
            <span className="font-mono text-lg text-honey tabular" aria-hidden="true">
              {i + 1}
            </span>
            <div>
              <h3 className="flex flex-wrap items-center gap-3 font-display text-xl font-medium">
                {p.titulo}
                {p.emBreve ? (
                  <Badge variant="outline" className="border-border font-normal text-muted-fg">
                    Em breve
                  </Badge>
                ) : null}
              </h3>
              <p className="mt-1 text-muted-fg">{p.frase}</p>
            </div>
          </li>
        ))}
      </ol>
    </Secao>
  );
}
