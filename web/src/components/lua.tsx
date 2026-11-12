"use client";

import { useEffect, useRef } from "react";

// Foto da Lua na fase de agora (NASA, rota /lua-de-hoje), recortada no disco e opaca: tapa o Sol e as
// estrelas que passam atrás, inclusive na parte escura, como no céu de verdade. A travessia fica em
// globals.css: o invólucro anda na horizontal e a foto na vertical, o que desenha um arco. Se a foto
// falhar, a imagem quebrada com alt vazio não aparece.
//
// O tamanho do disco na foto muda com a distância da Lua (~39% a ~44% da largura). Um recorte fixo
// largo deixa um anel do fundo preto da foto, visível em monitor com bom contraste; por isso o raio é
// medido na própria foto e o recorte fica um pouco para dentro da borda.

const LIMIAR = 40; // brilho (0-255) que conta como disco iluminado
const FOLGA_PX = 2; // recua do limbo para não pegar o degradê da borda do JPEG
const RAIO_MIN = 0.36; // abaixo disso a medida falhou (perto da Lua nova): fica o recorte do CSS

/** Raio do disco como fração da largura: o maior alcance do limbo iluminado em 16 direções. */
function medirRaio(img: HTMLImageElement): number | null {
  const w = img.naturalWidth;
  const h = img.naturalHeight;
  if (!w || !h) return null;
  const canvas = document.createElement("canvas");
  canvas.width = w;
  canvas.height = h;
  const ctx = canvas.getContext("2d", { willReadFrequently: true });
  if (!ctx) return null;
  ctx.drawImage(img, 0, 0);
  const { data } = ctx.getImageData(0, 0, w, h);
  const cx = w / 2;
  const cy = h / 2;
  let maior = 0;
  for (let i = 0; i < 16; i++) {
    const a = (i / 16) * 2 * Math.PI;
    for (let r = Math.floor(Math.min(cx, cy)) - 1; r > maior; r--) {
      const x = Math.round(cx + r * Math.cos(a));
      const y = Math.round(cy + r * Math.sin(a));
      const p = (y * w + x) * 4;
      if ((data[p] + data[p + 1] + data[p + 2]) / 3 > LIMIAR) {
        maior = r;
        break;
      }
    }
  }
  const raio = (maior - FOLGA_PX) / w;
  return raio >= RAIO_MIN ? raio : null;
}

export function Lua({ className = "" }: { className?: string }) {
  const ref = useRef<HTMLImageElement>(null);

  useEffect(() => {
    const img = ref.current;
    if (!img) return;
    const aplicar = () => {
      try {
        const raio = medirRaio(img);
        if (raio) img.style.clipPath = `circle(${(raio * 100).toFixed(2)}%)`;
      } catch {
        // Sem canvas: fica o recorte do CSS.
      }
    };
    if (img.complete && img.naturalWidth) aplicar();
    else img.addEventListener("load", aplicar, { once: true });
    return () => img.removeEventListener("load", aplicar);
  }, []);

  return (
    <span aria-hidden="true" className={`lua ${className}`}>
      <span className="lua-arco">
        {/* eslint-disable-next-line @next/next/no-img-element */}
        <img
          ref={ref}
          src="/lua-de-hoje"
          alt=""
          width={730}
          height={730}
          decoding="async"
          className="lua-foto size-full"
        />
      </span>
    </span>
  );
}
