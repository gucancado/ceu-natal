import type { CSSProperties } from "react";

// Só CSS, sem JavaScript no navegador. Períodos primos entre si: as cinco trajetórias não entram em ritmo
// repetido, e em média passa uma a cada 11 segundos. Com "reduzir movimento" ligado, nenhuma aparece.
const cadentes = [
  { top: "8%", left: "12%", angulo: "24deg", comprimento: "170px", distancia: "46vmax", periodo: "37s", atraso: "3s" },
  { top: "4%", left: "78%", angulo: "152deg", comprimento: "130px", distancia: "38vmax", periodo: "47s", atraso: "14s" },
  { top: "30%", left: "38%", angulo: "16deg", comprimento: "210px", distancia: "52vmax", periodo: "59s", atraso: "24s" },
  { top: "18%", left: "62%", angulo: "138deg", comprimento: "150px", distancia: "44vmax", periodo: "71s", atraso: "33s" },
  { top: "46%", left: "6%", angulo: "32deg", comprimento: "120px", distancia: "36vmax", periodo: "83s", atraso: "41s" },
];

export function EstrelasCadentes() {
  return (
    <div aria-hidden="true" className="estrelas-cadentes">
      {cadentes.map(({ top, left, angulo, comprimento, distancia, periodo, atraso }) => (
        <span
          key={periodo}
          className="estrela-cadente"
          style={
            {
              top,
              left,
              "--angulo": angulo,
              "--comprimento": comprimento,
              "--distancia": distancia,
              "--periodo": periodo,
              "--atraso": atraso,
            } as CSSProperties
          }
        />
      ))}
    </div>
  );
}
