"use client";

import Link from "next/link";
import { useEffect, useId, useRef, useState, type ChangeEvent, type FormEvent, type RefObject } from "react";
import { Copiar } from "@/components/copiar";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { CampoCidade } from "@/components/campo-cidade";
import { glifoPonto } from "@/lib/glifos";
import type { MapaRapido } from "@/lib/mapa-texto";
import { promptMapa } from "@/lib/prompt-mapa";
import { dataValida, signoSolar } from "@/lib/signo-solar";
import { site } from "@/lib/site";

const TEMPO_MAX_MS = 15000;
// Pausa antes do cálculo completo, para não calcular a cada dígito da hora.
const PAUSA_MS = 500;

const so = (s: string, max: number) => s.replace(/\D/g, "").slice(0, max);

type Pedido = { data: string; hora?: string; local?: string };
type Resposta = { mapa: MapaRapido } | { erro: string };

// `sinal` cancela quando os dados mudam (aí a promessa rejeita); o tempo máximo vira mensagem de erro.
async function pedirMapa(corpo: Pedido, sinal: AbortSignal): Promise<Resposta> {
  const ctrl = new AbortController();
  const parar = () => ctrl.abort();
  sinal.addEventListener("abort", parar);
  const limite = setTimeout(parar, TEMPO_MAX_MS);
  try {
    const r = await fetch(`${site.mcpUrl}/mapa-rapido`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(corpo),
      signal: ctrl.signal,
    });
    const json = await r.json().catch(() => null);
    if (!r.ok || !json || json.erro) return { erro: json?.erro || "Não foi possível calcular agora. Tente de novo." };
    return { mapa: json as MapaRapido };
  } catch (e) {
    if (sinal.aborted) throw e;
    return {
      erro: ctrl.signal.aborted
        ? "O servidor demorou demais. Tente de novo."
        : "Sem conexão com o servidor. Tente de novo em instantes.",
    };
  } finally {
    clearTimeout(limite);
    sinal.removeEventListener("abort", parar);
  }
}

function CampoNumero({
  id,
  rotulo,
  valor,
  max,
  placeholder,
  aoMudar,
  campoRef,
  proximo,
  autoComplete,
}: {
  id: string;
  rotulo: string;
  valor: string;
  max: number;
  placeholder: string;
  aoMudar: (v: string) => void;
  campoRef?: RefObject<HTMLInputElement | null>;
  proximo?: RefObject<HTMLInputElement | null>;
  autoComplete: string;
}) {
  function mudar(e: ChangeEvent<HTMLInputElement>) {
    const v = so(e.target.value, max);
    aoMudar(v);
    if (v.length === max) proximo?.current?.focus();
  }
  return (
    <div className="grid gap-2">
      <Label htmlFor={id}>{rotulo}</Label>
      <Input
        ref={campoRef}
        id={id}
        inputMode="numeric"
        autoComplete={autoComplete}
        placeholder={placeholder}
        maxLength={max}
        value={valor}
        onChange={mudar}
        className="tabular campo-dica"
      />
    </div>
  );
}

// Linha do prompt na tela: o símbolo do ponto (☉, ☽, AC…) sai colorido; o texto copiado é o mesmo.
const SIMBOLOS = new Set(Object.values(glifoPonto));

function LinhaPrompt({ texto }: { texto: string }) {
  const m = /^- (\S+) (\*\*.*)$/.exec(texto);
  if (m && SIMBOLOS.has(m[1])) {
    return (
      <div className="revelar">
        {"- "}
        <span className="glifo uppercase text-honey">{m[1]}</span> {m[2]}
      </div>
    );
  }
  return <div className="revelar">{texto || " "}</div>;
}

