from fastapi import APIRouter, Depends
from typing import List
from app.schemas.substancia import SubstanciaSchema
from app.services.substancia_service import SubstanciaService

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