# SPDX-License-Identifier: AGPL-3.0-or-later
"""Avisa buscadores e consulta diretórios do Céu Natal pela API, sem abrir navegador.

Comandos:
    python scripts/divulgacao.py indexnow [URL ...]        # Bing, Yandex, Seznam e outros (sem conta)
    python scripts/divulgacao.py bing cota
    python scripts/divulgacao.py bing enviar [URL ...]
    python scripts/divulgacao.py bing sitemap
    python scripts/divulgacao.py glama                      # nota, release e tools no Glama
    python scripts/divulgacao.py google sitemaps
    python scripts/divulgacao.py google enviar-sitemap
    python scripts/divulgacao.py google inspecionar URL

Sem URLs, `indexnow` e `bing enviar` usam todas as páginas do sitemap do site.

Envs, do ambiente ou de `scripts/deploy.env` (arquivo local, fora do git):
    SITE_URL          endereço do site (padrão https://ceunatal.gustavocancado.com.br)
    INDEXNOW_KEY      chave pública do IndexNow; o site serve `/<chave>.txt` (web/public/)
    BING_API_KEY      chave da API do Bing Webmaster Tools (Settings → API access)
    GLAMA_API_KEY     opcional; chave da API do Glama (exige cartão no Glama). Sem ela,
                      `glama` lê o selo e a página pública
    GOOGLE_SA_JSON    caminho do JSON da conta de serviço com acesso à propriedade
                      `sc-domain:gustavocancado.com.br` no Search Console
    GOOGLE_PROPRIEDADE  padrão `sc-domain:gustavocancado.com.br`

Saídas: 0 ok; 1 falha HTTP; 2 env ausente ou argumento inválido.
"""

import argparse
import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any

from dotenv import load_dotenv

RAIZ = Path(__file__).resolve().parent.parent
ARQUIVO_ENV = Path(os.environ.get("CEU_NATAL_DEPLOY_ENV") or RAIZ / "scripts" / "deploy.env")
GLAMA_SERVIDOR = "gucancado/ceu-natal"
BING_API = "https://ssl.bing.com/webmaster/api.svc/json"
GSC_API = "https://searchconsole.googleapis.com"
WEBMASTERS_API = "https://www.googleapis.com/webmasters/v3"


class FaltaEnv(Exception):
    """Env obrigatória ausente."""


def env(nome: str, padrao: str | None = None) -> str:
    valor = os.environ.get(nome) or padrao
    if not valor:
        raise FaltaEnv(f"Falta a variável {nome} (ambiente ou {ARQUIVO_ENV.name}).")
    return valor


def site_url() -> str:
    return env("SITE_URL", "https://ceunatal.gustavocancado.com.br").rstrip("/")


def requisitar(url: str, metodo: str = "GET", corpo: Any = None, headers: dict | None = None) -> tuple[int, Any]:
    dados = json.dumps(corpo).encode() if corpo is not None else None
    hs = {"User-Agent": "ceu-natal-divulgacao", **(headers or {})}
    if dados is not None:
        hs["Content-Type"] = "application/json; charset=utf-8"
    req = urllib.request.Request(url, data=dados, method=metodo, headers=hs)
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            texto = r.read().decode("utf-8", "replace")
            status = r.status
    except urllib.error.HTTPError as e:
        texto = e.read().decode("utf-8", "replace")
        status = e.code
    try:
        return status, json.loads(texto) if texto else None
    except json.JSONDecodeError:
        return status, texto


def urls_do_sitemap(xml: str) -> list[str]:
    """Páginas do sitemap, sem os arquivos de texto (llms.txt) que não são páginas."""
    return [u for u in re.findall(r"<loc>([^<]+)</loc>", xml) if not u.endswith(".txt")]


def baixar_sitemap() -> list[str]:
    status, corpo = requisitar(f"{site_url()}/sitemap.xml")
    if status != 200 or not isinstance(corpo, str):
        raise RuntimeError(f"sitemap respondeu {status}")
    return urls_do_sitemap(corpo)


def payload_indexnow(urls: list[str], chave: str, base: str) -> dict:
    host = urllib.parse.urlsplit(base).netloc
    return {"host": host, "key": chave, "keyLocation": f"{base}/{chave}.txt", "urlList": urls}


def mostrar(status: int, corpo: Any) -> int:
    print(status, json.dumps(corpo, ensure_ascii=False, indent=2) if not isinstance(corpo, str) else corpo[:2000])
    return 0 if 200 <= status < 300 else 1


# --- IndexNow ---------------------------------------------------------------

def cmd_indexnow(urls: list[str]) -> int:
    base = site_url()
    status, corpo = requisitar(
        "https://api.indexnow.org/indexnow", "POST", payload_indexnow(urls or baixar_sitemap(), env("INDEXNOW_KEY"), base)
    )
    return mostrar(status, corpo)


# --- Bing Webmaster ---------------------------------------------------------

