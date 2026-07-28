"""
Lógica temporal das revoluções planetárias — sem dependência de Kerykeion.

Isolado de propósito: `pyswisseph` não compila no Windows (não há toolchain C)
e não há Docker local, então tudo que importa Kerykeion só roda em Linux. As
bordas de calendário moram aqui, onde podem ser testadas em qualquer ambiente.
"""
from datetime import datetime, timedelta

# Duração média dos ciclos, em dias.
ANO_TROPICO_DIAS = 365.2422
MES_SIDERAL_DIAS = 27.321582

# Faixa aceita para o ano da revolução. Fora disso a precisão das efemérides
# do Swiss Ephemeris degrada e o caso de uso deixa de ser astrologia natal.
ANO_MINIMO = 1800
ANO_MAXIMO = 2200

# Folga, em dias, entre a âncora de busca e o aniversário. O retorno solar
# nunca se afasta mais de ~1 dia da data de nascimento, então 3 dias garantem
# que o próximo cruzamento encontrado é o do ano pedido — sem risco de pular
# para o do ano seguinte.
FOLGA_ANCORA_DIAS = 3


def validar_ano_revolucao(ano) -> int:
    """Valida o ano pedido para a revolução solar."""
    if isinstance(ano, bool) or not isinstance(ano, int):
        raise ValueError(
            f"ano deve ser um número inteiro, recebi {type(ano).__name__}."
        )
    if ano < ANO_MINIMO or ano > ANO_MAXIMO:
        raise ValueError(
            f"ano {ano} fora da faixa suportada ({ANO_MINIMO}–{ANO_MAXIMO})."
        )
    return ano


def aniversario_no_ano(dia_natal: int, mes_natal: int, ano: int) -> datetime:
    """
    Data do aniversário dentro de `ano`.

    Nascidos em 29/02 caem em 28/02 nos anos comuns — é a convenção usual e o
    erro introduzido (menos de um dia) é absorvido pela folga da âncora.
    """
    dia = dia_natal
    if mes_natal == 2 and dia_natal == 29:
        try:
            datetime(ano, 2, 29)
        except ValueError:
            dia = 28
    return datetime(ano, mes_natal, dia)


def ancora_revolucao_solar(dia_natal: int, mes_natal: int, ano: int) -> datetime:
    """
    Data a partir da qual buscar o cruzamento do Sol pela longitude natal.

    Aniversário no ano pedido menos `FOLGA_ANCORA_DIAS`. Para aniversários nos
    primeiros dias de janeiro a âncora cai em dezembro do ano anterior, o que é
    correto: o cruzamento seguinte ainda é o da revolução daquele ano.
    """
    return aniversario_no_ano(dia_natal, mes_natal, ano) - timedelta(days=FOLGA_ANCORA_DIAS)


def vigencia(inicio: datetime, duracao_dias: float) -> dict:
    """Janela de vigência da revolução: do instante do retorno ao próximo.

    O fim é aproximado — obter o exato exigiria calcular um segundo mapa
    completo. O nome do campo na saída declara isso.
    """
    fim = inicio + timedelta(days=duracao_dias)
    return {
        "inicio": inicio.replace(microsecond=0).isoformat(),
        # Microssegundos aqui seriam ruído: a duração média do ciclo já é uma
        # aproximação de horas.
        "fim_aproximado": fim.replace(microsecond=0).isoformat(),
    }


def vigencia_solar(inicio: datetime) -> dict:
    return vigencia(inicio, ANO_TROPICO_DIAS)


def vigencia_lunar(inicio: datetime) -> dict:
    return vigencia(inicio, MES_SIDERAL_DIAS)
