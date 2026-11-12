"use client";

import { useEffect, useId, useRef, useState } from "react";
import { CampoCidade } from "@/components/campo-cidade";
import { Copiar } from "@/components/copiar";
import { CampoNumero, FormContato, LinhaPrompt } from "@/components/mapa-progressivo";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { criarIdsDeMapa, idVisitante } from "@/lib/identidade";
import {
  promptRevolucaoSolar,
  promptSinastria,
  promptTransitos,
  type Nascimento,
  type ResultadoRevolucao,
  type ResultadoSinastria,
  type ResultadoTransitos,
  type Tema,
} from "@/lib/prompt-tema";
import { dataValida } from "@/lib/signo-solar";
import { site } from "@/lib/site";

const TEMPO_MAX_MS = 15000;
// Pausa antes de calcular, para não pedir a cada dígito digitado.
const PAUSA_MS = 500;

const dois = (n: number) => String(n).padStart(2, "0");

function hojeBr(): string {
  const h = new Date();
  return `${dois(h.getDate())}/${dois(h.getMonth() + 1)}/${h.getFullYear()}`;
}

/** Ano da revolução que vale hoje: a do último aniversário. */
function anoDoUltimoAniversario(dia: number, mes: number): number {
  const h = new Date();
  const passou = h.getMonth() + 1 > mes || (h.getMonth() + 1 === mes && h.getDate() >= dia);
  return passou ? h.getFullYear() : h.getFullYear() - 1;
}

type Pessoa = {
  dia: string; mes: string; ano: string; hora: string; cidade: string; cidadeOk: string;
  set: { dia: (v: string) => void; mes: (v: string) => void; ano: (v: string) => void; hora: (v: string) => void; cidade: (v: string) => void; cidadeOk: (v: string) => void };
  dataBr: string;
  /** Campos que vão para o servidor: hora e cidade só quando as duas estão prontas. */
  corpo: { data: string; hora?: string; local?: string } | null;
  texto: Nascimento;
};

function usePessoa(): Pessoa {
  const [dia, setDia] = useState("");
  const [mes, setMes] = useState("");
  const [ano, setAno] = useState("");
  const [hora, setHora] = useState("");
  const [cidade, setCidade] = useState("");
  const [cidadeOk, setCidadeOk] = useState("");
  const dataOk = ano.length === 4 && dataValida(Number(dia), Number(mes), Number(ano));
  const dataBr = dataOk ? `${dia.padStart(2, "0")}/${mes.padStart(2, "0")}/${ano}` : "";
  const corpo = dataOk ? { data: dataBr, ...(hora && cidadeOk ? { hora, local: cidadeOk } : {}) } : null;
  return {
    dia, mes, ano, hora, cidade, cidadeOk,
    set: { dia: setDia, mes: setMes, ano: setAno, hora: setHora, cidade: setCidade, cidadeOk: setCidadeOk },
    dataBr,
    corpo,
    texto: { data: dataBr, hora, cidade: cidadeOk || cidade.trim() },
  };
}

function CamposPessoa({ p, prefixo, legenda }: { p: Pessoa; prefixo: string; legenda: string }) {
  const refMes = useRef<HTMLInputElement>(null);
  const refAno = useRef<HTMLInputElement>(null);
  const refHora = useRef<HTMLInputElement>(null);
  return (
    <fieldset className="grid gap-4">
      <legend className="mb-3 text-lg">{legenda}</legend>
      <div className="grid grid-cols-[4.5rem_4.5rem_6rem] gap-3">
        <CampoNumero id={`${prefixo}-dia`} rotulo="dia" valor={p.dia} max={2} placeholder="dd" aoMudar={p.set.dia} proximo={refMes} autoComplete="off" />
        <CampoNumero id={`${prefixo}-mes`} rotulo="mês" valor={p.mes} max={2} placeholder="mm" aoMudar={p.set.mes} campoRef={refMes} proximo={refAno} autoComplete="off" />
        <CampoNumero id={`${prefixo}-ano`} rotulo="ano" valor={p.ano} max={4} placeholder="aaaa" aoMudar={p.set.ano} campoRef={refAno} proximo={refHora} autoComplete="off" />
      </div>
      <div className="grid grid-cols-1 gap-3 sm:grid-cols-[8rem_1fr]">
        <div className="grid min-w-0 max-w-[10rem] gap-2 sm:max-w-none">
          <Label htmlFor={`${prefixo}-hora`}>hora</Label>
          <Input ref={refHora} id={`${prefixo}-hora`} type="time" value={p.hora} onChange={(e) => p.set.hora(e.target.value)} className="w-full min-w-0" />
        </div>
        <div className="grid min-w-0 gap-2">
          <Label htmlFor={`${prefixo}-cidade`}>cidade</Label>
          <CampoCidade id={`${prefixo}-cidade`} valor={p.cidade} aoMudar={p.set.cidade} aoConfirmar={p.set.cidadeOk} />
        </div>
      </div>
    </fieldset>
  );
}

