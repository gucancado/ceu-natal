import json
from pathlib import Path

from app.config import Settings


def test_server_json_coerente_com_o_servidor():
    doc = json.loads((Path(__file__).resolve().parent.parent / "server.json").read_text(encoding="utf-8"))
    assert doc["$schema"] == "https://static.modelcontextprotocol.io/schemas/2025-12-11/server.schema.json"
    assert doc["name"] == "io.github.gucancado/ceu-natal"
    assert len(doc["description"]) <= 100
    assert doc["version"] == Settings().server_version
    assert doc["remotes"][0] == {"type": "streamable-http", "url": "https://astrologia-mcp.gustavocancado.com.br/mcp/"}
    assert doc["repository"] == {"url": "https://github.com/gucancado/ceu-natal", "source": "github"}
