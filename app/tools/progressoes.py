"""
Progressões secundárias — técnica "um dia após o nascimento = um ano de vida".

DECISÃO DE DESIGN: progressões secundárias clássicas calculam o mapa para
`data_nascimento + N dias`, onde N = idade em anos (fração inclusa). Não
implementamos via método nativo do Kerykeion porque a versão 5.x não expõe
um método dedicado e estável para isso — fazemos manualmente criando um
segundo AstrologicalSubject com a data progredida (dia + idade em anos).

Usar `(data_alvo - data_natal).days` *direto* daria o mapa do dia alvo
(trânsitos), não progressões. Por isso convertemos:
    anos_vividos = (data_alvo - data_natal).total_seconds() / (365.25 * 86400)
    data_progredida = data_natal + timedelta(days=anos_vividos)
"""
from datetime import datetime, timedelta
from typing import Optional

from app.core.aspectos import calcular_aspectos_sinastria, casa_de_longitude
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

SEGUNDOS_POR_ANO_TROPICO = 365.25 * 86400.0


def _datetime_natal(natal: dict) -> datetime:
    """Constrói datetime do nascimento (assume hora 12:00 se omitida — só
    afeta o ponto exato dentro do dia, não os anos vividos)."""
    dia, mes, ano = parse_data(natal["data"])
    h, m = parse_hora(natal.get("hora"))
    return datetime(
        ano, mes, dia,
        h if h is not None else 12,
        m if m is not None else 0,
    )


def computar_data_progredida(data_natal: datetime, data_alvo: datetime) -> datetime:
    """Aplica a regra '1 dia = 1 ano': retorna data_natal + idade_em_anos dias."""
    delta = data_alvo - data_natal
    anos_vividos = delta.total_seconds() / SEGUNDOS_POR_ANO_TROPICO
    return data_natal + timedelta(days=anos_vividos)


def _flags_signo(grau_no_signo: float) -> dict:
    """Sinaliza ingresso recente (<1°) ou mudança iminente (>29°) num signo."""
    return {
        "ingresso_recente": grau_no_signo < 1.0,
        "mudanca_iminente": grau_no_signo > 29.0,
    }


def _build_subject_progredido(natal: dict, data_progredida: datetime, sistema_id: str):
    """Cria o subject progredido — mesmo local do natal, data deslocada."""
    cidade, nacao = parse_local(natal.get("local"))

    return criar_subject(
        nome=(natal.get("nome") or "Anônimo") + " (progredido)",
        ano=data_progredida.year,
        mes=data_progredida.month,
        dia=data_progredida.day,
        hora=data_progredida.hour,
        minuto=data_progredida.minute,
        cidade=cidade, nacao=nacao,
        lat=natal.get("lat"), lng=natal.get("lng"), tz_str=natal.get("tz_str"),
        sistema_casas=sistema_id,
    )


def _build_subject_natal(natal: dict, sistema_id: str):
    data = natal.get("data")
    if not data:
        raise ValueError("Campo 'data' obrigatório no objeto natal.")

    dia, mes, ano = parse_data(data)
    h, m = parse_hora(natal.get("hora"))
    cidade, nacao = parse_local(natal.get("local"))

    tem_hora = h is not None
    tem_local = cidade is not None or (
        natal.get("lat") is not None and natal.get("lng") is not None
    )

    if not (tem_hora and tem_local):
        raise ValueError(
            "Progressões exigem hora e local de nascimento — sem isso, "
            "casas natais não podem ser calculadas."
        )

    return criar_subject(
        nome=natal.get("nome") or "Anônimo",
        ano=ano, mes=mes, dia=dia,
        hora=h, minuto=m,
        cidade=cidade, nacao=nacao,
        lat=natal.get("lat"), lng=natal.get("lng"), tz_str=natal.get("tz_str"),
        sistema_casas=sistema_id,
    )


def _coletar_pontos(subject) -> list[dict]:
    pontos = []
    for nome_pt, ponto in planetas_iter(subject):
        pontos.append({"nome": nome_pt, "abs_pos": ponto.abs_pos, "speed": ponto.speed})
    for nome_pt, ponto in pontos_sensiveis_iter(subject):
        pontos.append({"nome": nome_pt, "abs_pos": ponto.abs_pos, "speed": ponto.speed})
    return pontos