// Um pedido por vez: dados novos cancelam o anterior; o resultado só vale para a chave que o pediu.
function useCalculo<T>(corpo: Record<string, unknown> | null) {
  const chave = corpo ? JSON.stringify(corpo) : "";
  const [resultado, setResultado] = useState<{ chave: string; dados: T } | null>(null);
  const [erro, setErro] = useState<string | null>(null);
  const [calculando, setCalculando] = useState(false);
  const cache = useRef(new Map<string, T>());

  useEffect(() => {
    if (!chave) return;
    const guardado = cache.current.get(chave);
    if (guardado) {
      setResultado({ chave, dados: guardado });
      return;
    }
    const ctrl = new AbortController();
    const limite = setTimeout(() => ctrl.abort(), TEMPO_MAX_MS + PAUSA_MS);
    const t = setTimeout(async () => {
      setCalculando(true);
      try {
        const r = await fetch(`${site.mcpUrl}/mapa-rapido`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: chave,
          signal: ctrl.signal,
        });
        const json = await r.json().catch(() => null);
        if (!r.ok || !json || json.erro) setErro(json?.erro || "Não foi possível calcular agora. Tente de novo.");
        else {
          cache.current.set(chave, json as T);
          setResultado({ chave, dados: json as T });
          setErro(null);
        }
      } catch {
        if (!ctrl.signal.aborted) setErro("Sem conexão com o servidor. Tente de novo em instantes.");
        else setErro("O servidor demorou demais. Tente de novo.");
      } finally {
        setCalculando(false);
      }
    }, PAUSA_MS);
    return () => {
      clearTimeout(t);
      clearTimeout(limite);
      ctrl.abort();
      setCalculando(false);
      setErro(null);
    };
  }, [chave]);

  return { dados: resultado && resultado.chave === chave ? resultado.dados : null, erro, calculando };
}

function CaixaPromptTema({ prompt, rotulo }: { prompt: string; rotulo: string }) {
  const id = useId();
  const vistas = new Map<string, number>();
  const linhas = prompt.split("\n").map((texto) => {
    const n = (vistas.get(texto) ?? 0) + 1;
    vistas.set(texto, n);
    return { texto, chave: `${texto}#${n}` };
  });
  return (
    <div className="revelar grid max-w-[52rem] gap-4">
      <p className="text-lg">copie e cole na sua ia. o cálculo já vai dentro do pedido.</p>
      <div className="relative rounded-md bg-card">
        <div className="absolute right-3 top-3 z-10">
          <Copiar texto={prompt} rotulo="copiar" copiado="copiado" variant="default" size="sm" alvoId={id} />
        </div>
        <div
          id={id}
          tabIndex={0}
          aria-label={rotulo}
          className="texto-literal max-h-[30rem] overflow-y-auto whitespace-pre-wrap p-4 pt-14 font-mono text-sm leading-[1.6] [overflow-wrap:anywhere]"
        >
          {linhas.map((l) => (
            <LinhaPrompt key={l.chave} texto={l.texto} />
          ))}
        </div>
      </div>
    </div>
  );
}

function Status({ erro, calculando, dica }: { erro: string | null; calculando: boolean; dica: string | null }) {
  return (
    <p aria-live="polite" className="min-h-[1.5em] text-sm text-muted-fg">
      {erro ? <span className="text-fg">{erro}</span> : calculando ? "calculando…" : dica}
    </p>
  );
}

function comecou(p: Pessoa) {
  return [p.dia, p.mes, p.ano, p.hora, p.cidade].some(Boolean);
}

function useIdMapa(p: Pessoa) {
  const ids = useRef(criarIdsDeMapa());
  return p.dataBr ? { mapa: ids.current(p.dataBr), visitante: idVisitante() } : {};
}

function FormTransitos() {
  const p = usePessoa();
  const [hoje] = useState(hojeBr);
  const ids = useIdMapa(p);
  // A tool de trânsitos exige hora e cidade de nascimento (casas natais).
  const completo = p.corpo && p.corpo.hora && p.corpo.local;
  const corpo = completo ? { tecnica: "transitos", ...p.corpo, data_transito: hoje, ...ids } : null;
  const { dados, erro, calculando } = useCalculo<ResultadoTransitos>(corpo);
  const dica = p.dataBr && !completo ? "os trânsitos precisam da hora e da cidade de nascimento." : null;
  return (
    <div className="grid gap-12">
      <form onSubmit={(e) => e.preventDefault()} className="grid max-w-[30rem] content-start gap-6">
        <CamposPessoa p={p} prefixo="tr" legenda="quando você nasceu?" />
        <Status erro={erro} calculando={calculando} dica={dica} />
      </form>
      {comecou(p) ? <CaixaPromptTema prompt={promptTransitos(p.texto, hoje, dados)} rotulo="prompt com os seus trânsitos" /> : null}
      <FormContato />
    </div>
  );
}

