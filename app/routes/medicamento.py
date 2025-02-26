from fastapi import APIRouter, Depends
from typing import List
from app.schemas.medicamento import MedicamentoSchema
from app.services.medicamento_service import MedicamentoService

router = APIRouter()

@router.post("/medicamentos/", response_model=dict)
async def create_medicamento(medicamento: MedicamentoSchema, service: MedicamentoService = Depends()):
    return await service.create_medicamento(medicamento)

@router.get("/medicamentos/", response_model=List[MedicamentoSchema])
async def get_medicamentos(service: MedicamentoService = Depends()):
    return await service.get_medicamentos()

@router.get("/medicamentos/{medicamento_id}", response_model=MedicamentoSchema)
async def get_medicamento(medicamento_id: str, service: MedicamentoService = Depends()):
    return await service.get_medicamento(medicamento_id)

@router.delete("/medicamentos/{medicamento_id}")
async def delete_medicamento(medicamento_id: str, service: MedicamentoService = Depends()):
    return await service.delete_medicamento(medicamento_id)
