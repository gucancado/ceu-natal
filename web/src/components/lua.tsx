// Foto da Lua na fase de agora (NASA, rota /lua-de-hoje). O fundo preto da foto some com mix-blend-mode:
// screen sobre o céu, e a parte escura da Lua fica invisível, como no céu de verdade. A travessia fica em
// globals.css (.lua). Se a foto falhar, a imagem quebrada com alt vazio não aparece.
export function Lua({ className = "" }: { className?: string }) {
  return (
    // eslint-disable-next-line @next/next/no-img-element
    <img src="/lua-de-hoje" alt="" aria-hidden="true" width={730} height={730} decoding="async" className={`lua ${className}`} />
  );
}
