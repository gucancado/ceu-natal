# SPDX-License-Identifier: AGPL-3.0-or-later
"""
Gera web/public/municipios.json: os municípios do Brasil (IBGE) para as
sugestões do campo de cidade do site, do mais populoso para o menos (Censo
2022), no formato [["Belo Horizonte", "MG"], ...].

Uso: python scripts/gerar_municipios.py
"""
import gzip
import json
import urllib.request
from pathlib import Path

MUNICIPIOS = "https://servicodados.ibge.gov.br/api/v1/localidades/municipios"
POPULACAO = (
    "https://servicodados.ibge.gov.br/api/v3/agregados/4709/periodos/2022/variaveis/93"
    "?localidades=N6[all]"
)
SAIDA = Path(__file__).resolve().parent.parent / "web" / "public" / "municipios.json"


def _json(url: str):
    pedido = urllib.request.Request(url, headers={"User-Agent": "ceu-natal"})
    with urllib.request.urlopen(pedido, timeout=120) as r:
        corpo = r.read()
    if corpo[:2] == b"\x1f\x8b":
        corpo = gzip.decompress(corpo)
    return json.loads(corpo)


def _uf(m: dict) -> str:
    # Municípios recém-criados vêm sem microrregião; a região imediata sempre traz a UF.
    micro = m.get("microrregiao") or {}
    uf = (micro.get("mesorregiao") or {}).get("UF") or (
        (m.get("regiao-imediata") or {}).get("regiao-intermediaria") or {}
    ).get("UF")
    return uf["sigla"]


def main() -> None:
    populacao: dict[str, int] = {}
    for serie in _json(POPULACAO)[0]["resultados"][0]["series"]:
        valor = serie["serie"].get("2022", "")
        populacao[serie["localidade"]["id"]] = int(valor) if valor.isdigit() else 0
    municipios = _json(MUNICIPIOS)
    linhas = sorted(
        ((m["nome"], _uf(m), populacao.get(str(m["id"]), 0)) for m in municipios),
        key=lambda x: (-x[2], x[0]),
    )
    SAIDA.write_text(
        json.dumps([[nome, uf] for nome, uf, _ in linhas], ensure_ascii=False, separators=(",", ":")),
        encoding="utf-8",
    )
    print(f"{len(linhas)} municípios em {SAIDA}")


if __name__ == "__main__":
    main()
