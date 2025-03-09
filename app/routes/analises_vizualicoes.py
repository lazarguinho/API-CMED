from app.config.database import db
from fastapi import APIRouter, HTTPException
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId

router = APIRouter()

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

# Endpoint 1: Média de Preço Sem Impostos por Classe Terapêutica
@router.get("/analises-visualizacoes/precos-classe")
async def precos_por_classe():
    pipeline = [
        {"$lookup": {
             "from": "historico_precos",
             "localField": "historico_precos",
             "foreignField": "_id",
             "as": "precos"
        }},
        {"$unwind": "$precos"},
        {"$group": {
             "_id": "$classe_terapeutica",
             "avg_pf_sem_impostos": {"$avg": "$precos.pf_sem_impostos"}
        }},
        {"$sort": {"avg_pf_sem_impostos": -1}}
    ]
    result = await db.medicamentos.aggregate(pipeline).to_list(length=None)
    
    # Converter os ObjectIds para string
    result = convert_objectids(result)
    return result

# Endpoint 2: Tendência de Preços de um Medicamento ao Longo do Tempo
@router.get("/analises-visualizacoes/tendencia-precos/{med_id}")
async def tendencia_precos(med_id: str):
    try:
        med_obj_id = ObjectId(med_id)
    except Exception:
        raise HTTPException(status_code=400, detail="ID de medicamento inválido")
    
    pipeline = [
        {"$match": {"_id": med_obj_id}},
        {"$lookup": {
             "from": "historico_precos",
             "localField": "historico_precos",
             "foreignField": "_id",
             "as": "precos"
        }},
        {"$unwind": "$precos"},
        {"$sort": {"precos.data_comercializacao": 1}},
        {"$project": {
             "_id": 0,
             "data": "$precos.data_comercializacao",
             "pf_sem_impostos": "$precos.pf_sem_impostos",
             "pf_0": "$precos.pf_0",
             "pf_12": "$precos.pf_12",
             "pf_17": "$precos.pf_17",
             "pf_18": "$precos.pf_18"
        }}
    ]
    result = await db.medicamentos.aggregate(pipeline).to_list(length=None)
    if not result:
        raise HTTPException(status_code=404, detail="Medicamento não encontrado ou sem histórico de preços")
    
    # Converter os ObjectIds para string
    result = convert_objectids(result)
    return result
