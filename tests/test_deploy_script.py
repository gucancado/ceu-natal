import importlib.util
import os
import subprocess
import sys
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parent.parent
SCRIPT = RAIZ / "scripts" / "deploy.py"

API = "http://coolify.exemplo:8000/api/v1"
ENVS = {"COOLIFY_API": API, "COOLIFY_APP_UUID": "app-uuid-teste", "COOLIFY_WEB_UUID": "web-uuid-teste"}
VARIAVEIS = (*ENVS, "COOLIFY_TOKEN")


def _carregar():
    spec = importlib.util.spec_from_file_location("deploy", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture
def envs(monkeypatch):
    """Envs explícitas; o `deploy.env` local (se existir) não é lido nos testes."""
    for nome in VARIAVEIS:
        monkeypatch.delenv(nome, raising=False)
    for nome, valor in ENVS.items():
        monkeypatch.setenv(nome, valor)
    monkeypatch.setenv("COOLIFY_TOKEN", "t")


@pytest.fixture
def modulo(envs, monkeypatch):
    d = _carregar()
    monkeypatch.setattr(d, "ARQUIVO_ENV", RAIZ / "scripts" / "nao-existe.env")
    return d


def _rodar(args: list[str], **extra: str) -> subprocess.CompletedProcess:
    """Roda o script com só as envs dadas (+ o mínimo do sistema) e sem deploy.env."""
    env = {k: v for k, v in os.environ.items() if k not in VARIAVEIS}
    env.update(extra)
    env["CEU_NATAL_DEPLOY_ENV"] = str(RAIZ / "scripts" / "nao-existe.env")
    return subprocess.run([sys.executable, str(SCRIPT), *args], capture_output=True, text=True, cwd=RAIZ, env=env)


def test_extrai_uuid_dos_dois_formatos_do_coolify():
    d = _carregar()
    assert d.extrair_deployment_uuid({"deployments": [{"deployment_uuid": "abc"}]}) == "abc"
    assert d.extrair_deployment_uuid({"deployment_uuid": "xyz"}) == "xyz"
    assert d.extrair_deployment_uuid({"message": "ok"}) is None
    assert d.extrair_deployment_uuid(None) is None


def test_codigo_nao_tem_ip_nem_uuid_de_producao():
    texto = SCRIPT.read_text(encoding="utf-8")
    assert "5.78." not in texto
    assert "API_PADRAO" not in texto and "UUID_PADRAO" not in texto


def test_dry_run_monta_url_com_as_envs_e_dispensa_token():
    r = _rodar(["--dry-run"], COOLIFY_API=API, COOLIFY_APP_UUID="app-uuid-teste")
    assert r.returncode == 0, r.stderr
    assert f"POST {API}/deploy?uuid=app-uuid-teste" in r.stdout


def test_app_web_dry_run_usa_coolify_web_uuid():
    r = _rodar(["--app", "web", "--dry-run"], COOLIFY_API=API, COOLIFY_WEB_UUID="web-uuid-teste")
    assert r.returncode == 0, r.stderr
    assert f"{API}/deploy?uuid=web-uuid-teste" in r.stdout


def test_app_igual_web_funciona():
    r = _rodar(["--app=web", "--dry-run"], COOLIFY_API=API, COOLIFY_WEB_UUID="web-uuid-teste")
    assert r.returncode == 0, r.stderr
    assert "deploy?uuid=web-uuid-teste" in r.stdout


def test_sem_app_uuid_sai_dois_nomeando_a_variavel():
    r = _rodar(["--dry-run"], COOLIFY_API=API, COOLIFY_TOKEN="t")
    assert r.returncode == 2
    assert "COOLIFY_APP_UUID" in r.stderr


def test_sem_web_uuid_sai_dois_nomeando_a_variavel():
    r = _rodar(["--app", "web", "--dry-run"], COOLIFY_API=API, COOLIFY_APP_UUID="x")
    assert r.returncode == 2
    assert "COOLIFY_WEB_UUID" in r.stderr


def test_sem_api_sai_dois_nomeando_a_variavel():
    r = _rodar(["--dry-run"], COOLIFY_APP_UUID="x")
    assert r.returncode == 2
    assert "COOLIFY_API" in r.stderr


def test_sem_token_sai_dois():
    r = _rodar([], COOLIFY_API=API, COOLIFY_APP_UUID="x")
    assert r.returncode == 2
    assert "COOLIFY_TOKEN" in r.stderr


def test_le_deploy_env_sem_sobrescrever_o_ambiente(tmp_path):
    arquivo = tmp_path / "deploy.env"
    arquivo.write_text(
        f"COOLIFY_API={API}\nCOOLIFY_APP_UUID=do-arquivo\nCOOLIFY_WEB_UUID=web-do-arquivo\n", encoding="utf-8"
    )
    env = {k: v for k, v in os.environ.items() if k not in VARIAVEIS}
    env["CEU_NATAL_DEPLOY_ENV"] = str(arquivo)
    r = subprocess.run(
        [sys.executable, str(SCRIPT), "--dry-run"], capture_output=True, text=True, cwd=RAIZ, env=env
    )
    assert r.returncode == 0, r.stderr
    assert f"{API}/deploy?uuid=do-arquivo" in r.stdout
    env["COOLIFY_APP_UUID"] = "do-ambiente"
    r = subprocess.run(
        [sys.executable, str(SCRIPT), "--dry-run"], capture_output=True, text=True, cwd=RAIZ, env=env
    )
    assert "deploy?uuid=do-ambiente" in r.stdout


def test_app_invalido_sai_dois():
    r = _rodar(["--app", "x", "--dry-run"], COOLIFY_API=API, COOLIFY_APP_UUID="x")
    assert r.returncode == 2
    assert "--app" in r.stderr


def test_sem_deployment_uuid_avisa_e_sai_zero(modulo, monkeypatch):
    monkeypatch.setattr(modulo, "_post_json", lambda url, token: (200, {"message": "Deployment queued."}))
    assert modulo.main([]) == 0


def test_post_usa_url_das_envs(modulo, monkeypatch):
    chamadas = []
    monkeypatch.setattr(modulo, "_post_json", lambda url, token: chamadas.append(url) or (200, {}))
    assert modulo.main([]) == 0
    assert chamadas == [f"{API}/deploy?uuid=app-uuid-teste"]


def test_http_erro_sai_um(modulo, monkeypatch):
    monkeypatch.setattr(modulo, "_post_json", lambda url, token: (401, {"message": "Unauthenticated."}))
    assert modulo.main([]) == 1


def test_post_sem_resposta_sai_um(modulo, monkeypatch):
    monkeypatch.setattr(modulo, "_post_json", lambda url, token: (0, None))
    assert modulo.main([]) == 1


def test_poll_sem_resposta_continua_ate_finished(modulo, monkeypatch):
    monkeypatch.setattr(modulo, "_post_json", lambda url, token: (200, {"deployments": [{"deployment_uuid": "d1"}]}))
    respostas = iter([(0, None), (200, {"status": "finished"})])
    monkeypatch.setattr(modulo, "_get_json", lambda url, token: next(respostas))
    monkeypatch.setattr(modulo.time, "sleep", lambda s: None)
    assert modulo.main([]) == 0
