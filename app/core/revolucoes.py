"""
Core compartilhado das revoluções planetárias (solar e lunar).

Uma revolução é o mapa levantado para o instante exato em que um planeta em
trânsito volta à longitude eclíptica que ocupava no nascimento. O instante vem
do Swiss Ephemeris (`swe.solcross_ut` / `swe.mooncross_ut`), acessado pela
`PlanetaryReturnFactory` do Kerykeion 5.x — precisão melhor que 0,001", sem
busca iterativa própria.

DECISÃO DE DESIGN: revolução trópica pura, sem correção de precessão. A variante
precessionada somaria ~50,3"/ano à longitude alvo (aos 40 anos, ~0,56°, o que
desloca o instante em ~13,5h e muda o ascendente por completo). É minoritária;
o campo `metodo` do resultado declara a escolha para quem for interpretar.

DECISÃO DE DESIGN: o local da revolução é obrigatório e vem de fora. Ele não
altera nenhuma longitude planetária — muda apenas ascendente, meio do céu e
cúspides. Deixar um default silencioso (o local natal) entregaria casas erradas
para quem mudou de cidade, que é a maioria dos casos reais.
"""
from datetime import datetime
from typing import Optional

from app.core.aspectos import (
    calcular_aspectos,
    calcular_aspectos_sinastria,
    casa_de_longitude,
)
from app.core.formatter import (
    formatar_angulo,
    formatar_casas,
    formatar_planeta,
    nome_sistema_casas,
    regentes_de,
)
from app.core.geocoder import geocode
from app.core.kerykeion import (
    casas_iter,
    criar_subject,
    planetas_iter,
    pontos_sensiveis_iter,
)
from app.core.sintese import calcular_sintese
from app.core.validators import (
    parse_data,
    parse_hora,
    parse_local,
)

# Casas angulares — planetas aqui são os de maior peso na leitura da revolução.
CASAS_ANGULARES = (1, 4, 7, 10)


def build_subject_natal(natal: dict, sistema_id: str):
    """
    Cria o subject natal, exigindo hora e local.

    Hora é inegociável aqui: sem ela o Sol natal erra até 0,5°, o que desloca o
    instante do retorno em até 12 horas e inutiliza o ascendente da revolução —
    justamente o ponto central da técnica.
    """
    data = natal.get("data")
    if not data:
        raise ValueError("Campo 'data' obrigatório no objeto natal.")

    dia, mes, ano = parse_data(data)
    h, m = parse_hora(natal.get("hora"))
    cidade, nacao = parse_local(natal.get("local"))

    tem_local = cidade is not None or (
        natal.get("lat") is not None and natal.get("lng") is not None
    )

    if h is None:
        raise ValueError(
            "Revoluções exigem a hora de nascimento. Sem ela o Sol natal erra "
            "até 0,5°, o que desloca o instante do retorno em até 12 horas e "
            "torna o ascendente da revolução — o ponto central da técnica — "
            "inutilizável."
        )
    if not tem_local:
        raise ValueError(
            "Revoluções exigem o local de nascimento para sobrepor a revolução "
            "às casas natais."
        )

    subject = criar_subject(
        nome=natal.get("nome") or "Anônimo",
        ano=ano, mes=mes, dia=dia,
        hora=h, minuto=m,
        cidade=cidade, nacao=nacao,
        lat=natal.get("lat"), lng=natal.get("lng"), tz_str=natal.get("tz_str"),
        sistema_casas=sistema_id,
    )
    return subject, (dia, mes, ano)


def resolver_local_revolucao(local_revolucao: Optional[str]) -> dict:
    """Geocodifica o local onde a revolução será levantada."""
    if not local_revolucao or not str(local_revolucao).strip():
        raise ValueError(
            "local_revolucao é obrigatório: informe a cidade onde a pessoa "
            "estará no momento do retorno. A escolha não altera as posições "
            "dos planetas, mas define ascendente, meio do céu e casas."
        )

    cidade, nacao = parse_local(local_revolucao)
    coords = geocode(cidade, nacao or "")
    return {
        "local": local_revolucao,
        "cidade": cidade,
        "lat": coords["lat"],
        "lng": coords["lng"],
        "tz_str": coords["tz_str"],
    }


def criar_factory(subject_natal, coords: dict):
    """
    Instancia a PlanetaryReturnFactory em modo offline.

    Import local: manter o custo do import do Kerykeion fora do carregamento do
    módulo e localizar a falha caso a factory mude de lugar entre versões.
    """
    from kerykeion.planetary_return_factory import PlanetaryReturnFactory

    return PlanetaryReturnFactory(
        subject_natal,
        lat=coords["lat"],
        lng=coords["lng"],
        tz_str=coords["tz_str"],
        online=False,
    )


def executar_retorno(chamada):
    """
    Roda a chamada à factory convertendo falhas do Kerykeion em ValueError.

    `KerykeionException` não é tratada pelo marshaller do servidor — cairia em
    "Erro interno do servidor", sem informação útil para quem chamou.
    """
    from kerykeion.schemas import KerykeionException

    try:
        return chamada()
    except KerykeionException as exc:
        raise ValueError(f"Não foi possível calcular a revolução: {exc}") from exc


def _coletar_pontos(subject) -> list[dict]:
    """Planetas e pontos sensíveis no formato consumido por `aspectos`."""
    pontos = []
    for nome_pt, ponto in planetas_iter(subject):
        pontos.append({"nome": nome_pt, "abs_pos": ponto.abs_pos, "speed": ponto.speed})
    for nome_pt, ponto in pontos_sensiveis_iter(subject):
        pontos.append({"nome": nome_pt, "abs_pos": ponto.abs_pos, "speed": ponto.speed})
    return pontos