def _bing(metodo_api: str, http: str = "GET", corpo: Any = None, **params: str) -> tuple[int, Any]:
    q = urllib.parse.urlencode({"apikey": env("BING_API_KEY"), **params})
    return requisitar(f"{BING_API}/{metodo_api}?{q}", http, corpo)


def cmd_bing(acao: str, urls: list[str]) -> int:
    base = site_url() + "/"
    if acao == "cota":
        return mostrar(*_bing("GetUrlSubmissionQuota", siteUrl=base))
    if acao == "enviar":
        return mostrar(*_bing("SubmitUrlBatch", "POST", {"siteUrl": base, "urlList": urls or baixar_sitemap()}))
    return mostrar(*_bing("SubmitFeed", "POST", {"siteUrl": base, "feedUrl": f"{site_url()}/sitemap.xml"}))


# --- Glama ------------------------------------------------------------------

def resumo_do_selo(svg: str) -> str:
    """Título e descrição do selo público do Glama (nota, tools, manutenção)."""
    partes = [re.search(rf"<{tag}>([^<]*)</{tag}>", svg) for tag in ("title", "desc")]
    return "\n".join(m.group(1) for m in partes if m)


def cmd_glama() -> int:
    if not os.environ.get("GLAMA_API_KEY"):
        # A chave da API do Glama exige cartão cadastrado; sem ela, lê o selo e a página pública.
        base = f"https://glama.ai/mcp/servers/{GLAMA_SERVIDOR}"
        _, svg = requisitar(f"{base}/badges/score.svg")
        _, pagina = requisitar(base, headers={"User-Agent": "Mozilla/5.0"})
        print(resumo_do_selo(svg if isinstance(svg, str) else ""))
        antigos = sorted(set(re.findall(r"mistico\.gustavocancado\.com\.br[^\"'<\\\s]*", str(pagina))))
        print("Endereço antigo na página:", ", ".join(antigos) or "nenhum")
        return 0
    status, corpo = requisitar(
        f"https://glama.ai/api/mcp/v1/servers/{GLAMA_SERVIDOR}",
        headers={"Authorization": f"Bearer {env('GLAMA_API_KEY')}"},
    )
    return mostrar(status, corpo)


# --- Google Search Console ---------------------------------------------------

def token_google() -> str:
    import jwt  # pyjwt[crypto], já vem com o `mcp`

    sa = json.loads(Path(env("GOOGLE_SA_JSON")).read_text(encoding="utf-8"))
    agora = int(time.time())
    afirmacao = jwt.encode(
        {
            "iss": sa["client_email"],
            "scope": "https://www.googleapis.com/auth/webmasters",
            "aud": "https://oauth2.googleapis.com/token",
            "iat": agora,
            "exp": agora + 3600,
        },
        sa["private_key"],
        algorithm="RS256",
    )
    dados = urllib.parse.urlencode(
        {"grant_type": "urn:ietf:params:oauth:grant-type:jwt-bearer", "assertion": afirmacao}
    ).encode()
    with urllib.request.urlopen("https://oauth2.googleapis.com/token", dados, timeout=30) as r:
        return json.load(r)["access_token"]


def cmd_google(acao: str, urls: list[str]) -> int:
    prop = env("GOOGLE_PROPRIEDADE", "sc-domain:gustavocancado.com.br")
    auth = {"Authorization": f"Bearer {token_google()}"}
    prop_q = urllib.parse.quote(prop, safe="")
    if acao == "sitemaps":
        return mostrar(*requisitar(f"{WEBMASTERS_API}/sites/{prop_q}/sitemaps", headers=auth))
    if acao == "enviar-sitemap":
        mapa = urllib.parse.quote(f"{site_url()}/sitemap.xml", safe="")
        return mostrar(*requisitar(f"{WEBMASTERS_API}/sites/{prop_q}/sitemaps/{mapa}", "PUT", headers=auth))
    if not urls:
        raise FaltaEnv("Informe a URL a inspecionar.")
    codigo = 0
    for url in urls:
        codigo |= mostrar(*requisitar(
            f"{GSC_API}/v1/urlInspection/index:inspect", "POST", {"inspectionUrl": url, "siteUrl": prop}, auth
        ))
    return codigo


def main(argv: list[str] | None = None) -> int:
    load_dotenv(ARQUIVO_ENV, override=False)
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="comando", required=True)
    sub.add_parser("indexnow").add_argument("urls", nargs="*")
    b = sub.add_parser("bing")
    b.add_argument("acao", choices=["cota", "enviar", "sitemap"])
    b.add_argument("urls", nargs="*")
    sub.add_parser("glama")
    g = sub.add_parser("google")
    g.add_argument("acao", choices=["sitemaps", "enviar-sitemap", "inspecionar"])
    g.add_argument("urls", nargs="*")
    a = p.parse_args(argv)
    try:
        if a.comando == "indexnow":
            return cmd_indexnow(a.urls)
        if a.comando == "bing":
            return cmd_bing(a.acao, a.urls)
        if a.comando == "glama":
            return cmd_glama()
        return cmd_google(a.acao, a.urls)
    except FaltaEnv as e:
        print(e, file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
