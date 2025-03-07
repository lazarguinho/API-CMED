from motor.motor_asyncio import AsyncIOMotorDatabase
from fastapi import Depends, HTTPException
from bson import ObjectId
from app.schemas.medicamento import MedicamentoSchema
from app.config.database import get_database

class MedicamentoService:
    def __init__(self, db: AsyncIOMotorDatabase = Depends(get_database)):  
        self.collection = db["medicamentos"]

    async def create_medicamento(self, medicamento: MedicamentoSchema):
        medicamento_dict = medicamento.dict()
        result = await self.collection.insert_one(medicamento_dict)
        return {"id": str(result.inserted_id)}
    
    async def get_medicamentos(self):
        medicamentos = await self.collection.find().to_list(100)

        for med in medicamentos:
            med['_id'] = str(med['_id'])

        return medicamentos

    async def get_medicamento(self, medicamento_id: str):
        medicamento = await self.collection.find_one({"_id": ObjectId(medicamento_id)})
        if not medicamento:
            raise HTTPException(status_code=404, detail="Medicamento não encontrado")
        
        medicamento['_id'] = str(medicamento['_id'])

        return medicamento

    async def update_medicamento(self, medicamento_id: str, medicamento: MedicamentoSchema):
        medicamento_dict = medicamento.dict()
        result = await self.collection.update_one({"_id": ObjectId(medicamento_id)}, {"$set": medicamento_dict})
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Medicamento não encontrado")
        return {"message": "Medicamento atualizado com sucesso"}

    async def delete_medicamento(self, medicamento_id: str):
        result = await self.collection.delete_one({"_id": ObjectId(medicamento_id)})
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Medicamento não encontrado")
        return {"message": "Medicamento deletado com sucesso"}
