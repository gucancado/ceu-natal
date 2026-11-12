# SPDX-License-Identifier: AGPL-3.0-or-later
"""
Contatos para avisos de novidades, deixados por quem quiser no site.

Guarda só o contato (e-mail ou telefone), o tipo e a data do cadastro, uma
linha JSON por contato. Nada de dados de nascimento: o formulário envia o
contato num pedido separado do cálculo.
"""
import json
import re
import threading
from datetime import datetime, timezone
from pathlib import Path

_EMAIL = re.compile(r"^[^@\s]{1,64}@[^@\s]+\.[^@\s]{2,}$")
_SEPARADORES_FONE = re.compile(r"[\s().\-]")

ERRO_CONTATO = "Informe um e-mail ou um telefone com DDD."


def normalizar_contato(bruto: str) -> tuple[str, str]:
    """Devolve (tipo, contato normalizado) ou levanta ValueError.

    E-mail vai em minúsculas. Telefone vira +<dígitos>; sem código de país e
    com 10 ou 11 dígitos, assume o Brasil (+55).
    """
    texto = bruto.strip()
    if not texto or len(texto) > 254:
        raise ValueError(ERRO_CONTATO)
    if "@" in texto:
        if not _EMAIL.match(texto):
            raise ValueError(ERRO_CONTATO)
        return "email", texto.lower()
    fone = _SEPARADORES_FONE.sub("", texto)
    internacional = fone.startswith("+")
    digitos = fone[1:] if internacional else fone
    if not digitos.isdigit():
        raise ValueError(ERRO_CONTATO)
    if not internacional and len(digitos) in (10, 11):
        digitos = "55" + digitos
    if not 10 <= len(digitos) <= 15:
        raise ValueError(ERRO_CONTATO)
    return "telefone", "+" + digitos


class RegistroContatos:
    """Arquivo JSONL de contatos; ignora contato repetido."""

    def __init__(self, caminho: str) -> None:
        self.caminho = Path(caminho)
        self._trava = threading.Lock()

    def registrar(self, tipo: str, contato: str) -> bool:
        """Grava o contato; devolve False se ele já estava no arquivo."""
        with self._trava:
            if self.caminho.exists():
                with self.caminho.open(encoding="utf-8") as arquivo:
                    for linha in arquivo:
                        try:
                            if json.loads(linha).get("contato") == contato:
                                return False
                        except ValueError:
                            continue
            registro = {
                "contato": contato,
                "tipo": tipo,
                "em": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            }
            with self.caminho.open("a", encoding="utf-8") as arquivo:
                arquivo.write(json.dumps(registro, ensure_ascii=False) + "\n")
            return True

    def listar(self) -> list[dict]:
        """Todos os contatos, na ordem do cadastro; linhas corrompidas são puladas."""
        with self._trava:
            if not self.caminho.exists():
                return []
            registros = []
            with self.caminho.open(encoding="utf-8") as arquivo:
                for linha in arquivo:
                    try:
                        item = json.loads(linha)
                    except ValueError:
                        continue
                    if isinstance(item, dict):
                        registros.append(item)
            return registros
