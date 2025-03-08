from fastapi import APIRouter, Depends
from typing import List
from app.schemas.medicamento import MedicamentoSchema
from app.services.medicamento_service import MedicamentoService
from app.config.database import db

router = APIRouter()

@router.get("/filter/medicamento", response_model=dict)
async def filtrar_medicamentos(nome: str = None, classe_terapeutica: str = None, tarja: str = None, tipo_produto: str = None):
    filtro = {}

    if nome:
        filtro["nome"] = {"$regex": nome, "$options": "i"}  
    if classe_terapeutica:
        filtro["classe_terapeutica"] = {"$regex": classe_terapeutica, "$options": "i"}
    if tarja:
        filtro["tarja"] = {"$regex": tarja, "$options": "i"}
    if tipo_produto:
        filtro["tipo_produto"] = {"$regex": tipo_produto, "$options": "i"}
    
    medicamentos = await db["medicamentos"].find(filtro).to_list(100)

    for medicamento in medicamentos:
        medicamento["_id"] = str(medicamento["_id"])

    return {"data": medicamentos}

@router.post("/medicamentos/", response_model=dict)
async def create_medicamento(medicamento: MedicamentoSchema, service: MedicamentoService = Depends()):
    return await service.create_medicamento(medicamento)

@router.get("/medicamentos/", response_model=List[MedicamentoSchema])
async def get_medicamentos(service: MedicamentoService = Depends()):
    return await service.get_medicamentos()

@router.get("/medicamentos/{medicamento_id}", response_model=MedicamentoSchema)
async def get_medicamento(medicamento_id: str, service: MedicamentoService = Depends()):
    return await service.get_medicamento(medicamento_id)

@router.put("/medicamentos/{medicamento_id}", response_model=dict)
async def update_medicamento(medicamento_id: str, medicamento: MedicamentoSchema, service: MedicamentoService = Depends()):
    return await service.update_medicamento(medicamento_id, medicamento)

@router.delete("/medicamentos/{medicamento_id}")
async def delete_medicamento(medicamento_id: str, service: MedicamentoService = Depends()):
    return await service.delete_medicamento(medicamento_id)
@router.get("/count/medicamentos")
async def get_medicamentos_count():
    count = await db["medicamentos"].count_documents({})
    return {"count": count}

@router.get("/page/medicamentos", response_model=dict)
async def get_medicamentos(skip: int = 0, limit: int = 10):
    total_medicamentos = await db["medicamentos"].count_documents({})
    medicamentos = await db["medicamentos"].find().skip(skip).limit(limit).to_list(100)
    
    for medicamento in medicamentos:
        medicamento["_id"] = str(medicamento["_id"])

    metadados = {
        "total": total_medicamentos,
        "skip": skip,
        "limit": limit,
        "page": (skip // limit) + 1 if limit else 0
    }

    return {"data": medicamentos, "metadados": metadados}
