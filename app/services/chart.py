import os
from kerykeion import AstrologicalSubjectFactory, ChartDataFactory
from app.models.request import SISTEMAS_CASAS
from app.utils.validators import parse_data, parse_hora, parse_local
from app.services.formatter import formatar_mapa

GEONAMES_USERNAME = os.getenv("GEONAMES_USERNAME", "gucancado")


def calcular_mapa(nome: str, data: str, hora: str | None, local: str | None,
                  sistema_casas: str = "Placidus", incluir_aspectos: bool = True) -> dict:

    dia, mes, ano = parse_data(data)
    h, m = parse_hora(hora)
    cidade, nacao = parse_local(local)

    tem_hora = h is not None
    tem_local = cidade is not None

    hora_calc = h if tem_hora else 12
    min_calc = m if tem_hora else 0

    houses_id = SISTEMAS_CASAS.get(sistema_casas, "P")

    if tem_local:
        subject = AstrologicalSubjectFactory.from_birth_data(
            name=nome,
            year=ano, month=mes, day=dia,
            hour=hora_calc, minute=min_calc,
            city=cidade, nation=nacao,
            houses_system_identifier=houses_id,
            online=True,
            geonames_username=GEONAMES_USERNAME,
        )
    else:
        subject = AstrologicalSubjectFactory.from_birth_data(
            name=nome,
            year=ano, month=mes, day=dia,
            hour=hora_calc, minute=min_calc,
            lng=0.0, lat=0.0, tz_str="UTC",
            houses_system_identifier=houses_id,
            online=False,
        )

    chart_data = ChartDataFactory.create_natal_chart_data(subject)

    return formatar_mapa(
        subject=subject,
        chart_data=chart_data,
        data=data,
        hora=hora,
        local=local,
        tem_local=tem_local,
        sistema_casas=sistema_casas,
        incluir_aspectos=incluir_aspectos,
    )
