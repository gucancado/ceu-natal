from pydantic import BaseModel
from typing import Optional


class NatalChartRequest(BaseModel):
    nome: str
    data: str          # formato: DD/MM/YYYY
    hora: Optional[str] = None    # formato: HH:MM (opcional)
    local: Optional[str] = None   # ex: "Ouro Preto, MG" ou "Belo Horizonte, Brasil"

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "nome": "Pessoa Exemplo",
                    "data": "15/05/1990",
                    "hora": "13:47",
                    "local": "Ouro Preto, MG"
                }
            ]
        }
    }
