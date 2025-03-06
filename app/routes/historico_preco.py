from fastapi import APIRouter, Depends
from typing import List
from app.schemas.historico_preco import HistoricoPrecoSchema
from app.services.historico_preco_service import HistoricoPrecoService

router = APIRouter()

@router.post("/historico_preco/", response_model=dict)
async def create_historico_preco(historico_preco: HistoricoPrecoSchema, service: HistoricoPrecoService = Depends()):
    return await service.create_historico_preco(historico_preco)

@router.get("/historico_precos/", response_model=List[HistoricoPrecoSchema])
async def get_historico_precos(service: HistoricoPrecoService = Depends()):
    return await service.get_historico_precos()

@router.get("/historico_precos/{historico_preco_id}", response_model=HistoricoPrecoSchema)
async def get_historico_preco(historico_preco_id: str, service: HistoricoPrecoService = Depends()):
    return await service.get_historico_preco(historico_preco_id)

@router.put("/historico_precos/{historico_preco_id}", response_model=dict)
async def update_historico_preco(historico_preco_id: str, historico_preco: HistoricoPrecoSchema, service: HistoricoPrecoService = Depends()):
    return await service.update_historico_preco(historico_preco_id, historico_preco)

@router.delete("/historico_precos/{historico_preco_id}")
async def delete_historico_preco(historico_preco_id: str, service: HistoricoPrecoService = Depends()):
    return await service.delete_historico_preco(historico_preco_id)