def _formatar_progredidos(subject_p, cuspides_natais: list[float]) -> dict:
    saida = {}
    for nome_pt, ponto in planetas_iter(subject_p):
        base = formatar_planeta(ponto, incluir_casa=False)
        base["casa_natal"] = casa_de_longitude(ponto.abs_pos, cuspides_natais)
        base.update(_flags_signo(ponto.position))
        saida[nome_pt] = base
    return saida


def _renomear_aspectos(aspectos_sinastria: list[dict]) -> list[dict]:
    saida = []
    for a in aspectos_sinastria:
        saida.append({
            "planeta_progredido": a["planeta_a"],
            "planeta_natal": a["planeta_b"],
            "tipo": a["tipo"],
            "orbe": a["orbe"],
            "aplicando": a["aplicando"],
            "exato": a["exato"],
            "natureza": a["natureza"],
        })
    return saida


_ORDEM_SIGNOS = ["Ari", "Tau", "Gem", "Can", "Leo", "Vir",
                 "Lib", "Sco", "Sag", "Cap", "Aqu", "Pis"]


def _destaques(planetas_progredidos: dict, subject_p) -> dict:
    from app.core.formatter import SIGNOS_PT  # importação local p/ evitar ciclo

    lua = planetas_progredidos["lua"]
    sol = planetas_progredidos["sol"]

    mudancas = []
    for nome_pt, ponto in planetas_iter(subject_p):
        if ponto.position > 29.0:
            idx = _ORDEM_SIGNOS.index(ponto.sign) if ponto.sign in _ORDEM_SIGNOS else 0
            proximo = _ORDEM_SIGNOS[(idx + 1) % 12]
            mudancas.append({
                "planeta": nome_pt,
                "do_signo": SIGNOS_PT.get(ponto.sign, ponto.sign),
                "para_signo": SIGNOS_PT.get(proximo, proximo),
            })

    return {
        "lua_progredida": {
            "signo": lua["signo"],
            "casa_natal": lua["casa_natal"],
            "ingresso_recente": lua["ingresso_recente"],
        },
        "sol_progredido_signo": sol["signo"],
        "mudancas_iminentes": mudancas,
    }


def calcular_progressoes(
    *,
    natal: dict,
    data_alvo: str,
    sistema_casas: Optional[str] = None,
) -> dict:
    """Progressões secundárias para `data_alvo` em relação a um mapa natal."""
    sistema_id = validar_sistema_casas(sistema_casas)

    dt_natal = _datetime_natal(natal)
    dia_a, mes_a, ano_a = parse_data(data_alvo)
    dt_alvo = datetime(ano_a, mes_a, dia_a)

    if dt_alvo < dt_natal:
        raise ValueError("data_alvo deve ser posterior à data de nascimento.")

    dt_progredido = computar_data_progredida(dt_natal, dt_alvo)
    idade_aproximada = int((dt_alvo - dt_natal).total_seconds() / SEGUNDOS_POR_ANO_TROPICO)

    subject_natal = _build_subject_natal(natal, sistema_id)
    subject_p = _build_subject_progredido(natal, dt_progredido, sistema_id)

    pontos_p = _coletar_pontos(subject_p)
    pontos_n = _coletar_pontos(subject_natal)
    cuspides_natais = [c.abs_pos for _, c in casas_iter(subject_natal)]

    planetas_progredidos = _formatar_progredidos(subject_p, cuspides_natais)
    aspectos_raw = calcular_aspectos_sinastria(pontos_p, pontos_n, "progredido", "natal")
    aspectos = _renomear_aspectos(aspectos_raw)

    return {
        "natal": {
            "nome": natal.get("nome"),
            "data": natal.get("data"),
            "hora": natal.get("hora"),
            "local": natal.get("local"),
        },
        "data_alvo": data_alvo,
        "idade_aproximada": idade_aproximada,
        "planetas_progredidos": planetas_progredidos,
        "aspectos_progredido_natal": aspectos,
        "destaques": _destaques(planetas_progredidos, subject_p),
    }
