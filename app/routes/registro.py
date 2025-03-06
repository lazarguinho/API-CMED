from fastapi import APIRouter, Depends
from typing import List
from app.schemas.registro import RegistroSchema
from app.services.registro_service import RegistroService

router = APIRouter()

@router.post("/registros/", response_model=dict)
async def create_registro(registro: RegistroSchema, service: RegistroService = Depends()):
    return await service.create_registro(registro)

@router.get("/registros/", response_model=List[RegistroSchema])
async def get_registros(service: RegistroService = Depends()):
    return await service.get_registros()

@router.get("/registros/{registro_id}", response_model=RegistroSchema)
async def get_registro(registro_id: str, service: RegistroService = Depends()):
    return await service.get_registro(registro_id)

@router.put("/registros/{registro_id}", response_model=dict)
async def update_registro(registro_id: str, registro: RegistroSchema, service: RegistroService = Depends()):
    return await service.update_registro(registro_id, registro)

@router.delete("/registros/{registro_id}")
async def delete_registro(registro_id: str, service: RegistroService = Depends()):
    return await service.delete_registro(registro_id)