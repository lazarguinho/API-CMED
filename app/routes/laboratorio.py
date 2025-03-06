from fastapi import APIRouter, Depends
from typing import List
from app.schemas.laboratorio import LaboratorioSchema
from app.services.laboratorio_service import LaboratorioService

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