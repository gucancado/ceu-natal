// Foto do Sol de hoje (NASA SDO, rota /sol-de-hoje), do tamanho de uma estrela, mais lenta que a Lua, atrás dela. Mesma
// travessia em arco (globals.css, .sol); o recorte circular tira a legenda que a NASA grava no canto.
export function Sol({ className = "" }: { className?: string }) {
  return (
    <span aria-hidden="true" className={`sol ${className}`}>
      {/* eslint-disable-next-line @next/next/no-img-element */}
      <img src="/sol-de-hoje" alt="" width={512} height={512} decoding="async" className="sol-foto size-full" />
    </span>
  );
}