def instante_utc(retorno) -> datetime:
    """Instante do retorno como datetime UTC ingênuo, para cálculo de vigência."""
    iso_utc = retorno.iso_formatted_utc_datetime
    return datetime.fromisoformat(iso_utc.replace("Z", "+00:00")).replace(tzinfo=None)


def montar_resultado(
    *,
    tipo: str,
    natal: dict,
    subject_natal,
    retorno,
    coords: dict,
    sistema_id: str,
    vigencia: dict,
    fonte: str,
    nota_metodo: str,
) -> dict:
    """
    Payload comum às duas revoluções.

    Segue o formato de `transitos.py` e `progressoes.py`: identificação do natal,
    bloco `metodo` autoexplicativo, mapa completo da revolução, sobreposição
    sobre o natal e síntese.
    """
    iso_utc = retorno.iso_formatted_utc_datetime
    iso_local = retorno.iso_formatted_local_datetime

    planetas: dict = {}
    for nome_pt, ponto in planetas_iter(retorno):
        planetas[nome_pt] = formatar_planeta(ponto, incluir_casa=True)

    pontos_sensiveis: dict = {}
    for nome_pt, ponto in pontos_sensiveis_iter(retorno):
        pontos_sensiveis[nome_pt] = formatar_planeta(ponto, incluir_casa=True)

    pontos_revolucao = _coletar_pontos(retorno)
    pontos_natais = _coletar_pontos(subject_natal)

    aspectos_internos = calcular_aspectos(pontos_revolucao)
    aspectos_cruzados = [
        {
            "planeta_revolucao": a["planeta_a"],
            "planeta_natal": a["planeta_b"],
            "tipo": a["tipo"],
            "orbe": a["orbe"],
            "aplicando": a["aplicando"],
            "exato": a["exato"],
            "natureza": a["natureza"],
        }
        for a in calcular_aspectos_sinastria(
            pontos_revolucao, pontos_natais, "revolucao", "natal"
        )
    ]

    cuspides_natais = [c.abs_pos for _, c in casas_iter(subject_natal)]
    cuspides_revolucao = [c.abs_pos for _, c in casas_iter(retorno)]

    sobreposicao = {
        "planetas_revolucao_em_casas_natais": {
            p["nome"]: casa_de_longitude(p["abs_pos"], cuspides_natais)
            for p in pontos_revolucao
        },
        "planetas_natais_em_casas_revolucao": {
            p["nome"]: casa_de_longitude(p["abs_pos"], cuspides_revolucao)
            for p in pontos_natais
        },
    }

    return {
        "natal": {
            "nome": natal.get("nome"),
            "data": natal.get("data"),
            "hora": natal.get("hora"),
            "local": natal.get("local"),
        },
        "revolucao": {
            "tipo": tipo,
            "instante_utc": iso_utc,
            "instante_local": iso_local,
            "local": coords["local"],
            "lat": coords["lat"],
            "lng": coords["lng"],
            "tz_str": coords["tz_str"],
            "vigencia": vigencia,
        },
        "sistema_casas": nome_sistema_casas(sistema_id),
        "metodo": {
            "tecnica": f"revolucao_{tipo}",
            "precessao": "nao_aplicada",
            "fonte": fonte,
            "nota": nota_metodo,
        },
        "planetas": planetas,
        "angulos": {
            "ascendente":   formatar_angulo(retorno.first_house),
            "meio_do_ceu":  formatar_angulo(retorno.tenth_house),
            "descendente":  formatar_angulo(retorno.seventh_house),
            "fundo_do_ceu": formatar_angulo(retorno.fourth_house),
        },
        "casas": formatar_casas(retorno),
        "pontos_sensiveis": pontos_sensiveis,
        "aspectos_internos": aspectos_internos,
        "aspectos_revolucao_natal": aspectos_cruzados,
        "sobreposicao": sobreposicao,
        "sintese": calcular_sintese(planetas, aspectos_internos),
    }


def destaques_comuns(resultado: dict, retorno, subject_natal) -> dict:
    """
    Ascendente da revolução com seus regentes, planetas angulares e a casa natal
    onde o ascendente da revolução cai — leitura básica de qualquer revolução.
    """
    asc = resultado["angulos"]["ascendente"]
    cuspides_natais = [c.abs_pos for _, c in casas_iter(subject_natal)]

    angulares = [
        nome
        for nome, dados in resultado["planetas"].items()
        if dados.get("casa") in CASAS_ANGULARES
    ]

    return {
        "ascendente_revolucao": {
            "signo": asc["signo"],
            "grau": asc["grau"],
            "regente_moderno": regentes_de(asc["signo"])["moderno"],
            "regente_tradicional": regentes_de(asc["signo"])["tradicional"],
            "casa_natal_onde_cai": casa_de_longitude(
                asc["posicao_absoluta"], cuspides_natais
            ),
        },
        "planetas_angulares": angulares,
    }


def resumo_planeta(resultado: dict, nome: str) -> dict:
    """Signo, casa da revolução e casa natal de um planeta — para os destaques."""
    dados = resultado["planetas"].get(nome, {})
    return {
        "signo": dados.get("signo"),
        "grau": dados.get("grau"),
        "casa_revolucao": dados.get("casa"),
        "casa_natal": resultado["sobreposicao"]["planetas_revolucao_em_casas_natais"].get(nome),
    }
