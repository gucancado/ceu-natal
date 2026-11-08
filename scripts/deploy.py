# SPDX-License-Identifier: AGPL-3.0-or-later
"""Deploy manual do ceu-natal via API do Coolify.

O deploy não é automático (push na branch não publica em produção); este
script dispara o deploy e acompanha até terminar. Mantido manual porque o
token do Coolify rotaciona ~mensalmente (um workflow no GitHub Actions
quebraria em silêncio) e porque publicar em produção deve ser decisão
explícita.

Uso:
    COOLIFY_TOKEN=<bearer> python scripts/deploy.py            # dispara e acompanha
    python scripts/deploy.py --dry-run                         # só mostra o que faria (sem token)
    COOLIFY_TOKEN=<bearer> python scripts/deploy.py --no-wait  # dispara e sai
    COOLIFY_TOKEN=<bearer> python scripts/deploy.py --app web  # deploy do site (web/)

`--app server` (padrão) publica o servidor MCP; `--app web` publica o site.

Envs, todas sem default no código. Vêm do ambiente ou de `scripts/deploy.env`
(arquivo local, fora do git; o ambiente tem precedência):
    COOLIFY_API       URL base da API do Coolify (ex.: http://<host>:8000/api/v1)
    COOLIFY_APP_UUID  uuid do app do servidor MCP; exigido com --app server
    COOLIFY_WEB_UUID  uuid do app do site; exigido com --app web
    COOLIFY_TOKEN     Bearer token do Coolify, NUNCA commitar; dispensado no --dry-run
`CEU_NATAL_DEPLOY_ENV` troca o caminho do arquivo (usado nos testes).

Saídas: 0 ok; 1 falha HTTP, deploy falhou/cancelado ou timeout de 10 min;
2 variável obrigatória ausente ou argumento inválido (erro do argparse).
"""

import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

from dotenv import load_dotenv

RAIZ = Path(__file__).resolve().parent.parent
ARQUIVO_ENV = Path(os.environ.get("CEU_NATAL_DEPLOY_ENV") or RAIZ / "scripts" / "deploy.env")
INTERVALO_S = 5
TIMEOUT_S = 10 * 60


def extrair_deployment_uuid(corpo: dict | None) -> str | None:
    """Lê o uuid do deployment nos dois formatos de resposta do Coolify."""
    if not isinstance(corpo, dict):
        return None
    deployments = corpo.get("deployments")
    dep = deployments[0] if isinstance(deployments, list) and deployments else corpo
    if not isinstance(dep, dict):
        return None
    return dep.get("deployment_uuid") or dep.get("uuid")


def _requisitar(url: str, token: str, metodo: str) -> tuple[int, dict | None]:
    req = urllib.request.Request(
        url, method=metodo, headers={"Authorization": f"Bearer {token}"}
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            codigo, texto = resp.status, resp.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as e:
        codigo, texto = e.code, e.read().decode("utf-8", "replace")
    except (urllib.error.URLError, TimeoutError, OSError):
        # Sem resposta (rede, DNS, recusa, timeout): status 0. A API do Coolify
        # fica fora ~2 min durante o build Docker, então o chamador tolera isso.
        return 0, None
    try:
        corpo = json.loads(texto)
    except ValueError:
        corpo = None
    return codigo, corpo if isinstance(corpo, dict) else None


def _post_json(url: str, token: str) -> tuple[int, dict | None]:
    return _requisitar(url, token, "POST")


def _get_json(url: str, token: str) -> tuple[int, dict | None]:
    return _requisitar(url, token, "GET")


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description="Deploy manual do ceu-natal via API do Coolify.")
    parser.add_argument("--app", choices=("server", "web"), default="server", help="o que publicar (padrão: server)")
    parser.add_argument("--dry-run", action="store_true", help="só mostra o que faria")
    parser.add_argument("--no-wait", action="store_true", help="dispara e sai, sem acompanhar")
    try:
        args = parser.parse_args(argv)
    except SystemExit as e:  # argumento inválido: o argparse já imprimiu o erro
        return e.code if isinstance(e.code, int) else 2
    load_dotenv(ARQUIVO_ENV, override=False)
    var_uuid = "COOLIFY_WEB_UUID" if args.app == "web" else "COOLIFY_APP_UUID"
    exigidas = ["COOLIFY_API", var_uuid] + ([] if args.dry_run else ["COOLIFY_TOKEN"])
    faltando = [nome for nome in exigidas if not os.environ.get(nome)]
    if faltando:
        print(f"FALTA env {', '.join(faltando)} (no ambiente ou em {ARQUIVO_ENV}).", file=sys.stderr)
        return 2
    api = os.environ["COOLIFY_API"].rstrip("/")
    uuid = os.environ[var_uuid]
    token = os.environ.get("COOLIFY_TOKEN", "")
    dry_run = args.dry_run
    sem_espera = args.no_wait

    url = f"{api}/deploy?uuid={uuid}"
    if dry_run:
        print(f"[dry-run] POST {url}")
        print(f"[dry-run] Authorization: Bearer {'<token-presente>' if token else '<SEM TOKEN>'}")
        print(f"[dry-run] depois faria polling em {api}/deployments/<deployment_uuid> até finished/failed")
        return 0

    print(f"-> disparando deploy: {url}")
    codigo, corpo = _post_json(url, token)
    if codigo == 0:
        print(f"FAIL: sem resposta do Coolify em {url} (rede/timeout)", file=sys.stderr)
        return 1
    if not 200 <= codigo < 300:
        print(f"FALHA: deploy retornou HTTP {codigo}: {corpo}", file=sys.stderr)
        return 1
    print(f"deploy aceito. {(corpo or {}).get('message', '')}".rstrip())

    deployment_uuid = extrair_deployment_uuid(corpo)
    if not deployment_uuid:
        print("(sem deployment_uuid na resposta; não dá pra acompanhar, cheque o painel do Coolify)")
        return 0
    if sem_espera:
        print(f"deployment {deployment_uuid} (--no-wait, não acompanhando)")
        return 0

    print(f"-> acompanhando deployment {deployment_uuid}")
    limite = time.monotonic() + TIMEOUT_S
    ultimo = ""
    while time.monotonic() < limite:
        time.sleep(INTERVALO_S)
        codigo, dados = _get_json(f"{api}/deployments/{deployment_uuid}", token)
        if not 200 <= codigo < 300:
            aviso = "(sem resposta, tentando de novo)" if codigo == 0 else f"(status HTTP {codigo}, tentando de novo)"
            if aviso != ultimo:
                print(f"  {aviso}")
                ultimo = aviso
            continue
        status = (dados or {}).get("status") or (dados or {}).get("deployment_status") or "unknown"
        if status != ultimo:
            print(f"  status: {status}")
            ultimo = status
        if status in ("finished", "success"):
            print("deploy FINISHED")
            return 0
        if status in ("failed", "cancelled", "error"):
            print(f"deploy {status}", file=sys.stderr)
            return 1
    print("timeout (10 min) aguardando o deploy; cheque o painel do Coolify", file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