export function MapaProgressivo() {
  const [dia, setDia] = useState("");
  const [mes, setMes] = useState("");
  const [ano, setAno] = useState("");
  const [hora, setHora] = useState("");
  const [cidade, setCidade] = useState("");
  // Cidade que vai para o cálculo: escolhida na lista ou confirmada (Enter ou saindo do campo).
  const [cidadeOk, setCidadeOk] = useState("");
  const [doDia, setDoDia] = useState<{ chave: string; mapa: MapaRapido } | null>(null);
  const [completo, setCompleto] = useState<{ chave: string; mapa: MapaRapido } | null>(null);
  const [erro, setErro] = useState<string | null>(null);
  const [calculando, setCalculando] = useState(false);
  const cache = useRef(new Map<string, MapaRapido>());
  const refMes = useRef<HTMLInputElement>(null);
  const refAno = useRef<HTMLInputElement>(null);
  const refHora = useRef<HTMLInputElement>(null);
  const idPrompt = useId();

  const d = Number(dia);
  const m = Number(mes);
  const a = Number(ano);
  const sol = dia && mes ? signoSolar(d, m) : null;
  const dataOk = ano.length === 4 && dataValida(d, m, a);
  const dataBr = dataOk ? `${dia.padStart(2, "0")}/${mes.padStart(2, "0")}/${ano}` : "";
  const chaveDia = dataOk ? dataBr : "";
  const chaveCompleta = dataOk && hora && cidadeOk ? `${dataBr}|${hora}|${cidadeOk.toLowerCase()}` : "";

  // Só a data: planetas sem casas.
  useEffect(() => {
    if (!chaveDia) return;
    const guardado = cache.current.get(chaveDia);
    if (guardado) {
      setDoDia({ chave: chaveDia, mapa: guardado });
      return;
    }
    const ctrl = new AbortController();
    setCalculando(true);
    pedirMapa({ data: chaveDia }, ctrl.signal)
      .then((r) => {
        if ("mapa" in r) {
          cache.current.set(chaveDia, r.mapa);
          setDoDia({ chave: chaveDia, mapa: r.mapa });
          setErro(null);
        } else setErro(r.erro);
        setCalculando(false);
      })
      .catch(() => {});
    return () => {
      ctrl.abort();
      setCalculando(false);
    };
  }, [chaveDia]);

  // Data, hora e cidade confirmada: o mapa completo.
  useEffect(() => {
    if (!chaveCompleta) return;
    const guardado = cache.current.get(chaveCompleta);
    if (guardado) {
      setCompleto({ chave: chaveCompleta, mapa: guardado });
      return;
    }
    const ctrl = new AbortController();
    // Pausa curta: a hora muda a cada dígito digitado no campo de horário.
    const t = setTimeout(() => {
      setCalculando(true);
      pedirMapa({ data: dataBr, hora, local: cidadeOk }, ctrl.signal)
        .then((r) => {
          if ("mapa" in r) {
            cache.current.set(chaveCompleta, r.mapa);
            setCompleto({ chave: chaveCompleta, mapa: r.mapa });
            setErro(null);
          } else setErro(r.erro);
          setCalculando(false);
        })
        .catch(() => {});
    }, PAUSA_MS);
    return () => {
      clearTimeout(t);
      ctrl.abort();
      setCalculando(false);
    };
  }, [chaveCompleta, dataBr, hora, cidadeOk]);

  // Só vale o resultado que bate com os dados de agora.
  const mapaDia = doDia && doDia.chave === chaveDia ? doDia.mapa : null;
  const mapaCompleto = completo && completo.chave === chaveCompleta ? completo.mapa : null;

  const comecou = [dia, mes, ano, hora, cidade].some(Boolean);
  const prompt = promptMapa({ dia, mes, ano, hora, cidade: cidadeOk || cidade, solPelaData: sol, mapa: mapaCompleto ?? mapaDia });
  // Chave estável por linha: só a linha nova ou mudada entra com fade.
  const vistas = new Map<string, number>();
  const linhas = prompt.split("\n").map((texto) => {
    const n = (vistas.get(texto) ?? 0) + 1;
    vistas.set(texto, n);
    return { texto, chave: `${texto}#${n}` };
  });
  const dica =
    dia && mes && !sol
      ? "confira o dia e o mês."
      : ano.length === 4 && !dataOk
        ? "confira o ano: vale de 1800 a 2100."
        : hora && !cidadeOk && dataOk
          ? "escolha a cidade na lista para sair o ascendente."
          : null;

  return (
    <div className="grid gap-12">
      <form onSubmit={(e) => e.preventDefault()} className="grid max-w-[30rem] content-start gap-6">
        <fieldset className="grid gap-3">
          <legend className="mb-3 text-lg">quando você nasceu?</legend>
          <div className="grid grid-cols-[4.5rem_4.5rem_6rem] gap-3">
            <CampoNumero id="nasc-dia" rotulo="dia" valor={dia} max={2} placeholder="dd" aoMudar={setDia} proximo={refMes} autoComplete="bday-day" />
            <CampoNumero id="nasc-mes" rotulo="mês" valor={mes} max={2} placeholder="mm" aoMudar={setMes} campoRef={refMes} proximo={refAno} autoComplete="bday-month" />
            <CampoNumero id="nasc-ano" rotulo="ano" valor={ano} max={4} placeholder="aaaa" aoMudar={setAno} campoRef={refAno} proximo={refHora} autoComplete="bday-year" />
          </div>
        </fieldset>
        <div className="grid grid-cols-[8rem_1fr] gap-3">
          <div className="grid gap-2">
            <Label htmlFor="nasc-hora">hora</Label>
            <Input ref={refHora} id="nasc-hora" type="time" value={hora} onChange={(e) => setHora(e.target.value)} />
          </div>
          <div className="grid gap-2">
            <Label htmlFor="nasc-cidade">cidade</Label>
            <CampoCidade id="nasc-cidade" valor={cidade} aoMudar={setCidade} aoConfirmar={setCidadeOk} />
          </div>
        </div>
        <p aria-live="polite" className="min-h-[1.5em] text-sm text-muted-fg">
          {erro ? <span className="text-fg">{erro}</span> : calculando ? "calculando…" : dica}
        </p>
      </form>

      {comecou ? (
        <div className="revelar grid max-w-[52rem] gap-4">
          <p className="text-lg">copie e cole na sua ia. o mapa calculado já vai dentro do pedido.</p>
          <div className="relative rounded-md bg-card">
            <div className="absolute right-3 top-3 z-10">
              <Copiar texto={prompt} rotulo="copiar prompt" copiado="copiado" variant="default" size="sm" alvoId={idPrompt} />
            </div>
            <div
              id={idPrompt}
              tabIndex={0}
              aria-label="prompt com o seu mapa"
              className="texto-literal max-h-[30rem] overflow-y-auto whitespace-pre-wrap p-4 pt-14 font-mono text-sm leading-[1.6] [overflow-wrap:anywhere]"
            >
              {linhas.map((l) => (
                <LinhaPrompt key={l.chave} texto={l.texto} />
              ))}
            </div>
          </div>
        </div>
      ) : null}

      <FormContato />
    </div>
  );
}


