"use client";

import Link from "next/link";
import { useEffect, useId, useRef, useState, type ChangeEvent, type FormEvent, type RefObject } from "react";
import { Copiar } from "@/components/copiar";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { planeta } from "@/lib/glifos";
import { nome, signo, type MapaRapido } from "@/lib/mapa-texto";
import { promptMapa } from "@/lib/prompt-mapa";
import { dataValida, signoSolar } from "@/lib/signo-solar";
import { site } from "@/lib/site";

const TEMPO_MAX_MS = 15000;
// A cidade só é enviada depois de uma pausa na digitação: cada envio gasta uma consulta de geocodificação.
const PAUSA_CIDADE_MS = 1000;

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

type Revelacao = { chave: string; glifo?: string; texto: string; nota?: string };

function posicao(m: MapaRapido, chave: string, comCasa: boolean): string | null {
  const p = m.planetas[chave] ?? m.angulos?.[chave];
  if (!p) return null;
  const casa = comCasa && typeof p.casa === "number" ? `, casa ${p.casa}` : "";
  return `${nome(chave)} em ${signo(p.signo)}, ${p.grau}${casa}${p.retrogrado ? ", retrógrado" : ""}`;
}

function revelacoes(
  sol: { signo: string; cuspide: boolean } | null,
  doDia: MapaRapido | null,
  completo: MapaRapido | null,
): Revelacao[] {
  const m = completo ?? doDia;
  const lista: Revelacao[] = [];
  if (!m) {
    if (sol)
      lista.push({
        chave: "sol-data",
        glifo: planeta.sol,
        texto: `seu sol está em ${sol.signo}`,
        nota: sol.cuspide ? "você nasceu na troca de signo: o ano confirma" : "com o ano, vem o grau exato",
      });
    return lista;
  }
  const casa = !!completo;
  lista.push({ chave: "sol", glifo: planeta.sol, texto: posicao(m, "sol", casa) ?? "" });
  lista.push({
    chave: "lua",
    glifo: planeta.lua,
    texto: posicao(m, "lua", casa) ?? "",
    nota: casa ? undefined : "sem a hora, a lua pode variar alguns graus",
  });
  if (completo?.angulos?.ascendente)
    lista.push({ chave: "asc", glifo: "↑", texto: posicao(completo, "ascendente", false) ?? "", nota: "é o signo que nascia no horizonte" });
  if (completo?.angulos?.meio_do_ceu) lista.push({ chave: "mc", glifo: "⊤", texto: posicao(completo, "meio_do_ceu", false) ?? "" });
  lista.push({ chave: "mercurio", glifo: planeta.mercurio, texto: posicao(m, "mercurio", casa) ?? "" });
  lista.push({ chave: "venus", glifo: planeta.venus, texto: posicao(m, "venus", casa) ?? "" });
  lista.push({ chave: "marte", glifo: planeta.marte, texto: posicao(m, "marte", casa) ?? "" });
  const aspectos = (m.aspectos ?? []).filter((a) => !(a.planeta_a.startsWith("nodo_") && a.planeta_b.startsWith("nodo_")));
  lista.push({
    chave: `outros-${casa}`,
    glifo: planeta.saturno,
    texto: `júpiter, saturno, urano, netuno, plutão e ${aspectos.length} aspectos calculados`,
    nota: casa ? "e as 12 casas" : "com hora e cidade, saem ascendente e casas",
  });
  return lista.filter((r) => r.texto);
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
        className="tabular"
      />
    </div>
  );
}

