# SPDX-License-Identifier: AGPL-3.0-or-later
"""
Estatísticas de uso agregadas, num SQLite no volume persistente.

O que fica guardado (nada de nascimento, nome ou contato):
- `uso`: contagem por dia, origem (mcp/site), ferramenta, app e status, com a
  soma das durações.
- `paises`: cálculos por dia e país (ISO alpha-2 ou "??").
- `cidades`: a chave normalizada de cada cidade já calculada, só para contar
  quantas são; o nome nunca sai na rota pública.
- Pessoas únicas por dia: hash do IP (site) ou do id de sessão (MCP) com um
  sal aleatório do dia. No fim do dia sobra só a contagem: os hashes e o sal
  são apagados, e ninguém consegue refazer o hash de um IP depois disso.
"""
import hashlib
import re
import secrets
import sqlite3
import threading
from collections.abc import Callable
from datetime import date, datetime, timedelta, timezone

# Apps de IA que podem aparecer pelo nome na página pública. O `clientInfo.name`
# é escrito pelo cliente; qualquer coisa fora desta lista vira "outros", para
# que um cliente com nome de pessoa nunca seja publicado.
APPS_CONHECIDOS: dict[str, str] = {
    "claude-ai": "Claude",
    "claude": "Claude",
    "claude-code": "Claude Code",
    "anthropic": "Claude",
    "openai-mcp": "ChatGPT",
    "openai": "ChatGPT",
    "chatgpt": "ChatGPT",
    "cursor": "Cursor",
    "cursor-vscode": "Cursor",
    "visual studio code": "VS Code",
    "vscode": "VS Code",
    "windsurf": "Windsurf",
    "zed": "Zed",
    "le chat": "Le Chat",
    "mistral": "Le Chat",
    "manus": "Manus",
    "gemini-cli": "Gemini CLI",
    "mcp-inspector": "MCP Inspector",
}

# Países com menos chamadas que isto entram em "outros" na rota pública.
PAIS_MINIMO_PUBLICO = 5
DIAS_SERIE = 30
# O que conta como "cálculo" (healthcheck e listar_aspectos_tipos não contam).
_CALCULO = "(ferramenta LIKE 'calcular_%' OR ferramenta = 'mapa_rapido')"
_TEXTO_APP = re.compile(r"[^a-z0-9 ._-]")

_ESQUEMA = """
CREATE TABLE IF NOT EXISTS uso (
    dia TEXT NOT NULL, origem TEXT NOT NULL, ferramenta TEXT NOT NULL,
    app TEXT NOT NULL, status TEXT NOT NULL,
    chamadas INTEGER NOT NULL DEFAULT 0, soma_ms REAL NOT NULL DEFAULT 0,
    PRIMARY KEY (dia, origem, ferramenta, app, status)
);
CREATE TABLE IF NOT EXISTS paises (
    dia TEXT NOT NULL, pais TEXT NOT NULL, chamadas INTEGER NOT NULL DEFAULT 0,
    PRIMARY KEY (dia, pais)
);
CREATE TABLE IF NOT EXISTS cidades (chave TEXT PRIMARY KEY, primeiro_dia TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS sal (dia TEXT PRIMARY KEY, valor TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS unicos_abertos (
    dia TEXT NOT NULL, tipo TEXT NOT NULL, hash TEXT NOT NULL,
    PRIMARY KEY (dia, tipo, hash)
);
CREATE TABLE IF NOT EXISTS unicos (
    dia TEXT NOT NULL, tipo TEXT NOT NULL, quantidade INTEGER NOT NULL,
    PRIMARY KEY (dia, tipo)
);
"""


def normalizar_app(nome: str | None) -> str:
    """Nome do cliente MCP em minúsculas, só com caracteres seguros, até 40."""
    if not nome:
        return "desconhecido"
    texto = _TEXTO_APP.sub("", nome.strip().lower())[:40]
    return texto or "desconhecido"


def app_publico(app: str) -> str:
    """Rótulo publicável: o nome conhecido ou "outros"."""
    if app in APPS_CONHECIDOS:
        return APPS_CONHECIDOS[app]
    for chave, rotulo in APPS_CONHECIDOS.items():
        if app.startswith(chave):
            return rotulo
    return "outros"


def _agora() -> datetime:
    return datetime.now(timezone.utc)


