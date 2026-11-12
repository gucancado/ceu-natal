# SPDX-License-Identifier: AGPL-3.0-or-later
"""
Histórico dos mapas feitos no formulário do site, num SQLite no volume
persistente (`HISTORICO_PATH`).

Só o site grava aqui; o MCP continua sem guardar dados de nascimento.

- `mapas`: um registro por mapa. O id vem do navegador e só muda quando a
  data de nascimento muda, então o mapa feito só com a data e depois
  completado com hora e cidade é o mesmo registro (a última versão fica).
- `vinculos`: liga o id anônimo do navegador (`visitante`) a um contato
  deixado para novidades. Um contato pode ter vários navegadores.
"""
import re
import sqlite3
import threading
from collections.abc import Callable
from datetime import datetime, timezone

_UUID = re.compile(r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$")

_ESQUEMA = """
CREATE TABLE IF NOT EXISTS mapas (
    id TEXT PRIMARY KEY,
    visitante TEXT,
    criado_em TEXT NOT NULL,
    atualizado_em TEXT NOT NULL,
    data TEXT NOT NULL,
    hora TEXT,
    local TEXT,
    lat REAL,
    lng REAL,
    fuso TEXT,
    calculos INTEGER NOT NULL DEFAULT 1
);
CREATE INDEX IF NOT EXISTS mapas_visitante ON mapas (visitante);
CREATE TABLE IF NOT EXISTS vinculos (
    contato TEXT NOT NULL,
    visitante TEXT NOT NULL,
    em TEXT NOT NULL,
    PRIMARY KEY (contato, visitante)
);
CREATE INDEX IF NOT EXISTS vinculos_visitante ON vinculos (visitante);
"""

_COLUNAS_MAPA = ("id", "criado_em", "atualizado_em", "data", "hora", "local", "lat", "lng", "fuso", "calculos")


def id_valido(valor: object) -> str | None:
    """O id em minúsculas se for um UUID; senão None."""
    if isinstance(valor, str) and _UUID.match(valor.strip().lower()):
        return valor.strip().lower()
    return None


def _agora() -> datetime:
    return datetime.now(timezone.utc)


class Historico:
    """Mapas do site e vínculos navegador ↔ contato; seguro entre threads."""

    def __init__(self, caminho: str, relogio: Callable[[], datetime] = _agora) -> None:
        self._relogio = relogio
        self._trava = threading.Lock()
        self._con = sqlite3.connect(caminho, check_same_thread=False, isolation_level=None)
        self._con.execute("PRAGMA journal_mode=WAL")
        self._con.execute("PRAGMA synchronous=NORMAL")
        self._con.executescript(_ESQUEMA)

    def _agora_iso(self) -> str:
        return self._relogio().isoformat(timespec="seconds")

    def registrar_mapa(
        self, mapa_id: str, visitante: str | None, data: str,
        hora: str | None, local: str | None, resolvido: dict | None,
    ) -> None:
        """Cria o mapa ou atualiza o mesmo id com os dados mais recentes."""
        resolvido = resolvido or {}
        agora = self._agora_iso()
        with self._trava:
            self._con.execute(
                "INSERT INTO mapas (id, visitante, criado_em, atualizado_em, data, hora, local, lat, lng, fuso) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?) "
                "ON CONFLICT (id) DO UPDATE SET "
                "visitante = COALESCE(excluded.visitante, visitante), atualizado_em = excluded.atualizado_em, "
                "data = excluded.data, hora = excluded.hora, local = excluded.local, "
                "lat = excluded.lat, lng = excluded.lng, fuso = excluded.fuso, calculos = calculos + 1",
                (mapa_id, visitante, agora, agora, data, hora, local,
                 resolvido.get("lat"), resolvido.get("lng"), resolvido.get("fuso")),
            )

    def vincular(self, contato: str, visitante: str) -> None:
        with self._trava:
            self._con.execute(
                "INSERT OR IGNORE INTO vinculos (contato, visitante, em) VALUES (?, ?, ?)",
                (contato, visitante, self._agora_iso()),
            )

    # ── exclusão (pedidos da seção "Seus direitos" da política) ──
    def apagar_contato(self, contato: str) -> dict:
        """Tira os vínculos do contato e os mapas dos navegadores só dele.

        Navegador ligado também a outro contato fica com os mapas: eles podem
        ser da outra pessoa.
        """
        with self._trava:
            visitantes = [v for (v,) in self._con.execute(
                "SELECT visitante FROM vinculos WHERE contato = ?", (contato,),
            ).fetchall()]
            self._con.execute("DELETE FROM vinculos WHERE contato = ?", (contato,))
            mapas = 0
            for v in visitantes:
                outros = self._con.execute(
                    "SELECT COUNT(*) FROM vinculos WHERE visitante = ?", (v,),
                ).fetchone()[0]
                if not outros:
                    mapas += self._con.execute("DELETE FROM mapas WHERE visitante = ?", (v,)).rowcount
        return {"visitantes": len(visitantes), "mapas": mapas}

    def apagar_mapa(self, mapa_id: str) -> int:
        with self._trava:
            return self._con.execute("DELETE FROM mapas WHERE id = ?", (mapa_id,)).rowcount

    def apagar_visitante(self, visitante: str) -> dict:
        with self._trava:
            mapas = self._con.execute("DELETE FROM mapas WHERE visitante = ?", (visitante,)).rowcount
            vinculos = self._con.execute("DELETE FROM vinculos WHERE visitante = ?", (visitante,)).rowcount
        return {"mapas": mapas, "vinculos": vinculos}

    def _mapas_de(self, visitantes: list[str]) -> list[dict]:
        if not visitantes:
            return []
        marcas = ",".join("?" * len(visitantes))
        linhas = self._con.execute(
            f"SELECT {', '.join(_COLUNAS_MAPA)} FROM mapas WHERE visitante IN ({marcas}) "
            "ORDER BY criado_em",
            visitantes,
        ).fetchall()
        return [dict(zip(_COLUNAS_MAPA, linha, strict=True)) for linha in linhas]

    def do_contato(self, contato: str) -> dict:
        """Navegadores ligados ao contato e todos os mapas feitos neles."""
        with self._trava:
            visitantes = [v for (v,) in self._con.execute(
                "SELECT visitante FROM vinculos WHERE contato = ? ORDER BY em", (contato,),
            ).fetchall()]
            return {"visitantes": visitantes, "mapas": self._mapas_de(visitantes)}

    def por_visitante(self) -> list[dict]:
        """Histórico de cada navegador: contatos ligados e mapas, do mais recente ao mais antigo."""
        with self._trava:
            visitantes = [v for (v,) in self._con.execute(
                "SELECT visitante FROM mapas WHERE visitante IS NOT NULL "
                "GROUP BY visitante ORDER BY MAX(atualizado_em) DESC",
            ).fetchall()]
            saida = []
            for v in visitantes:
                contatos = [c for (c,) in self._con.execute(
                    "SELECT contato FROM vinculos WHERE visitante = ? ORDER BY em", (v,),
                ).fetchall()]
                mapas = self._mapas_de([v])
                saida.append({
                    "visitante": v,
                    "contatos": contatos,
                    "primeiro_uso": mapas[0]["criado_em"] if mapas else None,
                    "ultimo_uso": max(m["atualizado_em"] for m in mapas) if mapas else None,
                    "mapas": mapas,
                })
            sem_visitante = self._con.execute(
                "SELECT COUNT(*) FROM mapas WHERE visitante IS NULL",
            ).fetchone()[0]
        return [*saida, *([{"visitante": None, "contatos": [], "mapas_sem_navegador": sem_visitante}]
                          if sem_visitante else [])]