type EstadoContato = { tipo: "vazio" } | { tipo: "enviando" } | { tipo: "ok" } | { tipo: "erro"; mensagem: string };

function FormContato() {
  const [valor, setValor] = useState("");
  const [estado, setEstado] = useState<EstadoContato>({ tipo: "vazio" });

  async function enviar(e: FormEvent<HTMLFormElement>) {
    e.preventDefault();
    if (!valor.trim()) return;
    setEstado({ tipo: "enviando" });
    try {
      const r = await fetch(`${site.mcpUrl}/contato`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ contato: valor.trim() }),
        signal: AbortSignal.timeout(TEMPO_MAX_MS),
      });
      const json = await r.json().catch(() => null);
      if (!r.ok || !json?.ok) {
        setEstado({ tipo: "erro", mensagem: json?.erro || "Não consegui guardar agora. Tente de novo." });
        return;
      }
      setEstado({ tipo: "ok" });
      setValor("");
    } catch {
      setEstado({ tipo: "erro", mensagem: "Sem conexão com o servidor. Tente de novo em instantes." });
    }
  }

  return (
    <form onSubmit={enviar} className="grid max-w-[30rem] gap-3">
      <Label htmlFor="contato" className="leading-[1.5]">
        vou continuar desenvolvendo, então se quiser receber atualizações, deixe aqui seu telefone ou e-mail
      </Label>
      <div className="flex gap-3">
        <Input
          id="contato"
          type="text"
          autoComplete="email"
          placeholder="telefone ou e-mail"
          className="campo-dica"
          maxLength={254}
          value={valor}
          onChange={(e) => setValor(e.target.value)}
        />
        <Button type="submit" variant="outline" disabled={estado.tipo === "enviando"}>
          {estado.tipo === "enviando" ? "enviando…" : "quero receber"}
        </Button>
      </div>
      <p aria-live="polite" className="text-sm text-muted-fg">
        {estado.tipo === "ok" ? (
          <span className="text-fg">anotado. obrigado =]</span>
        ) : estado.tipo === "erro" ? (
          <span className="text-fg">{estado.mensagem}</span>
        ) : (
          <Link href="/privacidade" className="underline underline-offset-4 hover:text-fg">
            privacidade
          </Link>
        )}
      </p>
    </form>
  );
}
