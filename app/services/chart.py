import os
from kerykeion import AstrologicalSubjectFactory
from app.utils.validators import parse_data, parse_hora, parse_local
from app.services.formatter import formatar_mapa

GEONAMES_USERNAME = os.getenv("GEONAMES_USERNAME", "gucancado")


def calcular_mapa(nome: str, data: str, hora: str | None, local: str | None) -> dict:
    dia, mes, ano = parse_data(data)
    h, m = parse_hora(hora)
    cidade, nacao = parse_local(local)

    tem_hora = h is not None
    tem_local = cidade is not None

    # Se não tem hora, usa meio-dia (posições planetárias ainda válidas, exceto Lua rápida)
    hora_calc = h if tem_hora else 12
    min_calc = m if tem_hora else 0

    if tem_local:
        subject = AstrologicalSubjectFactory.from_birth_data(
            name=nome,
            year=ano,
            month=mes,
            day=dia,
            hour=hora_calc,
            minute=min_calc,
            city=cidade,
            nation=nacao,
            online=True,
            geonames_username=GEONAMES_USERNAME,
        )
    else:
        # Sem local: usa coordenadas neutras (Greenwich), timezone UTC
        subject = AstrologicalSubjectFactory.from_birth_data(
            name=nome,
            year=ano,
            month=mes,
            day=dia,
            hour=hora_calc,
            minute=min_calc,
            lng=0.0,
            lat=0.0,
            tz_str="UTC",
            online=False,
        )

    return formatar_mapa(
        subject=subject,
        data=data,
        hora=hora,
        local=local,
        tem_local=tem_local,
    )
