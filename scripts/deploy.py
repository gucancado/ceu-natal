"""Deploy manual do ceu-natal via API do Coolify.

O deploy não é automático (push na branch não publica em produção); este
script dispara o deploy e acompanha até terminar. Porte de
`scripts/deploy.mjs` do semente-platform-worker. Mantido manual porque o
token do Coolify rotaciona ~mensalmente (um workflow no GitHub Actions
quebraria em silêncio) e porque publicar em produção deve ser decisão
explícita.

Uso:
    COOLIFY_TOKEN=<bearer> python scripts/deploy.py            # dispara e acompanha
    COOLIFY_TOKEN=<bearer> python scripts/deploy.py --dry-run  # só mostra o que faria
    COOLIFY_TOKEN=<bearer> python scripts/deploy.py --no-wait  # dispara e sai

Envs (com defaults sãos; só o token é obrigatório fora do --dry-run):
    COOLIFY_TOKEN     (obrigatório) Bearer token do Coolify, NUNCA commitar
    COOLIFY_API       default http://5.78.199.192:8000/api/v1
    COOLIFY_APP_UUID  default ejbfwl0yfego72kk5n2us1gh (ceu-natal)

Saídas: 0 ok; 1 falha HTTP, deploy falhou/cancelado ou timeout de 10 min;
2 sem COOLIFY_TOKEN.
"""

import json
import os
import sys
import time
import urllib.error
import urllib.request

API_PADRAO = "http://5.78.199.192:8000/api/v1"
UUID_PADRAO = "ejbfwl0yfego72kk5n2us1gh"
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
    api = os.environ.get("COOLIFY_API", API_PADRAO)
    uuid = os.environ.get("COOLIFY_APP_UUID", UUID_PADRAO)
    token = os.environ.get("COOLIFY_TOKEN")
    dry_run = "--dry-run" in argv
    sem_espera = "--no-wait" in argv

    if not token and not dry_run:
        print(
            "FALTA env COOLIFY_TOKEN (Bearer do Coolify). "
            "Veja a seção Coolify no CLAUDE.md global.",
            file=sys.stderr,
        )
        return 2

    url = f"{api}/deploy?uuid={uuid}"
    if dry_run:
        print(f"[dry-run] POST {url}")
        print(f"[dry-run] Authorization: Bearer {'<token-presente>' if token else '<SEM TOKEN>'}")
        print(f"[dry-run] depois faria polling em {api}/deployments/<deployment_uuid> até finished/failed")
        return 0

    print(f"-> disparando deploy: {url}")
    codigo, corpo = _post_json(url, token)
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
            print(f"  (status HTTP {codigo}, tentando de novo)")
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
