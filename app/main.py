from fastapi import FastAPI
from app.routes import medicamento, laboratorio, substancia, registro, historico_preco, querys_complexas, analises_vizualicoes

app = FastAPI(title="API-CMED - Medicamentos")

app.include_router(medicamento.router, prefix="/api", tags=["Medicamentos"])
app.include_router(laboratorio.router, prefix="/api", tags=["Laboratorios"])
app.include_router(substancia.router, prefix="/api", tags=["Substancias"])
app.include_router(registro.router, prefix="/api", tags=["Registros"])
app.include_router(historico_preco.router, prefix="/api", tags=["HistoricoPrecos"])
app.include_router(querys_complexas.router, prefix="/api", tags=["Querys Complexas"])
app.include_router(analises_vizualicoes.router, prefix="/api", tags=["Analises&visualizações"])