from datetime import datetime
from typing import Tuple, Optional


def parse_data(data: str) -> Tuple[int, int, int]:
    """Converte DD/MM/YYYY para (dia, mes, ano)"""
    try:
        dt = datetime.strptime(data.strip(), "%d/%m/%Y")
        return dt.day, dt.month, dt.year
    except ValueError:
        raise ValueError(f"Data inválida: '{data}'. Use o formato DD/MM/YYYY.")


def parse_hora(hora: Optional[str]) -> Tuple[Optional[int], Optional[int]]:
    """Converte HH:MM para (hora, minuto). Retorna (None, None) se não informado."""
    if not hora:
        return None, None
    try:
        dt = datetime.strptime(hora.strip(), "%H:%M")
        return dt.hour, dt.minute
    except ValueError:
        raise ValueError(f"Hora inválida: '{hora}'. Use o formato HH:MM.")


def parse_local(local: Optional[str]) -> Tuple[Optional[str], Optional[str]]:
    """
    Divide 'Cidade, Estado/País' em (cidade, nação).
    Tenta inferir o código de país a partir de abreviações brasileiras de estado.
    """
    if not local:
        return None, None

    partes = [p.strip() for p in local.split(",")]
    cidade = partes[0]

    ESTADOS_BR = {
        "AC", "AL", "AP", "AM", "BA", "CE", "DF", "ES", "GO",
        "MA", "MT", "MS", "MG", "PA", "PB", "PR", "PE", "PI",
        "RJ", "RN", "RS", "RO", "RR", "SC", "SP", "SE", "TO"
    }

    if len(partes) >= 2:
        segundo = partes[1].strip().upper()
        if segundo in ESTADOS_BR:
            # É um estado brasileiro — passa cidade completa para o GeoNames
            cidade_completa = f"{cidade}, {partes[1].strip()}"
            return cidade_completa, "BR"
        else:
            # Pode ser um país escrito por extenso
            return cidade, partes[1].strip()

    return cidade, "BR"  # padrão Brasil se não informado