class Estatisticas:
    """Contadores agregados; seguro para chamar de várias threads."""

    def __init__(self, caminho: str, relogio: Callable[[], datetime] = _agora) -> None:
        self._relogio = relogio
        self._trava = threading.Lock()
        self._con = sqlite3.connect(caminho, check_same_thread=False, isolation_level=None)
        self._con.execute("PRAGMA journal_mode=WAL")
        self._con.execute("PRAGMA synchronous=NORMAL")
        self._con.executescript(_ESQUEMA)

    def _dia(self) -> str:
        return self._relogio().date().isoformat()

    # ── escrita ──────────────────────────────────────────────
    def registrar_chamada(
        self, origem: str, ferramenta: str, app: str, status: str, duracao_ms: float,
    ) -> None:
        with self._trava:
            self._con.execute(
                "INSERT INTO uso (dia, origem, ferramenta, app, status, chamadas, soma_ms) "
                "VALUES (?, ?, ?, ?, ?, 1, ?) "
                "ON CONFLICT (dia, origem, ferramenta, app, status) DO UPDATE SET "
                "chamadas = chamadas + 1, soma_ms = soma_ms + excluded.soma_ms",
                (self._dia(), origem, ferramenta, app, status, float(duracao_ms)),
            )

    def registrar_lugar(self, cidade: str, pais: str | None) -> None:
        dia = self._dia()
        chave = f"{cidade.strip().lower()}|{(pais or '').lower()}"
        with self._trava:
            self._con.execute(
                "INSERT INTO paises (dia, pais, chamadas) VALUES (?, ?, 1) "
                "ON CONFLICT (dia, pais) DO UPDATE SET chamadas = chamadas + 1",
                (dia, pais or "??"),
            )
            self._con.execute(
                "INSERT OR IGNORE INTO cidades (chave, primeiro_dia) VALUES (?, ?)", (chave, dia),
            )

    def registrar_unico(self, tipo: str, identificador: str | None) -> None:
        """Conta uma pessoa (site) ou sessão (mcp) no dia, sem guardar o identificador."""
        if not identificador:
            return
        dia = self._dia()
        with self._trava:
            self._fechar_dias_anteriores(dia)
            linha = self._con.execute("SELECT valor FROM sal WHERE dia = ?", (dia,)).fetchone()
            if linha is None:
                sal = secrets.token_hex(32)
                self._con.execute("INSERT INTO sal (dia, valor) VALUES (?, ?)", (dia, sal))
            else:
                sal = linha[0]
            resumo = hashlib.sha256(f"{sal}|{tipo}|{identificador}".encode()).hexdigest()[:32]
            self._con.execute(
                "INSERT OR IGNORE INTO unicos_abertos (dia, tipo, hash) VALUES (?, ?, ?)",
                (dia, tipo, resumo),
            )

    def _fechar_dias_anteriores(self, hoje: str) -> None:
        """Consolida a contagem dos dias passados e apaga os hashes e o sal deles."""
        antigos = self._con.execute(
            "SELECT DISTINCT dia FROM sal WHERE dia < ? "
            "UNION SELECT DISTINCT dia FROM unicos_abertos WHERE dia < ?", (hoje, hoje),
        ).fetchall()
        if not antigos:
            return
        self._con.execute("BEGIN")
        try:
            self._con.execute(
                "INSERT OR REPLACE INTO unicos (dia, tipo, quantidade) "
                "SELECT dia, tipo, COUNT(*) FROM unicos_abertos WHERE dia < ? GROUP BY dia, tipo",
                (hoje,),
            )
            self._con.execute("DELETE FROM unicos_abertos WHERE dia < ?", (hoje,))
            self._con.execute("DELETE FROM sal WHERE dia < ?", (hoje,))
            self._con.execute("COMMIT")
        except Exception:
            self._con.execute("ROLLBACK")
            raise

    # ── leitura ──────────────────────────────────────────────
    def resumo(self) -> dict:
        """Números para a rota pública: só agregados, sem cidades nem nomes."""
        hoje = self._dia()
        inicio_serie = (date.fromisoformat(hoje) - timedelta(days=DIAS_SERIE - 1)).isoformat()
        with self._trava:
            self._fechar_dias_anteriores(hoje)
            c = self._con
            desde = c.execute("SELECT MIN(dia) FROM uso").fetchone()[0]
            total, soma_ms, ok, calculos = c.execute(
                "SELECT COALESCE(SUM(chamadas), 0), COALESCE(SUM(soma_ms), 0), "
                "COALESCE(SUM(CASE WHEN status = 'ok' THEN chamadas END), 0), "
                f"COALESCE(SUM(CASE WHEN status = 'ok' AND {_CALCULO} THEN chamadas END), 0) FROM uso",
            ).fetchone()
            por_ferramenta = c.execute(
                "SELECT ferramenta, SUM(chamadas) FROM uso WHERE status = 'ok' "
                "GROUP BY ferramenta ORDER BY 2 DESC",
            ).fetchall()
            por_origem = c.execute(
                "SELECT origem, SUM(chamadas) FROM uso WHERE status = 'ok' GROUP BY origem",
            ).fetchall()
            por_app_bruto = c.execute(
                "SELECT app, SUM(chamadas) FROM uso WHERE status = 'ok' AND origem = 'mcp' GROUP BY app",
            ).fetchall()
            paises_bruto = c.execute(
                "SELECT pais, SUM(chamadas) FROM paises GROUP BY pais ORDER BY 2 DESC",
            ).fetchall()
            n_cidades = c.execute("SELECT COUNT(*) FROM cidades").fetchone()[0]
            serie_uso = dict(c.execute(
                f"SELECT dia, SUM(chamadas) FROM uso WHERE status = 'ok' AND {_CALCULO} AND dia >= ? "
                "GROUP BY dia",
                (inicio_serie,),
            ).fetchall())
            serie_unicos: dict[tuple[str, str], int] = {
                (d, t): q for d, t, q in c.execute(
                    "SELECT dia, tipo, quantidade FROM unicos WHERE dia >= ? "
                    "UNION ALL SELECT dia, tipo, COUNT(*) FROM unicos_abertos GROUP BY dia, tipo",
                    (inicio_serie,),
                ).fetchall()
            }
            unicos_total = dict(c.execute(
                "SELECT tipo, SUM(q) FROM (SELECT tipo, quantidade AS q FROM unicos "
                "UNION ALL SELECT tipo, COUNT(*) FROM unicos_abertos GROUP BY tipo) GROUP BY tipo",
            ).fetchall())

        por_app: dict[str, int] = {}
        for app, n in por_app_bruto:
            rotulo = app_publico(app)
            por_app[rotulo] = por_app.get(rotulo, 0) + n
        paises: list[dict] = []
        outros = 0
        for pais, n in paises_bruto:
            if pais == "??" or n < PAIS_MINIMO_PUBLICO:
                outros += n
            else:
                paises.append({"pais": pais, "chamadas": n})
        if outros:
            paises.append({"pais": "outros", "chamadas": outros})

        serie = []
        dia = date.fromisoformat(inicio_serie)
        for _ in range(DIAS_SERIE):
            d = dia.isoformat()
            serie.append({
                "dia": d,
                "calculos": serie_uso.get(d, 0),
                "pessoas_site": serie_unicos.get((d, "site"), 0),
                "sessoes_mcp": serie_unicos.get((d, "mcp"), 0),
            })
            dia += timedelta(days=1)

        return {
            "desde": desde,
            "atualizado_em": self._relogio().isoformat(timespec="seconds"),
            "totais": {
                "chamadas": total,
                "calculos": calculos,
                "taxa_erro": round((total - ok) / total, 4) if total else 0,
                "tempo_medio_ms": round(soma_ms / total, 1) if total else 0,
                "cidades": n_cidades,
                "paises": len([p for p in paises_bruto if p[0] != "??"]),
                # Soma de pessoas-dia: a mesma pessoa em dois dias conta duas vezes.
                "pessoas_dia_site": unicos_total.get("site", 0),
                "sessoes_mcp": unicos_total.get("mcp", 0),
            },
            "por_dia": serie,
            "por_origem": {o: n for o, n in por_origem},
            "por_ferramenta": [{"ferramenta": f, "chamadas": n} for f, n in por_ferramenta],
            "por_app": sorted(
                ({"app": a, "chamadas": n} for a, n in por_app.items()),
                key=lambda x: -x["chamadas"],
            ),
            "paises": paises,
        }
