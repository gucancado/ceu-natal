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


_ESTADOS_BR = {
    "AC", "AL", "AP", "AM", "BA", "CE", "DF", "ES", "GO",
    "MA", "MT", "MS", "MG", "PA", "PB", "PR", "PE", "PI",
    "RJ", "RN", "RS", "RO", "RR", "SC", "SP", "SE", "TO",
}


def parse_local(local: Optional[str]) -> Tuple[Optional[str], Optional[str]]:
    """
    'Cidade, UF/País' -> (cidade, nação). Inferência de país por UF brasileira.
    """
    if not local:
        return None, None

    partes = [p.strip() for p in local.split(",") if p.strip()]
    if not partes:
        return None, None

    cidade = partes[0]
    if len(partes) >= 2:
        segundo = partes[1].upper()
        if segundo in _ESTADOS_BR:
            return f"{cidade}, {partes[1]}", "BR"
        return cidade, partes[1]
    return cidade, "BR"
