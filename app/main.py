from fastapi import FastAPI
from app.routes import medicamento
from app.config.database import get_database  # Agora importamos de config/database.py

app = FastAPI(title="API-CMED - Medicamentos")

# Incluir rotas da API
app.include_router(medicamento.router, prefix="/api", tags=["Medicamentos"])
