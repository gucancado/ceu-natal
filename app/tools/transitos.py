"""
Trânsitos planetários — calcula a posição atual dos planetas em relação a
um mapa natal. Aspectos cruzados, casa natal de cada trânsito e curadoria
de trânsitos lentos relevantes.
"""
from typing import Optional

from app.core.aspectos import (
    calcular_aspectos_sinastria,
    casa_de_longitude,
)
from app.core.formatter import formatar_planeta
from app.core.kerykeion import (
    casas_iter,
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

# Planetas considerados "lentos" — trânsitos deles costumam marcar
# fases longas e merecem destaque.
PLANETAS_LENTOS = {"saturno", "urano", "netuno", "plutao", "chiron"}

# Luminares e planetas pessoais — para a contagem na síntese.
LUMINARES = {"sol", "lua"}
PESSOAIS = {"mercurio", "venus", "marte"}


def _build_natal(natal: dict, sistema_id: str):
    """Cria o subject natal a partir do dict de entrada."""
    data = natal.get("data")
    if not data:
        raise ValueError("Campo 'data' obrigatório no objeto natal.")

    hora = natal.get("hora")
    local = natal.get("local")
    nome = natal.get("nome") or "Anônimo"

    dia, mes, ano = parse_data(data)
    h, m = parse_hora(hora)
    cidade, nacao = parse_local(local)

    tem_hora = h is not None
    tem_local = cidade is not None or (
        natal.get("lat") is not None and natal.get("lng") is not None
    )

    if not (tem_hora and tem_local):
        raise ValueError(
            "Trânsitos exigem hora e local de nascimento — sem isso, casas "
            "natais não podem ser calculadas."
        )

    subject = criar_subject(
        nome=nome,
        ano=ano, mes=mes, dia=dia,
        hora=h, minuto=m,
        cidade=cidade, nacao=nacao,
        lat=natal.get("lat"), lng=natal.get("lng"), tz_str=natal.get("tz_str"),
        sistema_casas=sistema_id,
    )
    return subject, nome


def _build_transito(data_t: str, hora_t: Optional[str], local_t: Optional[str],
                    sistema_id: str):
    """Cria o subject do instante de trânsito.

    Defaults:
      - hora omitida → 12:00 UTC
      - local omitido → Greenwich (0,0, UTC)
    """
    dia, mes, ano = parse_data(data_t)
    h, m = parse_hora(hora_t)

    if h is None:
        h, m = 12, 0

    cidade, nacao = parse_local(local_t)
    if cidade:
        return criar_subject(
            nome="Transito",
            ano=ano, mes=mes, dia=dia, hora=h, minuto=m,
            cidade=cidade, nacao=nacao,
            sistema_casas=sistema_id,
        )

    # Sem local: Greenwich/UTC. Se a hora foi explícita também sem local,
    # tratamos a hora como UTC (consistente com defaults astrológicos).
    return criar_subject(
        nome="Transito",
        ano=ano, mes=mes, dia=dia, hora=h, minuto=m,
        lat=0.0, lng=0.0, tz_str="UTC",
        sistema_casas=sistema_id,
    )


def _coletar_pontos_completos(subject) -> list[dict]:
    """Lista de pontos para cálculo de aspectos: 10 planetas + nodos + Quíron."""
    pontos = []
    for nome_pt, ponto in planetas_iter(subject):
        pontos.append({
            "nome": nome_pt,
            "abs_pos": ponto.abs_pos,
            "speed": ponto.speed,
        })
    for nome_pt, ponto in pontos_sensiveis_iter(subject):
        pontos.append({
            "nome": nome_pt,
            "abs_pos": ponto.abs_pos,
            "speed": ponto.speed,
        })
    return pontos


def _formatar_planetas_em_transito(subject_t, cuspides_natais: list[float]) -> dict:
    """Cada planeta em trânsito recebe casa_natal (em qual casa do mapa natal cai)."""
    saida = {}
    for nome_pt, ponto in planetas_iter(subject_t):
        base = formatar_planeta(ponto, incluir_casa=False)
        base["casa_natal"] = casa_de_longitude(ponto.abs_pos, cuspides_natais)
        saida[nome_pt] = base
    return saida


def destacar_transitos_lentos(aspectos: list[dict], orbe_max: float = 2.0) -> list[dict]:
    """Filtra aspectos onde o planeta em trânsito é lento (Sat, Ur, Net, Plu,
    Quíron) e o orbe é menor que `orbe_max`. Retorno enxuto pra síntese."""
    return [
        {
            "planeta_transito": a["planeta_a"],
            "planeta_natal": a["planeta_b"],
            "tipo": a["tipo"],
            "orbe": a["orbe"],
        }
        for a in aspectos
        if a["planeta_a"] in PLANETAS_LENTOS and a["orbe"] < orbe_max
    ]


def _renomear_aspectos(aspectos_sinastria: list[dict]) -> list[dict]:
    """Adapta o formato de calcular_aspectos_sinastria para a semântica
    transito → natal. Substitui 'pessoa_a/pessoa_b' por 'planeta_transito/
    planeta_natal' e remove os campos de pessoa que não fazem sentido aqui."""
    saida = []
    for a in aspectos_sinastria:
        saida.append({
            "planeta_transito": a["planeta_a"],
            "planeta_natal": a["planeta_b"],
            "tipo": a["tipo"],
            "orbe": a["orbe"],
            "aplicando": a["aplicando"],
            "exato": a["exato"],
            "natureza": a["natureza"],
        })
    return saida


def _sintese(aspectos: list[dict], lentos_destacados: list[dict]) -> dict:
    aplicando = sum(1 for a in aspectos if a["aplicando"] is True)
    separando = sum(1 for a in aspectos if a["aplicando"] is False)
    para_luminares = sum(1 for a in aspectos if a["planeta_natal"] in LUMINARES)
    para_pessoais = sum(1 for a in aspectos if a["planeta_natal"] in PESSOAIS)
    return {
        "aspectos_aplicando": aplicando,
        "aspectos_separando": separando,
        "transitos_para_luminares": para_luminares,
        "transitos_para_pessoais": para_pessoais,
        "transitos_lentos_destacados": lentos_destacados,
    }


def calcular_transitos(
    *,
    natal: dict,
    data_transito: str,
    hora_transito: Optional[str] = None,
    local_transito: Optional[str] = None,
    orbes_aplicados: Optional[float] = None,  # placeholder p/ futuro: multiplicador de orbe
    sistema_casas: Optional[str] = None,
) -> dict:
    """Trânsitos planetários relativos a um mapa natal."""
    sistema_id = validar_sistema_casas(sistema_casas)

    subject_natal, nome_natal = _build_natal(natal, sistema_id)
    subject_t = _build_transito(data_transito, hora_transito, local_transito, sistema_id)

    pontos_t = _coletar_pontos_completos(subject_t)
    pontos_n = _coletar_pontos_completos(subject_natal)

    cuspides_natais = [c.abs_pos for _, c in casas_iter(subject_natal)]

    aspectos_raw = calcular_aspectos_sinastria(
        pontos_t, pontos_n, "transito", "natal",
    )
    # Destaque opera sobre o formato bruto (planeta_a/planeta_b)
    lentos = destacar_transitos_lentos(aspectos_raw, orbe_max=2.0)
    aspectos = _renomear_aspectos(aspectos_raw)

    return {
        "natal": {
            "nome": nome_natal,
            "data": natal.get("data"),
            "hora": natal.get("hora"),
            "local": natal.get("local"),
        },
        "transito": {
            "data": data_transito,
            "hora": hora_transito,
            "local": local_transito,
        },
        "planetas_em_transito": _formatar_planetas_em_transito(subject_t, cuspides_natais),
        "aspectos_transito_natal": aspectos,
        "sintese": _sintese(aspectos, lentos),
    }
