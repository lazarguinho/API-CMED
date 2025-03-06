from motor.motor_asyncio import AsyncIOMotorDatabase
from fastapi import Depends, HTTPException
from bson import ObjectId
from app.schemas.historico_preco import HistoricoPrecoSchema
from app.config.database import get_database

class HistoricoPrecoService:
    def __init__(self, db: AsyncIOMotorDatabase = Depends(get_database)):  
        self.collection = db["historico_precos"]

    async def create_historico_preco(self, historico_preco: HistoricoPrecoSchema):
        historico_preco_dict = historico_preco.dict()
        result = await self.collection.insert_one(historico_preco_dict)
        return {"_d": str(result.inserted_id)}
    
    async def get_historico_precos(self):
        historico_precos = await self.collection.find().to_list(100)
        
        for hp in historico_precos:
            hp['_id'] = str(hp['_id'])
        
        return historico_precos
    
    async def get_historico_preco(self, historico_preco_id: str):
        historico_preco = await self.collection.find_one({"_id": ObjectId(historico_preco_id)})
        if not historico_preco:
            raise HTTPException(status_code=404, detail="Histórico de Preços não encontrado")
        
        historico_preco['_id'] = str(historico_preco['_id'])
        
        return historico_preco
    
    async def update_historico_preco(self, historico_preco_id: str, historico_preco: HistoricoPrecoSchema):
        historico_preco_dict = historico_preco.dict()
        result = await self.collection.update_one({"_id": ObjectId(historico_preco_id)}, {"$set": historico_preco_dict})
        if result.modified_count == 0:
            raise HTTPException(status_code=404, detail="Histórico de Preços não encontrado")
        return {"message": "Histórico de Preços atualizado com sucesso"}
    
    async def delete_historico_preco(self, historico_preco_id: str):
        result = await self.collection.delete_one({"_id": ObjectId(historico_preco_id)})
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Histórico de Preços não encontrado")
        return {"message": "Histórico de Preços deletado com sucesso"}