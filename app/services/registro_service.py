from motor.motor_asyncio import AsyncIOMotorDatabase
from fastapi import Depends, HTTPException, UploadFile, File
from bson import ObjectId
from app.schemas.registro import RegistroSchema
from app.config.database import get_database
import pandas as pd
import io
import unidecode
import datetime

COLUNAS_REGISTRO = {
    "codigo_ggrem": "codigo_ggrem",
    "registro": "registro_anvisa",
    "ean_1": "ean1",
    "ean_2": "ean2",
    "ean_3": "ean3",
    "produto": "medicamento_nome"  # Para buscar o medicamento
}

class RegistroService:
    def __init__(self, db: AsyncIOMotorDatabase = Depends(get_database)):  
        self.collection = db["registros"]
        self.medicamentos_collection = db["medicamentos"]

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
    
    def normalizar_nome_coluna(self, nome: str) -> str:
        """
        Normaliza o nome de uma coluna removendo acentos, 
        convertendo para minúsculas e substituindo espaços por underscores.
        """
        nome = unidecode.unidecode(nome).lower().strip()
        nome = nome.replace(" ", "_").replace("-", "_").replace("(", "_").replace(")", "_")
        return nome

    async def upload_csv(self, file: UploadFile):
        """
        Recebe um arquivo CSV, processa os dados e insere os registros na coleção de registros.
        Estabelece relações com medicamentos.
        """
        try:
            # Lê o arquivo CSV e converte em DataFrame do Pandas
            contents = await file.read()
            df = pd.read_csv(io.BytesIO(contents))

            # Normaliza os nomes das colunas
            df.columns = [self.normalizar_nome_coluna(col) for col in df.columns]

            # Lista dos campos válidos no esquema
            campos_validos = {
                "codigo_ggrem", "registro_anvisa", "ean1", "ean2", "ean3", "medicamento_id"
            }

            # Filtra apenas as colunas que existem tanto no CSV quanto no modelo
            colunas_para_usar = {}
            for csv_col, model_col in COLUNAS_REGISTRO.items():
                normalizado = self.normalizar_nome_coluna(csv_col)
                if normalizado in df.columns:
                    colunas_para_usar[normalizado] = model_col
            
            # Cria um novo DataFrame com as colunas mapeadas
            df_mapeado = df.rename(columns=colunas_para_usar)
            
            # Contadores para resultados
            inseridos = 0
            atualizados = 0
            erros = []
            
            # Processa cada linha do DataFrame
            for index, row in df_mapeado.iterrows():
                try:
                    # Converte dados da linha para dicionário e filtra apenas campos válidos
                    row_dict = {k: v for k, v in row.to_dict().items() if pd.notna(v)}
                    reg_dict = {}
                    
                    # Verifica se temos o nome do medicamento para buscar
                    if "medicamento_nome" not in row_dict or not row_dict["medicamento_nome"]:
                        erros.append(f"Linha {index+2}: Nome do medicamento não encontrado ou vazio")
                        continue
                    
                    # Busca o medicamento pelo nome
                    medicamento_nome = row_dict["medicamento_nome"]
                    medicamento = await self.medicamentos_collection.find_one({"nome": medicamento_nome})
                    
                    if not medicamento:
                        erros.append(f"Linha {index+2}: Medicamento '{medicamento_nome}' não encontrado")
                        continue
                    
                    # Adiciona o ID do medicamento ao registro
                    reg_dict["medicamento_id"] = str(medicamento["_id"])
                    
                    # Transfere campos válidos
                    for campo in campos_validos:
                        if campo in row_dict and campo != "medicamento_id":
                            reg_dict[campo] = str(row_dict[campo])  # Converte para string para garantir
                    
                    # Verifica se já existe um registro para este medicamento
                    existing_reg = await self.collection.find_one({"medicamento_id": reg_dict["medicamento_id"]})
                    
                    if existing_reg:
                        # Se existe, atualiza os campos
                        update_data = {}
                        for key, value in reg_dict.items():
                            if key != "medicamento_id":
                                update_data[key] = value
                        
                        if update_data:
                            result = await self.collection.update_one(
                                {"_id": existing_reg["_id"]},
                                {"$set": update_data}
                            )
                            if result.modified_count > 0:
                                atualizados += 1
                    else:
                        # Se não existe, cria um novo registro
                        # Garante campos obrigatórios
                        if "codigo_ggrem" not in reg_dict:
                            reg_dict["codigo_ggrem"] = ""
                        if "registro_anvisa" not in reg_dict:
                            reg_dict["registro_anvisa"] = ""
                        if "ean1" not in reg_dict:
                            reg_dict["ean1"] = ""
                        if "ean2" not in reg_dict:
                            reg_dict["ean2"] = ""
                        if "ean3" not in reg_dict:
                            reg_dict["ean3"] = ""
                        
                        result = await self.collection.insert_one(reg_dict)
                        if result.inserted_id:
                            inseridos += 1
                            
                            # Atualiza o medicamento para referenciar este registro
                            await self.medicamentos_collection.update_one(
                                {"_id": ObjectId(reg_dict["medicamento_id"])},
                                {"$set": {"registro_id": str(result.inserted_id)}}
                            )
                
                except Exception as e:
                    # Registra erro para esta linha específica
                    erros.append(f"Erro na linha {index+2}: {str(e)}")
            
            return {
                "message": "Processamento concluído",
                "total_processado": len(df),
                "inseridos": inseridos,
                "atualizados": atualizados,
                "erros": erros
            }
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Erro ao processar arquivo: {str(e)}")