function FormSinastria() {
  const a = usePessoa();
  const b = usePessoa();
  const ids = useIdMapa(a);
  const corpo = a.corpo && b.corpo ? { tecnica: "sinastria", ...a.corpo, outra: b.corpo, ...ids } : null;
  const { dados, erro, calculando } = useCalculo<ResultadoSinastria>(corpo);
  const dica = a.corpo && !b.corpo ? "falta a data de nascimento da outra pessoa." : null;
  return (
    <div className="grid gap-12">
      <form onSubmit={(e) => e.preventDefault()} className="grid max-w-[60rem] content-start gap-10">
        <div className="grid gap-10 md:grid-cols-2">
          <CamposPessoa p={a} prefixo="sa" legenda="quando você nasceu?" />
          <CamposPessoa p={b} prefixo="sb" legenda="e a outra pessoa?" />
        </div>
        <Status erro={erro} calculando={calculando} dica={dica} />
      </form>
      {comecou(a) || comecou(b) ? (
        <CaixaPromptTema prompt={promptSinastria(a.texto, b.texto, dados)} rotulo="prompt com a sinastria" />
      ) : null}
      <FormContato />
    </div>
  );
}

function FormRevolucaoSolar() {
  const p = usePessoa();
  const [anoRev, setAnoRev] = useState("");
  const [cidadeAniv, setCidadeAniv] = useState("");
  const [cidadeAnivOk, setCidadeAnivOk] = useState("");
  const ids = useIdMapa(p);
  // Sem ano escolhido, vale o do último aniversário.
  const ano = anoRev.length === 4 ? anoRev : p.dia && p.mes ? String(anoDoUltimoAniversario(Number(p.dia), Number(p.mes))) : "";
  const completo = p.corpo && p.corpo.hora && p.corpo.local;
  const corpo = completo && ano
    ? { tecnica: "revolucao_solar", ...p.corpo, ano, ...(cidadeAnivOk ? { local_revolucao: cidadeAnivOk } : {}), ...ids }
    : null;
  const { dados, erro, calculando } = useCalculo<ResultadoRevolucao>(corpo);
  const dica = p.dataBr && !completo ? "a revolução solar precisa da hora e da cidade de nascimento." : null;
  return (
    <div className="grid gap-12">
      <form onSubmit={(e) => e.preventDefault()} className="grid max-w-[30rem] content-start gap-6">
        <CamposPessoa p={p} prefixo="rs" legenda="quando você nasceu?" />
        <fieldset className="grid gap-4">
          <legend className="mb-3 text-lg">qual aniversário?</legend>
          <div className="grid grid-cols-1 gap-3 sm:grid-cols-[8rem_1fr]">
            <div className="grid min-w-0 max-w-[10rem] gap-2 sm:max-w-none">
              <Label htmlFor="rs-ano-rev">ano</Label>
              <Input
                id="rs-ano-rev"
                inputMode="numeric"
                maxLength={4}
                placeholder={ano || "aaaa"}
                value={anoRev}
                onChange={(e) => setAnoRev(e.target.value.replace(/\D/g, "").slice(0, 4))}
                className="tabular campo-dica"
              />
            </div>
            <div className="grid min-w-0 gap-2">
              <Label htmlFor="rs-cidade-aniv">cidade do aniversário</Label>
              <CampoCidade id="rs-cidade-aniv" valor={cidadeAniv} aoMudar={setCidadeAniv} aoConfirmar={setCidadeAnivOk} />
            </div>
          </div>
          <p className="text-sm text-muted-fg">sem cidade, uso a de nascimento. ela muda o ascendente e as casas do ano.</p>
        </fieldset>
        <Status erro={erro} calculando={calculando} dica={dica} />
      </form>
      {comecou(p) ? (
        <CaixaPromptTema
          prompt={promptRevolucaoSolar(p.texto, ano, cidadeAnivOk || cidadeAniv.trim(), dados)}
          rotulo="prompt com a sua revolução solar"
        />
      ) : null}
      <FormContato />
    </div>
  );
}

export function FormTema({ tema }: { tema: Tema }) {
  if (tema === "transitos") return <FormTransitos />;
  if (tema === "sinastria") return <FormSinastria />;
  return <FormRevolucaoSolar />;
}
