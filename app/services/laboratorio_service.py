from motor.motor_asyncio import AsyncIOMotorDatabase
from fastapi import Depends, HTTPException
from bson import ObjectId
from app.schemas.laboratorio import LaboratorioSchema
from app.config.database import get_database

class LaboratorioService:
    def __init__(self, db: AsyncIOMotorDatabase = Depends(get_database)):  
        self.collection = db["laboratorios"]

    async def create_laboratorio(self, laboratorio: LaboratorioSchema):
        laboratorio_dict = laboratorio.dict()
        result = await self.collection.insert_one(laboratorio_dict)
        return {"id": str(result.inserted_id)}
    
    async def get_laboratorios(self):
        laboratorios = await self.collection.find().to_list(100)

        for lab in laboratorios:
            lab['_id'] = str(lab['_id'])

        return laboratorios

    async def get_laboratorio(self, laboratorio_id: str):
        laboratorio = await self.collection.find_one({"_id": ObjectId(laboratorio_id)})
        if not laboratorio:
            raise HTTPException(status_code=404, detail="Laboratório não encontrado")
        
        laboratorio['_id'] = str(laboratorio['_id'])

        return laboratorio
    
    async def update_laboratorio(self, laboratorio_id: str, laboratorio: LaboratorioSchema):
        laboratorio_dict = laboratorio.dict()
        result = await self.collection.update_one({"_id": ObjectId(laboratorio_id)}, {"$set": laboratorio_dict})
        if result.modified_count == 0:
            raise HTTPException(status_code=404, detail="Laboratório não encontrado")
        return {"message": "Laboratório atualizado com sucesso"}
    
    async def delete_laboratorio(self, laboratorio_id: str):
        result = await self.collection.delete_one({"_id": ObjectId(laboratorio_id)})
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Laboratório não encontrado")
        return {"message": "Laboratório deletado com sucesso"}