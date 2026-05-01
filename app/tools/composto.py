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
from app.core.formatter import (
    elemento_pt,
    formatar_grau,
    qualidade_pt,
    signo_pt,
)
from app.core.kerykeion import (
    criar_subject,
    planetas_iter,
    pontos_sensiveis_iter,
)
from app.core.validators import (
    parse_data,
    parse_hora,
    parse_local,
    validar_sistema_casas,
)


# ─────────────────────────────────────────────────────────────
# Midpoint matemático
# ─────────────────────────────────────────────────────────────
def midpoint_longitude(a: float, b: float) -> float:
    """Ponto médio mais curto entre duas longitudes (0..360°).

    Trata wrap-around: midpoint(350°, 10°) = 0°, não 180°.
    Pares antípodas (diferença de exatamente 180°) ficam em (a + 90) % 360.
    """
    a = a % 360.0
    b = b % 360.0
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
# Construção dos subjects A/B (idem sinastria)
# ─────────────────────────────────────────────────────────────
def _build_subject(pessoa: dict, sistema_id: str):
    data = pessoa.get("data")
    if not data:
        raise ValueError("Campo 'data' obrigatório em cada pessoa.")

    dia, mes, ano = parse_data(data)
    h, m = parse_hora(pessoa.get("hora"))
    cidade, nacao = parse_local(pessoa.get("local"))

    tem_local = cidade is not None or (
        pessoa.get("lat") is not None and pessoa.get("lng") is not None
    )

    return criar_subject(
        nome=pessoa.get("nome") or "Anônimo",
        ano=ano, mes=mes, dia=dia,
        hora=h if h is not None else 12,
        minuto=m if m is not None else 0,
        cidade=cidade, nacao=nacao,
        lat=pessoa.get("lat"), lng=pessoa.get("lng"), tz_str=pessoa.get("tz_str"),
        sistema_casas=sistema_id,
    ), tem_local


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

    subject_a, tem_local_a = _build_subject(pessoa_a, sistema_id)
    subject_b, tem_local_b = _build_subject(pessoa_b, sistema_id)

    # Coleta longitudes de A e B por nome em PT
    pos_a, pos_b = {}, {}
    for nome_pt, ponto in planetas_iter(subject_a):
        pos_a[nome_pt] = ponto.abs_pos
    for nome_pt, ponto in planetas_iter(subject_b):
        pos_b[nome_pt] = ponto.abs_pos
    for nome_pt, ponto in pontos_sensiveis_iter(subject_a):
        pos_a[nome_pt] = ponto.abs_pos
    for nome_pt, ponto in pontos_sensiveis_iter(subject_b):
        pos_b[nome_pt] = ponto.abs_pos

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
        mid = midpoint_longitude(pos_a[nome_pt], pos_b[nome_pt])
        pontos_sensiveis_compostos[nome_pt] = _formatar_ponto_composto(mid)
        pontos_aspectos.append({"nome": nome_pt, "abs_pos": mid, "speed": None})

    # Ângulos: midpoint dos ASCs e MCs (só faz sentido se ambos têm horário+local)
    angulos_compostos = {}
    if tem_local_a and tem_local_b:
        asc_mid = midpoint_longitude(subject_a.first_house.abs_pos,
                                     subject_b.first_house.abs_pos)
        mc_mid = midpoint_longitude(subject_a.tenth_house.abs_pos,
                                    subject_b.tenth_house.abs_pos)
        angulos_compostos = {
            "ascendente":  _formatar_ponto_composto(asc_mid),
            "meio_do_ceu": _formatar_ponto_composto(mc_mid),
        }

    # Aspectos internos do composto (sem velocidade → aplicando=None)
    aspectos = calcular_aspectos(pontos_aspectos)

    return {
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


def _sintese_composto(planetas_compostos: dict) -> dict:
    """Distribuição de elementos e detecção de stelliums por signo."""
    elementos = Counter()
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
