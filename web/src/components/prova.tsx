const fatos = [
  "Efemérides suíças (NASA JPL)",
  "9 técnicas",
  "Em português",
  "Cidade brasileira geocodificada",
  "Código aberto, AGPL",
];

export function Prova() {
  return (
    <section aria-label="Em resumo" className="mx-auto max-w-[72rem] px-6">
      {/* overflow-hidden recorta o filete do primeiro item de cada linha quando a lista quebra no mobile */}
      <div className="overflow-hidden border-t border-border py-6">
        <ul className="-ml-[calc(1rem+1px)] flex flex-wrap gap-y-2 text-muted-fg">
          {fatos.map((f) => (
            <li key={f} className="border-l border-border px-4">
              {f}
            </li>
          ))}
        </ul>
      </div>
    </section>
  );
}
