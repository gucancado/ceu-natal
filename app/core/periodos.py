"""
Lógica temporal das revoluções planetárias — sem dependência de Kerykeion.

Isolado de propósito: `pyswisseph` não compila no Windows (não há toolchain C)
e não há Docker local, então tudo que importa Kerykeion só roda em Linux. As
bordas de calendário moram aqui, onde podem ser testadas em qualquer ambiente.
"""
from datetime import datetime, timedelta, timezone

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

NOTA_FIM_APROXIMADO = (
    "fim_aproximado_utc = inicio + duração média do ciclo, não a revolução "
    "seguinte calculada de fato. Erro típico de 20 a 30 minutos."
)


def validar_ano_revolucao(ano, ano_nascimento=None) -> int:
    """
    Valida o ano pedido para a revolução solar.

    `ano_nascimento`, quando informado, barra anos anteriores ao nascimento —
    sem isso a tool devolveria alegremente uma "revolução" décadas antes de a
    pessoa existir.
    """
    if isinstance(ano, bool) or not isinstance(ano, int):
        raise ValueError(
            f"ano deve ser um número inteiro, recebi {type(ano).__name__}."
        )
    if ano < ANO_MINIMO or ano > ANO_MAXIMO:
        raise ValueError(
            f"ano {ano} fora da faixa suportada ({ANO_MINIMO}–{ANO_MAXIMO})."
        )
    if ano_nascimento is not None and ano < ano_nascimento:
        raise ValueError(
            f"ano {ano} é anterior ao nascimento ({ano_nascimento}). A primeira "
            f"revolução solar de uma pessoa é a de {ano_nascimento}."
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


def _em_utc(dt: datetime) -> datetime:
    """Anexa UTC a um datetime ingênuo; converte se já tiver fuso."""
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def vigencia(inicio: datetime, duracao_dias: float) -> dict:
    """
    Janela de vigência da revolução: do instante do retorno até o próximo.

    Sempre em UTC e com o offset explícito na string — sem isso um consumidor
    pode tratar como hora local e errar horas. O fim é aproximado; obter o exato
    exigiria calcular um segundo mapa completo.
    """
    inicio_utc = _em_utc(inicio).replace(microsecond=0)
    fim_utc = (_em_utc(inicio) + timedelta(days=duracao_dias)).replace(microsecond=0)
    return {
        "inicio_utc": inicio_utc.isoformat(),
        "fim_aproximado_utc": fim_utc.isoformat(),
        "duracao_dias": round(duracao_dias, 4),
        "nota": NOTA_FIM_APROXIMADO,
    }


def vigencia_solar(inicio: datetime) -> dict:
    return vigencia(inicio, ANO_TROPICO_DIAS)


def vigencia_lunar(inicio: datetime) -> dict:
    return vigencia(inicio, MES_SIDERAL_DIAS)


def ciclo_anterior(instante_retorno: datetime, data_referencia: datetime,
                   duracao_dias: float) -> dict | None:
    """
    Descreve o ciclo que já estava em curso na data de referência.

    A busca devolve o *próximo* retorno a partir da data pedida, então quando o
    retorno não cai na própria data de referência existe um ciclo anterior ainda
    rodando — e é ele que "rege" a data pedida. Devolver isso explicitamente
    evita a leitura silenciosamente errada de quem pergunta "como está meu mês
    agora?" e recebe o mapa do mês que ainda não começou.
    """
    retorno_utc = _em_utc(instante_retorno)
    referencia_utc = _em_utc(data_referencia)

    if retorno_utc.date() <= referencia_utc.date():
        return None

    inicio_anterior = (retorno_utc - timedelta(days=duracao_dias)).replace(microsecond=0)
    return {
        "inicio_aproximado_utc": inicio_anterior.isoformat(),
        "nota": (
            "A data de referência caiu dentro do ciclo anterior, que começou por "
            "volta desta data. O mapa retornado é do ciclo SEGUINTE, que ainda "
            "não estava em vigor. Para analisar o ciclo em curso, chame de novo "
            "usando esta data como data_referencia."
        ),
    }
