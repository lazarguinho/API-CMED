from app.config.database import db
from fastapi import APIRouter, HTTPException
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId

router = APIRouter()

# Configuração do cliente e banco de dados
client = AsyncIOMotorClient("mongodb://localhost:27017")
db = client["nome_do_banco"]  # Substitua pelo nome do seu banco

def convert_objectids(item):
    """
    Função auxiliar para converter recursivamente ObjectId em string.
    """
    if isinstance(item, list):
        return [convert_objectids(subitem) for subitem in item]
    elif isinstance(item, dict):
        return {key: convert_objectids(value) for key, value in item.items()}
    elif isinstance(item, ObjectId):
        return str(item)
    else:
        return item

# Endpoint 1: Detalhes completos de um medicamento com junções
@router.get("/querys-complexas/detalhes-medicamento/{med_id}")
async def detalhes_medicamento(med_id: str):
    try:
        med_obj_id = ObjectId(med_id)
    except Exception:
        raise HTTPException(status_code=400, detail="ID de medicamento inválido")
    
    pipeline = [
        {"$match": {"_id": med_obj_id}},
        {"$lookup": {
             "from": "laboratorios",
             "localField": "laboratorio_id",
             "foreignField": "_id",
             "as": "laboratorio"
        }},
        {"$lookup": {
             "from": "historico_precos",
             "localField": "historico_precos",
             "foreignField": "_id",
             "as": "precos"
        }},
        {"$lookup": {
             "from": "registros",
             "localField": "registro_id",
             "foreignField": "medicamento_id",
             "as": "registro"
        }}
    ]
    
    result = await db.medicamentos.aggregate(pipeline).to_list(length=None)
    if not result:
        raise HTTPException(status_code=404, detail="Medicamento não encontrado")
    
    # Converter os ObjectIds para string
    result = convert_objectids(result)
    return result

# Endpoint 2: Consulta de substâncias com seus medicamentos e respectivos laboratórios
@router.get("/querys-complexas/substancias-completo")
async def substancias_completo():
    pipeline = [
        {"$lookup": {
             "from": "medicamentos",
             "localField": "medicamentos",
             "foreignField": "_id",
             "as": "lista_medicamentos"
        }},
        {"$lookup": {
             "from": "laboratorios",
             "localField": "lista_medicamentos.laboratorio_id",
             "foreignField": "_id",
             "as": "lista_laboratorios"
        }}
    ]
    result = await db.substancias.aggregate(pipeline).to_list(length=None)
    
    # Converter os ObjectIds para string
    result = convert_objectids(result)
    return result
