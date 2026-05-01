from typing import Optional

from app.core.aspectos import calcular_aspectos_sinastria, casa_de_longitude
from app.core.formatter import planeta_pt, signo_pt
from app.core.kerykeion import (
    casas_iter,
    criar_subject,
    planetas_iter,
    pontos_sensiveis_iter,
)
from app.core.sintese import sintese_sinastria
from app.core.validators import (
    parse_data,
    parse_hora,
    parse_local,
    validar_sistema_casas,
)


def _build_subject(pessoa: dict, sistema_id: str = "P"):
    data = pessoa.get("data")
    if not data:
        raise ValueError("Campo 'data' obrigatório em cada pessoa.")

    hora = pessoa.get("hora")
    local = pessoa.get("local")
    nome = pessoa.get("nome") or "Anônimo"

    dia, mes, ano = parse_data(data)
    h, m = parse_hora(hora)
    cidade, nacao = parse_local(local)

    tem_hora = h is not None
    tem_local = cidade is not None or (
        pessoa.get("lat") is not None and pessoa.get("lng") is not None
    )

    subject = criar_subject(
        nome=nome,
        ano=ano, mes=mes, dia=dia,
        hora=h if tem_hora else 12,
        minuto=m if tem_hora else 0,
        cidade=cidade, nacao=nacao,
        lat=pessoa.get("lat"),
        lng=pessoa.get("lng"),
        tz_str=pessoa.get("tz_str"),
        sistema_casas=sistema_id,
    )
    return subject, nome, tem_hora, tem_local


def _coletar_pontos(subject) -> list[dict]:
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


def _resumo_pessoa(subject, nome: str, tem_local: bool) -> dict:
    asc = subject.first_house
    return {
        "nome": nome,
        "sol": signo_pt(subject.sun.sign),
        "lua": signo_pt(subject.moon.sign),
        "asc": signo_pt(asc.sign) if tem_local else None,
    }


def _ativacoes(planetas_da_pessoa: list[dict], subject_outro,
               nome_pessoa: str, nome_outro: str) -> list[dict]:
    """Cada planeta de uma pessoa cai em qual casa do mapa do outro."""
    casas_lista = list(casas_iter(subject_outro))
    cuspides = [c.abs_pos for _, c in casas_lista]
    saida = []
    for p in planetas_da_pessoa:
        casa = casa_de_longitude(p["abs_pos"], cuspides)
        cuspide_obj = casas_lista[casa - 1][1]
        saida.append({
            "planeta": p["nome"],
            "pessoa": nome_pessoa,
            "cai_na_casa": casa,
            "da_pessoa": nome_outro,
            "signo_da_cuspide": signo_pt(cuspide_obj.sign),
        })
    return saida


def calcular_sinastria(
    pessoa_a: dict,
    pessoa_b: dict,
    sistema_casas: Optional[str] = None,
) -> dict:
    sistema_id = validar_sistema_casas(sistema_casas)
    subject_a, nome_a, _, tem_local_a = _build_subject(pessoa_a, sistema_id)
    subject_b, nome_b, _, tem_local_b = _build_subject(pessoa_b, sistema_id)

    pontos_a = _coletar_pontos(subject_a)
    pontos_b = _coletar_pontos(subject_b)

    aspectos = calcular_aspectos_sinastria(pontos_a, pontos_b, nome_a, nome_b)

    ativacoes: list[dict] = []
    if tem_local_a and tem_local_b:
        # planetas de A nas casas de B, e vice-versa
        ativacoes.extend(_ativacoes(pontos_a, subject_b, nome_a, nome_b))
        ativacoes.extend(_ativacoes(pontos_b, subject_a, nome_b, nome_a))

    return {
        "pessoa_a": _resumo_pessoa(subject_a, nome_a, tem_local_a),
        "pessoa_b": _resumo_pessoa(subject_b, nome_b, tem_local_b),
        "aspectos_sinastria": aspectos,
        "ativacoes_de_casas": ativacoes,
        "sintese_sinastria": sintese_sinastria(aspectos),
    }
