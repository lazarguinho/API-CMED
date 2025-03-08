from fastapi import APIRouter, Depends
from typing import List
from app.schemas.substancia import SubstanciaSchema
from app.services.substancia_service import SubstanciaService
from app.config.database import db

router = APIRouter()

@router.post("/substancias/", response_model=dict)
async def create_substancia(substancia: SubstanciaSchema, service: SubstanciaService = Depends()):
    return await service.create_substancia(substancia)

@router.get("/substancias/", response_model=List[SubstanciaSchema])
async def get_substancias(service: SubstanciaService = Depends()):
    return await service.get_substancias()

@router.get("/substancias/{substancia_id}", response_model=SubstanciaSchema)
async def get_substancia(substancia_id: str, service: SubstanciaService = Depends()):
    return await service.get_substancia(substancia_id)

@router.put("/substancias/{substancia_id}", response_model=dict)
async def update_substancia(substancia_id: str, substancia: SubstanciaSchema, service: SubstanciaService = Depends()):
    return await service.update_substancia(substancia_id, substancia)

@router.delete("/substancias/{substancia_id}")
async def delete_substancia(substancia_id: str, service: SubstanciaService = Depends()):
    return await service.delete_substancia(substancia_id)

@router.get("/count/substancias")
async def get_substancias_count():
    count = await db["substancias"].count_documents({})
    return {"count": count}

@router.get("/page/substancias", response_model=dict)
async def get_substancias(skip: int = 0, limit: int = 10):
    total_substancias = await db["substancias"].count_documents({})
    substancias = await db["substancias"].find().skip(skip).limit(limit).to_list(100)
    
    for substancia in substancias:
        substancia["_id"] = str(substancia["_id"])

    metadados = {
        "total": total_substancias,
        "skip": skip,
        "limit": limit,
        "page": (skip // limit) + 1 if limit else 0
    }

    return {"data": substancias, "metadados": metadados}

@router.get("/filter", response_model=dict)
async def filtrar_medicamentos(nome: str = None, classe_terapeutica: str = None, tarja: str = None, tipo_produto: str = None):
    filtro = {}

    if nome:
        filtro["nome"] = {"$regex": nome, "$options": "i"}  
    if classe_terapeutica:
        filtro["classe_terapeutica"] = {"$regex": classe_terapeutica, "$options": "i"}
    
    substancias = await db["substancias"].find(filtro).to_list(100)

    for substancia in substancias:
        substancia["_id"] = str(substancia["_id"])

    return {"data": substancias}