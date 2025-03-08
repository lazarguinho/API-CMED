from fastapi import APIRouter, Depends
from typing import List
from app.schemas.laboratorio import LaboratorioSchema
from app.services.laboratorio_service import LaboratorioService
from app.config.database import db

router = APIRouter()

@router.post("/laboratorios/", response_model=dict)
async def create_laboratorio(laboratorio: LaboratorioSchema, service: LaboratorioService = Depends()):
    return await service.create_laboratorio(laboratorio)

@router.get("/laboratorios/", response_model=List[LaboratorioSchema])
async def get_laboratorios(service: LaboratorioService = Depends()):
    return await service.get_laboratorios()

@router.get("/laboratorios/{laboratorio_id}", response_model=LaboratorioSchema)
async def get_laboratorio(laboratorio_id: str, service: LaboratorioService = Depends()):
    return await service.get_laboratorio(laboratorio_id)

@router.put("/laboratorios/{laboratorio_id}", response_model=dict)
async def update_laboratorio(laboratorio_id: str, laboratorio: LaboratorioSchema, service: LaboratorioService = Depends()):
    return await service.update_laboratorio(laboratorio_id, laboratorio)

@router.delete("/laboratorios/{laboratorio_id}")
async def delete_laboratorio(laboratorio_id: str, service: LaboratorioService = Depends()):
    return await service.delete_laboratorio(laboratorio_id)

@router.get("/count/laboratorios")
async def get_laboratorios_count():
    count = await db["laboratorios"].count_documents({})
    return {"count": count}

@router.get("/page/laboratorios", response_model=dict)
async def get_laboratorios(skip: int = 0, limit: int = 10):
    total_laboratorios = await db["laboratorios"].count_documents({})
    laboratorios = await db["laboratorios"].find().skip(skip).limit(limit).to_list(100)
    
    for laboratorio in laboratorios:
        laboratorio["_id"] = str(laboratorio["_id"])

    metadados = {
        "total": total_laboratorios,
        "skip": skip,
        "limit": limit,
        "page": (skip // limit) + 1 if limit else 0
    }

    return {"data": laboratorios, "metadados": metadados}


@router.get("/filter", response_model=dict)
async def filtrar_laboratorios(nome: str = None, telefone: str = None, endereco: str = None, atividade_principal: str = None, natureza_juridica: str = None):
    filtro = {}

    if nome:
        filtro["nome"] = {"$regex": nome, "$options": "i"}  
    if telefone:
        filtro["telefone"] = {"$regex": telefone, "$options": "i"}
    if endereco:
        filtro["endereco"] = {"$regex": endereco, "$options": "i"}
    if atividade_principal:
        filtro["atividade_principal"] = {"$regex": atividade_principal, "$options": "i"}
    if natureza_juridica:
        filtro["natureza_juridica"] = {"$regex": natureza_juridica, "$options": "i"}

    laboratorios = await db["laboratorios"].find(filtro).to_list(100)

    for laboratorio in laboratorios:
        laboratorio["_id"] = str(laboratorio["_id"])

    return {"data": laboratorios}