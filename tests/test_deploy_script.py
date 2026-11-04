import importlib.util
import subprocess
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
SCRIPT = RAIZ / "scripts" / "deploy.py"


def _carregar():
    spec = importlib.util.spec_from_file_location("deploy", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_extrai_uuid_dos_dois_formatos_do_coolify():
    d = _carregar()
    assert d.extrair_deployment_uuid({"deployments": [{"deployment_uuid": "abc"}]}) == "abc"
    assert d.extrair_deployment_uuid({"deployment_uuid": "xyz"}) == "xyz"
    assert d.extrair_deployment_uuid({"message": "ok"}) is None
    assert d.extrair_deployment_uuid(None) is None


def test_dry_run_sai_zero_sem_token(monkeypatch):
    monkeypatch.delenv("COOLIFY_TOKEN", raising=False)
    r = subprocess.run([sys.executable, str(SCRIPT), "--dry-run"], capture_output=True, text=True, cwd=RAIZ)
    assert r.returncode == 0
    assert "deploy?uuid=ejbfwl0yfego72kk5n2us1gh" in r.stdout


def test_sem_token_sai_dois(monkeypatch):
    monkeypatch.delenv("COOLIFY_TOKEN", raising=False)
    r = subprocess.run([sys.executable, str(SCRIPT)], capture_output=True, text=True, cwd=RAIZ)
    assert r.returncode == 2
    assert "COOLIFY_TOKEN" in r.stderr


def test_sem_deployment_uuid_avisa_e_sai_zero(monkeypatch):
    d = _carregar()
    monkeypatch.setenv("COOLIFY_TOKEN", "t")
    monkeypatch.setattr(d, "_post_json", lambda url, token: (200, {"message": "Deployment queued."}))
    assert d.main([]) == 0


def test_http_erro_sai_um(monkeypatch):
    d = _carregar()
    monkeypatch.setenv("COOLIFY_TOKEN", "t")
    monkeypatch.setattr(d, "_post_json", lambda url, token: (401, {"message": "Unauthenticated."}))
    assert d.main([]) == 1


def test_post_sem_resposta_sai_um(monkeypatch):
    d = _carregar()
    monkeypatch.setenv("COOLIFY_TOKEN", "t")
    monkeypatch.setattr(d, "_post_json", lambda url, token: (0, None))
    assert d.main([]) == 1


def test_poll_sem_resposta_continua_ate_finished(monkeypatch):
    d = _carregar()
    monkeypatch.setenv("COOLIFY_TOKEN", "t")
    monkeypatch.setattr(d, "_post_json", lambda url, token: (200, {"deployments": [{"deployment_uuid": "d1"}]}))
    respostas = iter([(0, None), (200, {"status": "finished"})])
    monkeypatch.setattr(d, "_get_json", lambda url, token: next(respostas))
    monkeypatch.setattr(d.time, "sleep", lambda s: None)
    assert d.main([]) == 0


def test_app_web_dry_run_usa_uuid_do_site(monkeypatch):
    monkeypatch.delenv("COOLIFY_TOKEN", raising=False)
    monkeypatch.delenv("COOLIFY_WEB_UUID", raising=False)
    r = subprocess.run([sys.executable, str(SCRIPT), "--app", "web", "--dry-run"], capture_output=True, text=True, cwd=RAIZ)
    assert r.returncode == 0
    assert "deploy?uuid=atbazr01ybzciaqfmvnyfdvg" in r.stdout


def test_app_web_respeita_env_coolify_web_uuid(monkeypatch):
    monkeypatch.delenv("COOLIFY_TOKEN", raising=False)
    monkeypatch.setenv("COOLIFY_WEB_UUID", "abc123")
    r = subprocess.run([sys.executable, str(SCRIPT), "--app", "web", "--dry-run"], capture_output=True, text=True, cwd=RAIZ)
    assert r.returncode == 0
    assert "deploy?uuid=abc123" in r.stdout
