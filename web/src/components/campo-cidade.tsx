"use client";

import { useId, useState, type KeyboardEvent } from "react";
import { Input } from "@/components/ui/input";
import { rotuloCidade, sugerirCidades, type Municipio } from "@/lib/cidades";

// A lista só é baixada quando a pessoa entra no campo, e uma vez por página.
let carregando: Promise<Municipio[]> | null = null;
function municipios(): Promise<Municipio[]> {
  carregando ??= fetch("/municipios.json")
    .then((r) => (r.ok ? r.json() : []))
    .catch(() => {
      carregando = null;
      return [];
    });
  return carregando;
}

type Props = {
  id: string;
  valor: string;
  aoMudar: (texto: string) => void;
  /** Cidade pronta para o cálculo: escolhida na lista, ou digitada e confirmada com Enter ou saindo do campo. */
  aoConfirmar: (cidade: string) => void;
};

// Combobox (padrão ARIA): setas escolhem, Enter confirma, Esc fecha.
export function CampoCidade({ id, valor, aoMudar, aoConfirmar }: Props) {
  const [lista, setLista] = useState<Municipio[]>([]);
  const [opcoes, setOpcoes] = useState<Municipio[]>([]);
  const [ativa, setAtiva] = useState(-1);
  const idLista = useId();
  const aberta = opcoes.length > 0;

  function escolher(m: Municipio) {
    const texto = rotuloCidade(m);
    aoMudar(texto);
    aoConfirmar(texto);
    setOpcoes([]);
    setAtiva(-1);
  }

  function digitar(texto: string) {
    aoMudar(texto);
    aoConfirmar("");
    setOpcoes(sugerirCidades(lista, texto));
    setAtiva(-1);
  }

  function tecla(e: KeyboardEvent<HTMLInputElement>) {
    if (e.key === "ArrowDown" && aberta) {
      e.preventDefault();
      setAtiva((i) => (i + 1) % opcoes.length);
    } else if (e.key === "ArrowUp" && aberta) {
      e.preventDefault();
      setAtiva((i) => (i <= 0 ? opcoes.length - 1 : i - 1));
    } else if (e.key === "Enter") {
      e.preventDefault();
      if (aberta) escolher(opcoes[Math.max(ativa, 0)]);
      else if (valor.trim().length >= 3) aoConfirmar(valor.trim());
    } else if (e.key === "Escape") {
      setOpcoes([]);
    }
  }

  return (
    <div className="relative">
      <Input
        id={id}
        role="combobox"
        aria-autocomplete="list"
        aria-expanded={aberta}
        aria-controls={idLista}
        aria-activedescendant={ativa >= 0 ? `${idLista}-${ativa}` : undefined}
        placeholder="digite sua cidade"
        className="campo-dica"
        maxLength={120}
        autoComplete="off"
        value={valor}
        onFocus={(e) => {
          const campo = e.currentTarget;
          municipios().then((l) => {
            setLista(l);
            // A pessoa pode ter digitado enquanto a lista baixava: sugere com o texto de agora.
            if (document.activeElement === campo && campo.value) setOpcoes(sugerirCidades(l, campo.value));
          });
        }}
        onChange={(e) => digitar(e.target.value)}
        onKeyDown={tecla}
        onBlur={() => {
          setOpcoes([]);
          if (valor.trim().length >= 3) aoConfirmar(valor.trim());
        }}
      />
      <ul
        id={idLista}
        role="listbox"
        aria-label="cidades"
        className={aberta ? "absolute inset-x-0 top-full z-20 mt-1 overflow-hidden rounded-md border border-border bg-muted shadow-lg" : "hidden"}
      >
        {opcoes.map((m, i) => (
          <li
            key={rotuloCidade(m)}
            id={`${idLista}-${i}`}
            role="option"
            aria-selected={i === ativa}
            // mousedown, e não click: o click viria depois do blur, que fecha a lista.
            onMouseDown={(e) => {
              e.preventDefault();
              escolher(m);
            }}
            onMouseEnter={() => setAtiva(i)}
            className={`cursor-pointer px-3 py-2 text-sm ${i === ativa ? "bg-bg text-honey" : ""}`}
          >
            {m[0]}, <span className="uppercase">{m[1]}</span>
          </li>
        ))}
      </ul>
    </div>
  );
}
