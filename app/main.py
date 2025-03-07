from fastapi import FastAPI
from app.routes import medicamento, laboratorio, substancia, registro, historico_preco

app = FastAPI(title="API-CMED - Medicamentos")

app.include_router(medicamento.router, prefix="/api", tags=["Medicamentos"])
app.include_router(laboratorio.router, prefix="/api", tags=["Laboratorios"])
app.include_router(substancia.router, prefix="/api", tags=["Substancias"])
app.include_router(registro.router, prefix="/api", tags=["Registros"])
app.include_router(historico_preco.router, prefix="/api", tags=["HistoricoPrecos"])