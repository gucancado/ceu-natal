# SPDX-License-Identifier: AGPL-3.0-or-later
"""Entrada dos formulários do site (`POST /mapa-rapido`) para cada técnica.

O corpo traz o nascimento de quem preenche (`data`, `hora`, `local`) e, conforme
a `tecnica`, os campos dela. Daqui sai a tool a chamar, os argumentos dela e o
nascimento de quem preenche, que é o único dado guardado no histórico: na
sinastria, a outra pessoa entra no cálculo e não é guardada.
"""
from typing import Any

# Teto de cada campo de texto: data, hora e cidade cabem com folga.
TAMANHO_MAX_CAMPO = 120
TECNICAS = ("natal", "transitos", "sinastria", "revolucao_solar")
_CAMPOS_NASCIMENTO = ("data", "hora", "local")


def _texto(fonte: dict, campo: str, obrigatorio: bool = False) -> str | None:
    """Campo de texto aparado; vazio vira None. Erro de tipo ou tamanho vira ValueError."""
    valor = fonte.get(campo)
    if valor is None or (isinstance(valor, str) and not valor.strip()):
        if obrigatorio:
            raise ValueError(f"Campo obrigatório: {campo}.")
        return None
    if not isinstance(valor, str) or len(valor) > TAMANHO_MAX_CAMPO:
        raise ValueError(f"Campo inválido: {campo}.")
    return valor.strip()


def _nascimento(fonte: dict, obrigatorio_hora_local: bool = False) -> dict[str, str]:
    """Data, hora e local de uma pessoa, só com os campos preenchidos."""
    if not isinstance(fonte, dict) or not isinstance(fonte.get("data"), str):
        raise ValueError("Envie um JSON com data (DD/MM/YYYY).")
    pessoa: dict[str, str] = {}
    for campo in _CAMPOS_NASCIMENTO:
        valor = _texto(fonte, campo, obrigatorio=obrigatorio_hora_local and campo != "data")
        if valor is not None:
            pessoa[campo] = valor
    if "data" not in pessoa:
        raise ValueError("Envie um JSON com data (DD/MM/YYYY).")
    return pessoa


def argumentos_do_site(corpo: Any) -> tuple[str, dict[str, Any], dict[str, str]]:
    """Devolve (tool, argumentos da tool, nascimento de quem preenche).

    Levanta ValueError com mensagem para a pessoa quando a entrada é inválida.
    """
    if not isinstance(corpo, dict):
        raise ValueError("Envie um JSON com data (DD/MM/YYYY).")
    tecnica = corpo.get("tecnica") or "natal"
    if tecnica not in TECNICAS:
        raise ValueError("Técnica inválida.")

    if tecnica == "natal":
        natal = _nascimento(corpo)
        return "calcular_mapa_natal", dict(natal), natal

    if tecnica == "transitos":
        natal = _nascimento(corpo)
        data_transito = _texto(corpo, "data_transito", obrigatorio=True)
        return "calcular_transitos", {"natal": natal, "data_transito": data_transito}, natal

    if tecnica == "sinastria":
        natal = _nascimento(corpo)
        bruto = corpo.get("outra")
        outra = _nascimento(bruto if isinstance(bruto, dict) else {})
        # Rótulos fixos: sem nome, as duas viriam como "Anônimo" e o resultado não diria quem é quem.
        argumentos = {"pessoa_a": {**natal, "nome": "pessoa 1"}, "pessoa_b": {**outra, "nome": "pessoa 2"}}
        return "calcular_sinastria", argumentos, natal

    # revolucao_solar: hora e local de nascimento são necessários para o mapa da revolução.
    natal = _nascimento(corpo, obrigatorio_hora_local=True)
    ano = corpo.get("ano")
    if isinstance(ano, str) and ano.strip().isdigit():
        ano = int(ano.strip())
    if not isinstance(ano, int) or isinstance(ano, bool):
        raise ValueError("Campo inválido: ano.")
    local_revolucao = _texto(corpo, "local_revolucao") or natal["local"]
    return "calcular_revolucao_solar", {"natal": natal, "ano": ano, "local_revolucao": local_revolucao}, natal
