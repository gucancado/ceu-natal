from datetime import datetime
from typing import Optional, Tuple


def parse_data(data: str) -> Tuple[int, int, int]:
    """DD/MM/YYYY -> (dia, mes, ano)."""
    try:
        dt = datetime.strptime(data.strip(), "%d/%m/%Y")
        return dt.day, dt.month, dt.year
    except ValueError as exc:
        raise ValueError(f"Data inválida: '{data}'. Use o formato DD/MM/YYYY.") from exc


def parse_hora(hora: Optional[str]) -> Tuple[Optional[int], Optional[int]]:
    """HH:MM -> (hora, minuto). (None, None) se não informado."""
    if not hora:
        return None, None
    try:
        dt = datetime.strptime(hora.strip(), "%H:%M")
        return dt.hour, dt.minute
    except ValueError as exc:
        raise ValueError(f"Hora inválida: '{hora}'. Use o formato HH:MM.") from exc


def parse_local(local: Optional[str]) -> Tuple[Optional[str], str]:
    """
    'Cidade, UF/País' -> (cidade, nacao).

    Usa apenas a última vírgula como separador, então cidades cujo nome
    contém vírgula (ex: 'Washington, D.C.') são preservadas:
      'Washington, D.C., USA' -> ('Washington, D.C.', 'USA')

    Sem vírgula, nacao volta como string vazia — o geocoder decide o que fazer.
    `None` retorna (None, "") — ausência total de local.
    String vazia ou só espaços levanta ValueError.
    """
    if local is None:
        return None, ""

    if not local.strip():
        raise ValueError("Local inválido: string vazia.")

    if "," in local:
        cidade, nacao = local.rsplit(",", 1)
        cidade = cidade.strip()
        nacao = nacao.strip()
    else:
        cidade = local.strip()
        nacao = ""

    if not cidade:
        raise ValueError(f"Local inválido: '{local}'.")

    return cidade, nacao
