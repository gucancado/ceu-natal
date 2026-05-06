"""
Script de validação: conecta ao MCP de produção (SSE), executa as tools
disponíveis com dados reais e mede tempos.

Uso:
  1. Copiar scripts/dados_familia.example.json -> scripts/dados_familia.json
     e preencher com seus dados de nascimento (não vai pro git).
  2. python scripts/validacao_producao.py

Saídas em scripts/saida/ (gitignored — contêm dados pessoais).
"""
import asyncio
import json
import statistics
import sys
import time
from pathlib import Path

from mcp import ClientSession
from mcp.client.sse import sse_client

URL = "https://ceu-natal-api.pu5h6p.easypanel.host/sse"
OUT_DIR = Path("scripts/saida")
DADOS_PATH = Path("scripts/dados_familia.json")
DADOS_EXEMPLO = Path("scripts/dados_familia.example.json")


def _carregar_dados() -> dict:
    if not DADOS_PATH.exists():
        raise SystemExit(
            f"Arquivo {DADOS_PATH} não existe.\n"
            f"Copie {DADOS_EXEMPLO} para {DADOS_PATH} e preencha."
        )
    with open(DADOS_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def _save(filename: str, data) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    with open(OUT_DIR / filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def _parse_tool_result(result) -> dict:
    if not result.content:
        return {"_erro_protocolo": "resultado vazio"}
    text = result.content[0].text
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return {"_raw": text}


def _args_natal(pessoa: dict) -> dict:
    args = {"data": pessoa["data"]}
    for k in ("hora", "local", "nome"):
        v = pessoa.get(k)
        if v:
            args[k] = v
    return args


async def main() -> int:
    familia = _carregar_dados()
    referencia_key = familia.get("_referencia", "maria")
    sequencia_keys = familia.get("_sequencia_estabilidade", list(familia.keys()))
    pessoas = {k: v for k, v in familia.items() if not k.startswith("_")}

    erros = 0
    tempos_natal: list[float] = []

    async with sse_client(URL) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            tools_resp = await session.list_tools()
            tools_names = sorted(t.name for t in tools_resp.tools)
            print(f"[tools] {len(tools_names)}: {tools_names}")
            _save("00_tools_listadas.json", {"count": len(tools_names),
                                             "tools": tools_names})

            t0 = time.perf_counter()
            r = await session.call_tool("healthcheck", {})
            dt = time.perf_counter() - t0
            health = _parse_tool_result(r)
            print(f"[healthcheck] {dt*1000:.0f} ms — {health}")
            _save("01_healthcheck.json", {"tempo_ms": round(dt*1000, 1), "resp": health})

            t0 = time.perf_counter()
            r = await session.call_tool("listar_aspectos_tipos", {})
            dt = time.perf_counter() - t0
            asp = _parse_tool_result(r)
            print(f"[listar_aspectos_tipos] {dt*1000:.0f} ms — "
                  f"{len((asp or {}).get('aspectos', []))} aspectos")
            _save("02_listar_aspectos.json", {"tempo_ms": round(dt*1000, 1), "resp": asp})

            ref = pessoas[referencia_key]
            print(f"\n=== Mapa natal de referência ({ref.get('nome', referencia_key)}) ===")
            t0 = time.perf_counter()
            r = await session.call_tool("calcular_mapa_natal", _args_natal(ref))
            dt = time.perf_counter() - t0
            ref_natal = _parse_tool_result(r)
            tempos_natal.append(dt)
            print(f"  tempo: {dt*1000:.0f} ms")
            if "erro" in ref_natal:
                print(f"  ERRO: {ref_natal['erro']}")
                erros += 1
            else:
                p = ref_natal["planetas"]; a = ref_natal.get("angulos", {})
                print(f"  Sol: {p['sol']['signo']} {p['sol']['grau']} casa {p['sol'].get('casa')}")
                print(f"  Asc: {a.get('ascendente', {}).get('signo')} {a.get('ascendente', {}).get('grau')}")
                print(f"  MC : {a.get('meio_do_ceu', {}).get('signo')} {a.get('meio_do_ceu', {}).get('grau')}")
                print(f"  Sat: {p['saturno']['signo']} {p['saturno']['grau']} casa {p['saturno'].get('casa')}")
            _save(f"10_{referencia_key}_natal.json", ref_natal)

            # Sinastria com a primeira outra pessoa após referência
            outras = [k for k in pessoas if k != referencia_key]
            if outras:
                outro = outras[0]
                print(f"\n=== Sinastria: {referencia_key} + {outro} ===")
                t0 = time.perf_counter()
                r = await session.call_tool("calcular_sinastria", {
                    "pessoa_a": pessoas[referencia_key],
                    "pessoa_b": pessoas[outro],
                })
                dt = time.perf_counter() - t0
                sin = _parse_tool_result(r)
                print(f"  tempo: {dt*1000:.0f} ms")
                if "erro" in sin:
                    print(f"  ERRO: {sin['erro']}")
                    erros += 1
                else:
                    print(f"  {len(sin.get('aspectos_sinastria', []))} aspectos cruzados")
                _save(f"11_sinastria_{referencia_key}_{outro}.json", sin)

            print("\n=== Tools da Fase 2 ===")
            for t in ("calcular_transitos", "calcular_progressoes", "calcular_mapa_composto"):
                presente = t in tools_names
                print(f"  {t}: {'PRESENTE' if presente else 'AUSENTE em produção'}")

            print(f"\n=== Estabilidade: {len(sequencia_keys)} chamadas ===")
            estabilidade = []
            for i, key in enumerate(sequencia_keys, 1):
                pessoa = pessoas.get(key)
                if not pessoa:
                    print(f"  {i}. {key} -> não encontrado em dados, pulando")
                    continue
                t0 = time.perf_counter()
                try:
                    r = await session.call_tool("calcular_mapa_natal", _args_natal(pessoa))
                    dt = time.perf_counter() - t0
                    body = _parse_tool_result(r)
                    erro = body.get("erro")
                    sol = body.get("planetas", {}).get("sol", {}).get("signo") if not erro else None
                    asc = body.get("angulos", {}).get("ascendente", {}).get("signo") if not erro else None
                    aviso = body.get("aviso")
                except Exception as exc:
                    dt = time.perf_counter() - t0
                    erro = f"{type(exc).__name__}: {exc}"
                    sol = asc = aviso = None
                tempos_natal.append(dt)
                estabilidade.append({"ordem": i, "key": key,
                                     "tempo_ms": round(dt*1000, 1),
                                     "erro": erro, "sol": sol, "asc": asc, "aviso": aviso})
                status = "ERRO" if erro else "OK"
                print(f"  {i:2d}. {key:10s} {dt*1000:7.0f} ms  Sol={sol} Asc={asc}  {status}")
                if erro:
                    erros += 1

            tempos_ms = [t * 1000 for t in tempos_natal]
            sumario = {
                "n": len(tempos_ms),
                "media_ms": round(statistics.mean(tempos_ms), 1),
                "mediana_ms": round(statistics.median(tempos_ms), 1),
                "min_ms": round(min(tempos_ms), 1),
                "max_ms": round(max(tempos_ms), 1),
                "stdev_ms": round(statistics.stdev(tempos_ms), 1) if len(tempos_ms) > 1 else 0.0,
                "erros": erros,
            }
            print(f"\n[sumário tempos] {sumario}")
            _save("20_estabilidade.json", {"sumario": sumario, "chamadas": estabilidade})

    print(f"\n=== fim — erros: {erros} ===")
    return 0 if erros == 0 else 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
