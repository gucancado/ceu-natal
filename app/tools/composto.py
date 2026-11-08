# SPDX-License-Identifier: AGPL-3.0-or-later
"""
Mapa composto (composite chart) pelo método de midpoints.

DECISÃO DE DESIGN: existem dois métodos populares — Davison (recalcula um
mapa para o instante/local médios entre os dois nascimentos) e Midpoint
(pega o ponto médio das longitudes planetárias). Implementamos APENAS o
Midpoint, mais comum e que não exige instante/local definido — por isso
não retornamos casas, só planetas, ângulos e aspectos.
"""
from collections import Counter
from typing import Optional

from app.core.aspectos import calcular_aspectos
from app.core.entrada import EntradaNascimento
from app.core.formatter import (
    elemento_pt,
    formatar_grau,
    qualidade_pt,
    signo_pt,
)
from app.core.kerykeion import coletar_pontos
from app.core.validators import validar_sistema_casas


# ─────────────────────────────────────────────────────────────
# Midpoint matemático
# ─────────────────────────────────────────────────────────────
def midpoint_longitude(a: float, b: float) -> float:
    """Ponto médio mais curto entre duas longitudes (0..360°).

    Trata wrap-around: midpoint(350°, 10°) = 0°, não 180°.
    Comutativo: os ângulos são ordenados antes, então a ordem dos argumentos
    não muda o resultado. Pares antípodas (diferença de exatamente 180°) ficam
    em (menor + 90) % 360.
    """
    a, b = sorted((a % 360.0, b % 360.0))
    diff = (b - a) % 360.0
    if diff > 180.0:
        return (a + diff / 2 - 180.0) % 360.0
    return (a + diff / 2) % 360.0


# ─────────────────────────────────────────────────────────────
# Helpers de signo / casa a partir de longitude pura
# ─────────────────────────────────────────────────────────────
_ORDEM_SIGNOS = ["Ari", "Tau", "Gem", "Can", "Leo", "Vir",
                 "Lib", "Sco", "Sag", "Cap", "Aqu", "Pis"]

_ELEMENTOS_POR_SIGNO = {
    "Ari": "Fire", "Leo": "Fire", "Sag": "Fire",
    "Tau": "Earth", "Vir": "Earth", "Cap": "Earth",
    "Gem": "Air", "Lib": "Air", "Aqu": "Air",
    "Can": "Water", "Sco": "Water", "Pis": "Water",
}

_QUALIDADES_POR_SIGNO = {
    "Ari": "Cardinal", "Can": "Cardinal", "Lib": "Cardinal", "Cap": "Cardinal",
    "Tau": "Fixed", "Leo": "Fixed", "Sco": "Fixed", "Aqu": "Fixed",
    "Gem": "Mutable", "Vir": "Mutable", "Sag": "Mutable", "Pis": "Mutable",
}


