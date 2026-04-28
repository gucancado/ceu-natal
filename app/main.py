from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from app.models.request import NatalChartRequest
from app.services.chart import calcular_mapa

app = FastAPI(
    title="Ceu Natal API",
    description="Calcula o mapa astral natal com planetas, casas, aspectos, nodos e sintese.",
    version="2.0.0",
)


@app.get("/health")
def health():
    return {"status": "ok", "service": "ceu-natal", "version": "2.0.0"}


@app.post("/natal-chart")
def natal_chart(request: NatalChartRequest):
    try:
        resultado = calcular_mapa(
            nome=request.nome,
            data=request.data,
            hora=request.hora,
            local=request.local,
            sistema_casas=request.sistema_casas or "Placidus",
            incluir_aspectos=request.incluir_aspectos if request.incluir_aspectos is not None else True,
        )
        return JSONResponse(content=resultado)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")
