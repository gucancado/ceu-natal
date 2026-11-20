import importlib.util
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
SCRIPT = RAIZ / "scripts" / "divulgacao.py"


def _carregar():
    spec = importlib.util.spec_from_file_location("divulgacao", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_sitemap_ignora_arquivos_de_texto():
    d = _carregar()
    xml = (
        "<urlset><url><loc>https://x.br/</loc></url><url><loc>https://x.br/mapa</loc></url>"
        "<url><loc>https://x.br/llms.txt</loc></url><url><loc>https://x.br/en/llms.txt</loc></url></urlset>"
    )
    assert d.urls_do_sitemap(xml) == ["https://x.br/", "https://x.br/mapa"]


def test_payload_indexnow_aponta_o_arquivo_da_chave():
    d = _carregar()
    p = d.payload_indexnow(["https://x.br/"], "abc", "https://x.br")
    assert p == {"host": "x.br", "key": "abc", "keyLocation": "https://x.br/abc.txt", "urlList": ["https://x.br/"]}


def test_env_ausente_sai_com_2(monkeypatch, capsys):
    d = _carregar()
    monkeypatch.setattr(d, "ARQUIVO_ENV", RAIZ / "scripts" / "nao-existe.env")
    monkeypatch.delenv("GLAMA_API_KEY", raising=False)
    assert d.main(["glama"]) == 2
    assert "GLAMA_API_KEY" in capsys.readouterr().err