export function MapaProgressivo() {
  const [dia, setDia] = useState("");
  const [mes, setMes] = useState("");
  const [ano, setAno] = useState("");
  const [hora, setHora] = useState("");
  const [cidade, setCidade] = useState("");
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
  const local = cidade.trim();
  const chaveDia = dataOk ? dataBr : "";
  const chaveCompleta = dataOk && hora && local.length >= 3 ? `${dataBr}|${hora}|${local.toLowerCase()}` : "";

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

  // Data, hora e cidade: o mapa completo, depois de uma pausa na digitação.
  useEffect(() => {
    if (!chaveCompleta) return;
    const guardado = cache.current.get(chaveCompleta);
    if (guardado) {
      setCompleto({ chave: chaveCompleta, mapa: guardado });
      return;
    }
    const ctrl = new AbortController();
    const t = setTimeout(() => {
      setCalculando(true);
      pedirMapa({ data: dataBr, hora, local }, ctrl.signal)
        .then((r) => {
          if ("mapa" in r) {
            cache.current.set(chaveCompleta, r.mapa);
            setCompleto({ chave: chaveCompleta, mapa: r.mapa });
            setErro(null);
          } else setErro(r.erro);
          setCalculando(false);
        })
        .catch(() => {});
    }, PAUSA_CIDADE_MS);
    return () => {
      clearTimeout(t);
      ctrl.abort();
      setCalculando(false);
    };
  }, [chaveCompleta, dataBr, hora, local]);

  // Só vale o resultado que bate com os dados de agora.
  const mapaDia = doDia && doDia.chave === chaveDia ? doDia.mapa : null;
  const mapaCompleto = completo && completo.chave === chaveCompleta ? completo.mapa : null;
  const lista = revelacoes(sol, mapaDia, mapaCompleto);

  const comecou = [dia, mes, ano, hora, cidade].some(Boolean);
  const prompt = promptMapa({ dia, mes, ano, hora, cidade, solPelaData: sol, mapa: mapaCompleto ?? mapaDia });
  const dica =
    dia && mes && !sol
      ? "confira o dia e o mês."
      : ano.length === 4 && !dataOk
        ? "confira o ano: vale de 1800 a 2100."
        : hora && local.length < 3 && dataOk
          ? "com a cidade, sai o ascendente."
          : null;

  return (
    <div className="grid gap-12">
      <div className="grid gap-12 lg:grid-cols-12">
        <form onSubmit={(e) => e.preventDefault()} className="grid max-w-[30rem] content-start gap-6 lg:col-span-5">
          <fieldset className="grid gap-3">
            <legend className="mb-3 text-lg">quando você nasceu?</legend>
            <div className="grid grid-cols-[4.5rem_4.5rem_6rem] gap-3">
              <CampoNumero id="nasc-dia" rotulo="dia" valor={dia} max={2} placeholder="15" aoMudar={setDia} proximo={refMes} autoComplete="bday-day" />
              <CampoNumero id="nasc-mes" rotulo="mês" valor={mes} max={2} placeholder="05" aoMudar={setMes} campoRef={refMes} proximo={refAno} autoComplete="bday-month" />
              <CampoNumero id="nasc-ano" rotulo="ano" valor={ano} max={4} placeholder="1990" aoMudar={setAno} campoRef={refAno} proximo={refHora} autoComplete="bday-year" />
            </div>
          </fieldset>
          <div className="grid grid-cols-[8rem_1fr] gap-3">
            <div className="grid gap-2">
              <Label htmlFor="nasc-hora">hora</Label>
              <Input ref={refHora} id="nasc-hora" type="time" value={hora} onChange={(e) => setHora(e.target.value)} />
            </div>
            <div className="grid gap-2">
              <Label htmlFor="nasc-cidade">cidade</Label>
              <Input
                id="nasc-cidade"
                placeholder="belo horizonte, mg"
                maxLength={120}
                autoComplete="off"
                value={cidade}
                onChange={(e) => setCidade(e.target.value)}
              />
            </div>
          </div>
          <p aria-live="polite" className="min-h-[1.5em] text-sm text-muted-fg">
            {erro ? <span className="text-fg">{erro}</span> : calculando ? "calculando…" : dica}
          </p>
        </form>

        <div className="lg:col-span-7">
          {lista.length > 0 ? (
            <ul aria-live="polite" className="grid gap-4">
              {lista.map((r) => (
                <li key={`${r.chave}-${r.texto}`} className="revelar flex gap-4">
                  <span aria-hidden="true" className="glifo w-6 shrink-0 text-center text-xl text-honey">
                    {r.glifo}
                  </span>
                  <span>
                    <span className="text-lg">{r.texto}</span>
                    {r.nota ? <span className="block text-sm text-muted-fg">{r.nota}</span> : null}
                  </span>
                </li>
              ))}
            </ul>
          ) : (
            <p className="text-muted-fg">digite o dia e o mês e veja o que o céu já conta.</p>
          )}
        </div>
      </div>

      {comecou ? (
        <div className="revelar grid max-w-[48rem] gap-4">
          <p className="text-lg">copie e cole na sua ia. o mapa calculado já vai dentro do pedido.</p>
          <p
            id={idPrompt}
            tabIndex={0}
            className="texto-literal max-h-[24rem] overflow-y-auto whitespace-pre-wrap rounded-md bg-card p-4 font-mono text-sm leading-[1.6] [overflow-wrap:anywhere]"
          >
            {prompt}
          </p>
          <div>
            <Copiar texto={prompt} rotulo="copiar prompt" copiado="copiado. cole na sua ia" variant="default" size="lg" alvoId={idPrompt} />
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
      <Label htmlFor="contato">se quiser receber atualizações, informe seu telefone ou e-mail</Label>
      <div className="flex gap-3">
        <Input
          id="contato"
          type="text"
          autoComplete="email"
          placeholder="voce@exemplo.com ou (31) 99999-0000"
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
          <>
            é opcional e fica separado dos dados de nascimento.{" "}
            <Link href="/privacidade" className="underline underline-offset-4 hover:text-fg">
              privacidade
            </Link>
          </>
        )}
      </p>
    </form>
  );
}
