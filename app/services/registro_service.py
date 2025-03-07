from motor.motor_asyncio import AsyncIOMotorDatabase
from fastapi import Depends, HTTPException
from bson import ObjectId
from app.schemas.registro import RegistroSchema
from app.config.database import get_database

class RegistroService:
    def __init__(self, db: AsyncIOMotorDatabase = Depends(get_database)):  
        self.collection = db["registros"]

    async def create_registro(self, registro: RegistroSchema):
        registro_dict = registro.dict()
        result = await self.collection.insert_one(registro_dict)
        return {"id": str(result.inserted_id)}
    
    async def get_registros(self):
        registros = await self.collection.find().to_list(100)

        for reg in registros:
            reg['_id'] = str(reg['_id'])

        return registros
    
    async def get_registro(self, registro_id: str):
        registro = await self.collection.find_one({"_id": ObjectId(registro_id)})
        if not registro:
            raise HTTPException(status_code=404, detail="Registro não encontrado")
        
        registro['_id'] = str(registro['_id'])

        return registro
    
    async def update_registro(self, registro_id: str, registro: RegistroSchema):
        registro_dict = registro.dict()
        result = await self.collection.update_one({"_id": ObjectId(registro_id)}, {"$set": registro_dict})
        if result.modified_count == 0:
            raise HTTPException(status_code=404, detail="Registro não encontrado")
        return {"message": "Registro atualizado com sucesso"}
    
    async def delete_registro(self, registro_id: str):
        result = await self.collection.delete_one({"_id": ObjectId(registro_id)})
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Registro não encontrado")
        return {"message": "Registro deletado com sucesso"}