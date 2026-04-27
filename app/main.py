from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from app.models.request import NatalChartRequest
from app.services.chart import calcular_mapa

app = FastAPI(
    title="Céu Natal API",
    description="Calcula o mapa astral natal a partir de nome, data, hora e local de nascimento.",
    version="1.0.0",
)


@app.get("/health")
def health():
    return {"status": "ok", "service": "ceu-natal"}


@app.post("/natal-chart")
def natal_chart(request: NatalChartRequest):
    try:
        resultado = calcular_mapa(
            nome=request.nome,
            data=request.data,
            hora=request.hora,
            local=request.local,
        )
        return JSONResponse(content=resultado)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")
