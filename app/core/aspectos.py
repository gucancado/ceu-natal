# SPDX-License-Identifier: AGPL-3.0-or-later
"""
Cálculo de aspectos com orbes definidos no spec, sem depender da lógica
interna do Kerykeion (que tem orbes diferentes).
"""
from typing import Optional

# (nome_pt, angulo_graus, natureza)
ASPECTOS_DEF = [
    ("conjuncao",      0.0,   "neutro"),
    ("oposicao",       180.0, "tensao"),
    ("trigono",        120.0, "harmonico"),
    ("quadratura",     90.0,  "tensao"),
    ("sextil",         60.0,  "harmonico"),
    ("quintil",        72.0,  "neutro"),
    ("inconjuncao",    150.0, "tensao"),
    ("semi_sextil",    30.0,  "neutro"),
]

LUMINARES = {"sol", "lua"}

# Abaixo deste orbe o aspecto é marcado como `exato` na saída.
ORBE_EXATO = 0.5


def orbe_para(tipo: str, p1_nome: str, p2_nome: str) -> float:
    """
    Orbes (graus):
      conjunção/oposição: 8 com luminares, 6 demais
      trigono/sextil: 4
      quadratura: 6
      menores (quintil, inconjunção, semi_sextil): 2
    """
    tem_luminar = p1_nome in LUMINARES or p2_nome in LUMINARES
    if tipo in ("conjuncao", "oposicao"):
        return 8.0 if tem_luminar else 6.0
    if tipo == "quadratura":
        return 6.0
    if tipo in ("trigono", "sextil"):
        return 4.0
    return 2.0  # quintil, inconjuncao, semi_sextil


def _diferenca_circular(a: float, b: float) -> float:
    """Menor diferença angular entre duas posições (0..180)."""
    d = abs(a - b) % 360.0
    return d if d <= 180.0 else 360.0 - d


def _aplicando(p1_abs: float, p1_speed: Optional[float],
               p2_abs: float, p2_speed: Optional[float], alvo: float) -> Optional[bool]:
    """
    Determina se o aspecto está aplicando (planetas se aproximando do ângulo exato).
    Compara |sep| atual vs estimativa após pequeno avanço de tempo.
    Um lado fixo (natal em trânsitos, progressões e revoluções) chega com
    `speed=0.0` — ver `coletar_pontos(..., fixo=True)` — e só o outro se move.
    Retorna None se velocidades não estiverem disponíveis.
    """
    if p1_speed is None or p2_speed is None:
        return None
    sep_now = _diferenca_circular(p1_abs, p2_abs)
    delta_t = 1.0 / 24.0  # 1 hora (em dias)
    p1_next = (p1_abs + p1_speed * delta_t) % 360.0
    p2_next = (p2_abs + p2_speed * delta_t) % 360.0
    sep_next = _diferenca_circular(p1_next, p2_next)
    return abs(sep_next - alvo) < abs(sep_now - alvo)


def _aspecto_entre(p1: dict, p2: dict) -> Optional[dict]:
    """Aspecto formado pelo par (o de menor ângulo na ordem de `ASPECTOS_DEF`), ou None.

    Um par só forma um tipo de aspecto. Chaves: planeta_a, planeta_b, tipo,
    orbe, aplicando, exato, natureza.
    """
    sep = _diferenca_circular(p1["abs_pos"], p2["abs_pos"])
    for tipo, angulo, natureza in ASPECTOS_DEF:
        orbe = abs(sep - angulo)
        if orbe <= orbe_para(tipo, p1["nome"], p2["nome"]):
            return {
                "planeta_a": p1["nome"],
                "planeta_b": p2["nome"],
                "tipo": tipo,
                "orbe": round(orbe, 4),
                "aplicando": _aplicando(
                    p1["abs_pos"], p1.get("speed"),
                    p2["abs_pos"], p2.get("speed"),
                    angulo,
                ),
                "exato": orbe < ORBE_EXATO,
                "natureza": natureza,
            }
    return None


def calcular_aspectos(pontos: list[dict]) -> list[dict]:
    """
    Recebe lista de pontos no formato:
      {"nome": str, "abs_pos": float, "speed": float|None}
    Retorna lista de aspectos {planeta_a, planeta_b, tipo, orbe, aplicando, exato, natureza}.
    """
    resultado = []
    for i, p1 in enumerate(pontos):
        for p2 in pontos[i + 1:]:
            aspecto = _aspecto_entre(p1, p2)
            if aspecto:
                resultado.append(aspecto)
    return sorted(resultado, key=lambda x: x["orbe"])


def calcular_aspectos_cruzados(pontos_a: list[dict], pontos_b: list[dict],
                               rotulo_a: str, rotulo_b: str) -> list[dict]:
    """
    Aspectos cruzados entre dois conjuntos de pontos (sinastria, trânsito x
    natal, progredido x natal, revolução x natal). Cada item: ponto de A vs
    ponto de B (não calcula intra-conjunto), com `pessoa_a`/`pessoa_b` = rótulos.
    """
    resultado = []
    for p1 in pontos_a:
        for p2 in pontos_b:
            aspecto = _aspecto_entre(p1, p2)
            if aspecto:
                resultado.append({
                    "planeta_a": aspecto.pop("planeta_a"),
                    "pessoa_a": rotulo_a,
                    "planeta_b": aspecto.pop("planeta_b"),
                    "pessoa_b": rotulo_b,
                    **aspecto,
                })
    return sorted(resultado, key=lambda x: x["orbe"])


# Nome histórico (sinastria); mesma função.
calcular_aspectos_sinastria = calcular_aspectos_cruzados


def renomear(aspectos: list[dict], chave_a: str, chave_b: str) -> list[dict]:
    """Aspectos cruzados com `planeta_a`/`planeta_b` renomeados para a semântica
    da técnica (ex.: planeta_transito/planeta_natal), sem `pessoa_a`/`pessoa_b`."""
    return [
        {
            chave_a: a["planeta_a"],
            chave_b: a["planeta_b"],
            "tipo": a["tipo"],
            "orbe": a["orbe"],
            "aplicando": a["aplicando"],
            "exato": a["exato"],
            "natureza": a["natureza"],
        }
        for a in aspectos
    ]


def listar_tipos_aspectos() -> list[dict]:
    """Lista os aspectos suportados com ângulos, orbes e natureza."""
    saida = []
    for tipo, angulo, natureza in ASPECTOS_DEF:
        saida.append({
            "tipo": tipo,
            "angulo": angulo,
            "orbe_padrao": orbe_para(tipo, "outro", "outro"),
            "orbe_com_luminar": orbe_para(tipo, "sol", "outro"),
            "orbe_exato": ORBE_EXATO,
            "natureza": natureza,
        })
    return saida


def casa_de_longitude(longitude_abs: float, cuspides: list[float]) -> int:
    """
    Dada a longitude absoluta (0..360) e as 12 cúspides em ordem, retorna
    o número da casa (1..12): a casa é a da cúspide anterior à longitude.
    Vale para qualquer sistema de casas — só depende das cúspides recebidas.
    """
    longitude_abs = longitude_abs % 360.0
    for i in range(12):
        inicio = cuspides[i] % 360.0
        fim = cuspides[(i + 1) % 12] % 360.0
        if inicio <= fim:
            if inicio <= longitude_abs < fim:
                return i + 1
        else:  # cruza 0°
            if longitude_abs >= inicio or longitude_abs < fim:
                return i + 1
    return 12
