import type { CSSProperties } from "react";
import { mapaHero, type LinhaMapa } from "@/content/mapa-hero";
import { site } from "@/lib/site";

// "13°49' Gêmeos" vira grau "13°49'" e signo "Gêmeos".
function angulo(corpo: string, valor: string): LinhaMapa {
  const [grau, ...signo] = valor.split(" ");
  return { glifo: "", corpo, signo: signo.join(" "), grau, casa: null, retrogrado: false };
}

// "21/04/1960, 09:30, Brasília, DF" vira "21/04/1960, 09:30".
const dataHora = mapaHero.nascimento.split(", ").slice(0, 2).join(", ");

const celula = "px-1 py-1.5 sm:px-3";

function revelar(i: number): CSSProperties {
  return {
    "--i": i,
    animation: "aparecer .4s ease-out calc(var(--i) * 60ms) both",
  } as CSSProperties;
}

export function TabelaEfemeride() {
  const angulos = [
    angulo("Ascendente", mapaHero.angulos.ascendente),
    angulo("Meio do Céu", mapaHero.angulos.meioDoCeu),
  ];
  const n = mapaHero.linhas.length;

  return (
    <table className="w-full border-collapse text-left text-sm sm:text-base">
      <caption className="caption-bottom pt-4 text-left font-display text-sm italic text-muted-fg">
        Mapa calculado pelo {site.nome}: {mapaHero.titulo}, {dataHora}
      </caption>
      <thead>
        <tr className="border-b border-border text-sm text-muted-fg">
          <th scope="col" className={`${celula} w-8 font-normal`}>
            <span className="sr-only">Símbolo</span>
          </th>
          <th scope="col" className={`${celula} font-normal`}>Corpo</th>
          <th scope="col" className={`${celula} font-normal`}>Signo</th>
          <th scope="col" className={`${celula} text-right font-normal`}>Grau</th>
          <th scope="col" className={`${celula} text-right font-normal`}>Casa</th>
        </tr>
      </thead>
      <tbody>
        {mapaHero.linhas.map((l, i) => (
          <tr key={l.corpo} style={revelar(i)}>
            <td className={`${celula} text-lg leading-none`} aria-hidden="true">
              {l.glifo}
            </td>
            <td className={celula}>{l.corpo}</td>
            <td className={celula}>{l.signo}</td>
            <td className={`${celula} whitespace-nowrap text-right font-mono tabular`}>
              {l.grau}
              <span className="inline-block w-4 text-left">
                {l.retrogrado ? (
                  <span className="ml-0.5 text-honey" title="Retrógrado">
                    ℞<span className="sr-only"> retrógrado</span>
                  </span>
                ) : null}
              </span>
            </td>
            <td className={`${celula} text-right font-mono tabular`}>{l.casa ?? ""}</td>
          </tr>
        ))}
        {angulos.map((l, i) => (
          <tr
            key={l.corpo}
            style={revelar(n + i)}
            className={i === 0 ? "border-t border-border" : undefined}
          >
            <td className={celula} />
            <td className={`${celula} whitespace-nowrap`}>{l.corpo}</td>
            <td className={celula}>{l.signo}</td>
            <td className={`${celula} whitespace-nowrap text-right font-mono tabular`}>
              {l.grau}
              <span className="inline-block w-4" />
            </td>
            <td className={celula} />
          </tr>
        ))}
      </tbody>
    </table>
  );
}
