from motor.motor_asyncio import AsyncIOMotorDatabase
from fastapi import Depends, HTTPException
from bson import ObjectId
from app.schemas.substancia import SubstanciaSchema
from app.config.database import get_database

class SubstanciaService:
    def __init__(self, db: AsyncIOMotorDatabase = Depends(get_database)):  
        self.collection = db["substancias"]

    async def create_substancia(self, substancia: SubstanciaSchema):
        substancia_dict = substancia.dict()
        result = await self.collection.insert_one(substancia_dict)
        return {"id": str(result.inserted_id)}
    
    async def get_substancias(self):
        substancias = await self.collection.find().to_list(100)

        for sub in substancias:
            sub['_id'] = str(sub['_id'])

        return substancias
    
    async def get_substancia(self, substancia_id: str):
        substancia = await self.collection.find_one({"_id": ObjectId(substancia_id)})
        if not substancia:
            raise HTTPException(status_code=404, detail="Substância não encontrada")
        
        substancia['_id'] = str(substancia['_id'])

        return substancia
    
    async def update_substancia(self, substancia_id: str, substancia: SubstanciaSchema):
        substancia_dict = substancia.dict()
        result = await self.collection.update_one({"_id": ObjectId(substancia_id)}, {"$set": substancia_dict})
        if result.modified_count == 0:
            raise HTTPException(status_code=404, detail="Substância não encontrada")
        return {"message": "Substância atualizada com sucesso"}
    
    async def delete_substancia(self, substancia_id: str):
        result = await self.collection.delete_one({"_id": ObjectId(substancia_id)})
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Substância não encontrada")
        return {"message": "Substância excluida com sucesso"}