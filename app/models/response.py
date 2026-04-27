from pydantic import BaseModel
from typing import Optional


class NascimentoModel(BaseModel):
    data: str
    hora: Optional[str] = None
    local: Optional[str] = None


class PlanetaModel(BaseModel):
    signo: str
    casa: Optional[int] = None
    grau: str
    retrogrado: bool = False


class PlanetasModel(BaseModel):
    sol: PlanetaModel
    lua: PlanetaModel
    mercurio: PlanetaModel
    venus: PlanetaModel
    marte: PlanetaModel
    jupiter: PlanetaModel
    saturno: PlanetaModel
    urano: PlanetaModel
    netuno: PlanetaModel
    plutao: PlanetaModel


class AnguloModel(BaseModel):
    signo: str
    grau: str


class AngulosModel(BaseModel):
    ascendente: AnguloModel
    meio_do_ceu: AnguloModel
    descendente: AnguloModel
    fundo_do_ceu: AnguloModel


class NatalChartResponse(BaseModel):
    nome: str
    nascimento: NascimentoModel
    planetas: PlanetasModel
    angulos: Optional[AngulosModel] = None
    aviso: Optional[str] = None
