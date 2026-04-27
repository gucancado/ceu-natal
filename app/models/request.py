from pydantic import BaseModel
from typing import Optional


class NatalChartRequest(BaseModel):
    nome: str
    data: str          # formato: DD/MM/YYYY
    hora: Optional[str] = None    # formato: HH:MM (opcional)
    local: Optional[str] = None   # ex: "Mariana, MG" ou "Belo Horizonte, Brasil"

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "nome": "Brina Vasconcelos",
                    "data": "03/05/1987",
                    "hora": "13:47",
                    "local": "Mariana, MG"
                }
            ]
        }
    }
