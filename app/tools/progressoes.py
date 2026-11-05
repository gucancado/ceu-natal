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

A conta inteira é feita em tempo universal: a hora natal de parede é
localizada no fuso natal e convertida para UTC, `data_alvo` é tomada como
meia-noite UTC e o subject progredido é criado com `tz_str="UTC"`. Somar dias
à hora de parede e relocalizá-la no fuso natal deslocaria o UT em 1 h sempre
que o horário de verão do natal e o do instante progredido diferissem (~15°
no MC progredido), e o instante progredido poderia cair numa hora local
inexistente.
"""
from datetime import date, datetime, timedelta, timezone
from typing import Optional
from zoneinfo import ZoneInfo

from app.core.aspectos import calcular_aspectos_cruzados, casa_de_longitude, renomear
from app.core.entrada import EntradaNascimento
from app.core.formatter import SIGNOS_PT, formatar_planeta
from app.core.kerykeion import (
    casas_iter,
    coletar_pontos,
    criar_subject,
    planetas_iter,
)
from app.core.validators import parse_data, validar_sistema_casas

SEGUNDOS_POR_ANO_JULIANO = 365.25 * 86400.0

# Só os luminares progredidos trocam de signo em prazo que interesse a uma
# leitura (Lua ~2,5 anos, Sol ~30 anos); nos demais "iminente" pode levar décadas.
PLANETAS_MUDANCA_IMINENTE = ("sol", "lua")


def _datetime_natal_utc(entrada: EntradaNascimento) -> datetime:
    """Instante do nascimento em UTC (aware): hora de parede localizada em `entrada.tz_str`.

    Hora omitida vale 12:00 (só a validação do subject natal exige hora).
    Na transição do horário de verão a hora de parede é ambígua (repetida) ou
    inexistente (pulada); as duas leituras são `fold=0` e `fold=1`, e `is_dst`
    escolhe a que tem horário de verão em vigor (`is_dst=True`) ou não
    (`is_dst=False`), como o Kerykeion faz no subject natal. Fora da transição
    as duas leituras coincidem e `is_dst` é ignorado; sem `is_dst` vale
    `fold=0` (o subject natal já recusa a hora ambígua nesse caso).
    """
    local = datetime(
        entrada.ano, entrada.mes, entrada.dia,
        entrada.hora if entrada.tem_hora else 12,
        entrada.minuto if entrada.tem_hora else 0,
        tzinfo=ZoneInfo(entrada.tz_str),
    )
    leituras = [local.replace(fold=0), local.replace(fold=1)]
    is_dst = entrada.is_dst
    if is_dst is not None and leituras[0].utcoffset() != leituras[1].utcoffset():
        local = next(
            (d for d in leituras if bool(d.dst()) == bool(is_dst)), leituras[0],
        )
    else:
        local = leituras[0]
    return local.astimezone(timezone.utc)


def computar_data_progredida(data_natal: datetime, data_alvo: datetime) -> datetime:
    """Aplica a regra '1 dia = 1 ano': retorna data_natal + idade_em_anos dias.

    Aritmética pura: os dois datetimes devem ser ambos naive ou ambos aware
    (em `calcular_progressoes`, ambos em UTC).
    """
    delta = data_alvo - data_natal
    anos_vividos = delta.total_seconds() / SEGUNDOS_POR_ANO_JULIANO
    return data_natal + timedelta(days=anos_vividos)


def _flags_signo(grau_no_signo: float, planeta: str) -> dict:
    """Sinaliza ingresso recente (<1°) ou mudança iminente (>29°) num signo.

    `mudanca_iminente` só vale para Sol e Lua; nos demais vem sempre False.
    """
    return {
        "ingresso_recente": grau_no_signo < 1.0,
        "mudanca_iminente": (
            planeta in PLANETAS_MUDANCA_IMINENTE and grau_no_signo > 29.0
        ),
    }


def _build_subject_progredido(
    entrada: EntradaNascimento,
    data_progredida_utc: datetime,
    sistema_id: str,
):
    """Cria o subject progredido em UTC — mesmas lat/lng do natal (já
    resolvidas), sem `is_dst` (em UTC não há hora ambígua nem inexistente)."""
    return criar_subject(
        nome=entrada.nome + " (progredido)",
        ano=data_progredida_utc.year,
        mes=data_progredida_utc.month,
        dia=data_progredida_utc.day,
        hora=data_progredida_utc.hour,
        minuto=data_progredida_utc.minute,
        lat=entrada.lat, lng=entrada.lng, tz_str="UTC",
        sistema_casas=sistema_id,
    )


def _formatar_progredidos(subject_p, cuspides_natais: list[float]) -> dict:
    saida = {}
    for nome_pt, ponto in planetas_iter(subject_p):
        base = formatar_planeta(ponto, incluir_casa=False)
        base["casa_natal"] = casa_de_longitude(ponto.abs_pos, cuspides_natais)
        base.update(_flags_signo(ponto.position, nome_pt))
        saida[nome_pt] = base
    return saida


_ORDEM_SIGNOS = ["Ari", "Tau", "Gem", "Can", "Leo", "Vir",
                 "Lib", "Sco", "Sag", "Cap", "Aqu", "Pis"]


def _destaques(planetas_progredidos: dict, subject_p) -> dict:
    lua = planetas_progredidos["lua"]
    sol = planetas_progredidos["sol"]

    mudancas = []
    for nome_pt, ponto in planetas_iter(subject_p):
        if nome_pt in PLANETAS_MUDANCA_IMINENTE and ponto.position > 29.0:
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

    dia_a, mes_a, ano_a = parse_data(data_alvo)
    entrada = EntradaNascimento.de_dict(natal, rotulo="natal")
    if date(ano_a, mes_a, dia_a) < date(entrada.ano, entrada.mes, entrada.dia):
        raise ValueError("data_alvo não pode ser anterior à data de nascimento.")

    # O subject natal vem antes: valida hora/local, latitude e hora local
    # inexistente ou ambígua no horário de verão. As coordenadas resolvidas
    # (uma geocodificação) servem também ao instante UTC e ao progredido.
    entrada.exigir_hora_e_local("Progressões")
    entrada = entrada.exigir_casas()
    subject_natal = entrada.subject(sistema_id)

    dt_natal = _datetime_natal_utc(entrada)
    dt_alvo = datetime(ano_a, mes_a, dia_a, tzinfo=timezone.utc)
    dt_progredido = computar_data_progredida(dt_natal, dt_alvo)
    idade_aproximada = int((dt_alvo - dt_natal).total_seconds() / SEGUNDOS_POR_ANO_JULIANO)

    subject_p = _build_subject_progredido(entrada, dt_progredido, sistema_id)

    pontos_p = coletar_pontos(subject_p)
    pontos_n = coletar_pontos(subject_natal, fixo=True)
    cuspides_natais = [c.abs_pos for _, c in casas_iter(subject_natal)]

    planetas_progredidos = _formatar_progredidos(subject_p, cuspides_natais)
    aspectos = renomear(
        calcular_aspectos_cruzados(pontos_p, pontos_n, "progredido", "natal"),
        "planeta_progredido", "planeta_natal",
    )

    return {
        "natal": {
            "nome": natal.get("nome"),
            "data": natal.get("data"),
            "hora": natal.get("hora"),
            "local": natal.get("local"),
        },
        "data_alvo": data_alvo,
        "idade_aproximada": idade_aproximada,
        "metodo": {
            "progressao": "secundaria",
            "regra": "1 dia apos o nascimento = 1 ano de vida",
            "mc": "kerykeion_recompute",
            "nota": (
                "Mapa progredido recalculado para data_natal + idade_em_anos "
                "dias no local natal, em tempo universal: hora natal convertida "
                "para UTC, data_alvo tomada como meia-noite UTC, imune ao "
                "horario de verao. O MC e demais cuspides resultam da "
                "recomputacao do AstrologicalSubject pelo Kerykeion para esse "
                "datetime — equivalente em ordem de magnitude a Naibod, mas "
                "nao identico a Naibod nem a Solar Arc classicos. Use o campo "
                "para que agentes interpretadores ponderem a precisao do MC "
                "progredido em analises de transicoes."
            ),
        },
        "planetas_progredidos": planetas_progredidos,
        "aspectos_progredido_natal": aspectos,
        "destaques": _destaques(planetas_progredidos, subject_p),
    }
