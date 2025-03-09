from fastapi import APIRouter, Depends, File, UploadFile
from typing import List
from app.schemas.registro import RegistroSchema
from app.services.registro_service import RegistroService
from app.config.database import db

router = APIRouter()

@router.post(
    "/upload/registros", 
    response_model=dict,
    tags=["Registros"],
    responses={
        200: {
            "description": "Importação realizada com sucesso",
            "content": {
                "application/json": {
                    "example": {
                        "message": "Processamento concluído",
                        "total_processado": 100,
                        "inseridos": 80,
                        "atualizados": 15,
                        "erros": ["Erro na linha 5: Medicamento não encontrado"]
                    }
                }
            }
        }
    },
    summary="Importar registros de um arquivo CSV",
    description="""
    Recebe um arquivo CSV, processa os dados e insere os registros na coleção de registros.
    
    - Lê o arquivo CSV.
    - Normaliza os nomes das colunas para garantir compatibilidade.
    - Estabelece relações com medicamentos.
    - Insere os registros na base de dados.
    """
)
async def upload_registros(
    file: UploadFile = File(...),
    service: RegistroService = Depends()
):
    return await service.upload_csv(file)

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

@router.get("/count/registros")
async def get_registros_count():
    count = await db["registros"].count_documents({})
    return {"count": count}

@router.get("/page/registros", response_model=dict)
async def get_registros(skip: int = 0, limit: int = 10):
    total_registros = await db["registros"].count_documents({})
    registros = await db["registros"].find().skip(skip).limit(limit).to_list(100)
    
    for registro in registros:
        registro["_id"] = str(registro["_id"])

    metadados = {
        "total": total_registros,
        "skip": skip,
        "limit": limit,
        "page": (skip // limit) + 1 if limit else 0
    }

    return {"data": registros, "metadados": metadados}