def _signo_de_longitude(longitude: float) -> str:
    idx = int((longitude % 360.0) // 30)
    return _ORDEM_SIGNOS[idx]


def _formatar_ponto_composto(longitude: float) -> dict:
    longitude = longitude % 360.0
    grau_no_signo = longitude % 30.0
    sign = _signo_de_longitude(longitude)
    return {
        "signo": signo_pt(sign),
        "grau": formatar_grau(grau_no_signo),
        "grau_decimal": round(grau_no_signo, 4),
        "posicao_absoluta": round(longitude, 4),
        "elemento": elemento_pt(_ELEMENTOS_POR_SIGNO[sign]),
        "qualidade": qualidade_pt(_QUALIDADES_POR_SIGNO[sign]),
    }


# ─────────────────────────────────────────────────────────────
# Composto principal
# ─────────────────────────────────────────────────────────────
def calcular_mapa_composto(
    *,
    pessoa_a: dict,
    pessoa_b: dict,
    sistema_casas: Optional[str] = None,
) -> dict:
    sistema_id = validar_sistema_casas(sistema_casas)

    entrada_a = EntradaNascimento.de_dict(pessoa_a, rotulo="pessoa_a").resolvida()
    subject_a = entrada_a.subject(sistema_id)
    entrada_b = EntradaNascimento.de_dict(pessoa_b, rotulo="pessoa_b").resolvida()
    subject_b = entrada_b.subject(sistema_id)
    completo_a = entrada_a.casas_confiaveis
    completo_b = entrada_b.casas_confiaveis

    # Longitudes de A e B por nome em PT (planetas + pontos sensíveis)
    pos_a = {p["nome"]: p["abs_pos"] for p in coletar_pontos(subject_a)}
    pos_b = {p["nome"]: p["abs_pos"] for p in coletar_pontos(subject_b)}

    # Midpoints de cada planeta + ponto sensível
    planetas_compostos: dict = {}
    pontos_aspectos: list[dict] = []

    nomes_planetas = ["sol", "lua", "mercurio", "venus", "marte",
                      "jupiter", "saturno", "urano", "netuno", "plutao"]
    nomes_pontos_sensiveis = ["nodo_norte_verdadeiro", "nodo_sul_verdadeiro", "chiron"]

    for nome_pt in nomes_planetas:
        mid = midpoint_longitude(pos_a[nome_pt], pos_b[nome_pt])
        planetas_compostos[nome_pt] = _formatar_ponto_composto(mid)
        pontos_aspectos.append({"nome": nome_pt, "abs_pos": mid, "speed": None})

    pontos_sensiveis_compostos: dict = {}
    for nome_pt in nomes_pontos_sensiveis:
        if nome_pt not in pos_a or nome_pt not in pos_b:
            continue  # ponto sem efeméride na data (ver `pontos_sensiveis_iter`)
        mid = midpoint_longitude(pos_a[nome_pt], pos_b[nome_pt])
        pontos_sensiveis_compostos[nome_pt] = _formatar_ponto_composto(mid)
        pontos_aspectos.append({"nome": nome_pt, "abs_pos": mid, "speed": None})

    # Ângulos: midpoint dos ASCs e MCs (só faz sentido se ambos têm horário+local)
    angulos_compostos = {}
    if completo_a and completo_b:
        asc_mid = midpoint_longitude(subject_a.ascendant.abs_pos,
                                     subject_b.ascendant.abs_pos)
        mc_mid = midpoint_longitude(subject_a.medium_coeli.abs_pos,
                                    subject_b.medium_coeli.abs_pos)
        angulos_compostos = {
            "ascendente":  _formatar_ponto_composto(asc_mid),
            "meio_do_ceu": _formatar_ponto_composto(mc_mid),
        }

    # Aspectos internos do composto (sem velocidade → aplicando=None)
    aspectos = calcular_aspectos(pontos_aspectos)

    resultado = {
        "pessoa_a": {"nome": pessoa_a.get("nome"), "data": pessoa_a.get("data")},
        "pessoa_b": {"nome": pessoa_b.get("nome"), "data": pessoa_b.get("data")},
        "tipo_composto": "midpoint",
        "planetas_compostos": planetas_compostos,
        "pontos_sensiveis_compostos": pontos_sensiveis_compostos,
        "angulos_compostos": angulos_compostos,
        "aspectos_compostos": aspectos,
        "casas": None,  # composto midpoint não tem casas
        "sintese": _sintese_composto(planetas_compostos),
    }
    entradas = (entrada_a, entrada_b)
    sem_dados = [e.nome for e in entradas if not (e.tem_hora and e.tem_local)]
    polares = [e.nome for e in entradas if e.tem_hora and e.tem_local and not e.casas_confiaveis]
    avisos = []
    if sem_dados:
        avisos.append(f"Ângulos compostos omitidos: hora ou local de nascimento ausente em {' e '.join(sem_dados)}.")
    if polares:
        avisos.append(f"Ângulos compostos omitidos: latitude acima de 66° em {' e '.join(polares)}.")
    if avisos:
        resultado["aviso"] = " ".join(avisos)
    return resultado


def _sintese_composto(planetas_compostos: dict) -> dict:
    """Distribuição de elementos e detecção de stelliums por signo."""
    elementos: Counter[str] = Counter()
    por_signo: dict = {}
    for nome, p in planetas_compostos.items():
        elementos[p["elemento"]] += 1
        por_signo.setdefault(p["signo"], []).append(nome)

    stelliums = [
        {"tipo": "signo", "valor": signo, "planetas": planetas}
        for signo, planetas in por_signo.items()
        if len(planetas) >= 3
    ]

    return {
        "distribuicao_elementos": dict(elementos),
        "stelliums_compostos": stelliums,
    }
