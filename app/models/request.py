from pydantic import BaseModel
from typing import Optional


SISTEMAS_CASAS = {
    "Placidus": "P",
    "Whole Sign": "W",
    "Koch": "K",
    "Equal House": "E",
    "Regiomontanus": "R",
    "Campanus": "C",
    "Porphyry": "O",
    "Morinus": "M",
    "Topocentric": "T",
}


class NatalChartRequest(BaseModel):
    nome: str
    data: str
    hora: Optional[str] = None
    local: Optional[str] = None
    sistema_casas: Optional[str] = "Placidus"
    incluir_aspectos: Optional[bool] = True

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "nome": "Brina Vasconcelos",
                    "data": "03/05/1987",
                    "hora": "13:47",
                    "local": "Mariana, MG",
                    "sistema_casas": "Placidus",
                    "incluir_aspectos": True
                }
            ]
        }
    }
