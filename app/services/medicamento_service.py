from motor.motor_asyncio import AsyncIOMotorDatabase
from fastapi import Depends, HTTPException, UploadFile, File
from bson import ObjectId
from app.schemas.medicamento import MedicamentoSchema
from app.config.database import get_database
import pandas as pd
import io
import unidecode
import datetime

COLUNAS_MEDICAMENTO = {
    "produto": "nome",
    "apresentacao": "apresentacao",
    "classe_terapeutica": "classe_terapeutica",
    "tipo_de_produto_(status_do_produto)": "tipo_produto",
    "tarja": "tarja",
    "restricao_hospitalar": "restricao_hospitalar",
    "cnpj": "laboratorio_id",
    "substancia": "substancias"
}

class MedicamentoService:
    def __init__(self, db: AsyncIOMotorDatabase = Depends(get_database)):  
        self.collection = db["medicamentos"]
        self.laboratorio_collection = db["laboratorios"]
        self.substancia_collection = db["substancias"]

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
        Recebe um arquivo CSV, processa os dados e insere os registros na coleção de medicamentos.
        Relaciona medicamentos com laboratórios (por CNPJ) e substâncias (por nome).
        """
        try:
            # Lê o arquivo CSV e converte em DataFrame do Pandas
            contents = await file.read()
            df = pd.read_csv(io.BytesIO(contents))

            # Normaliza os nomes das colunas
            df.columns = [self.normalizar_nome_coluna(col) for col in df.columns]

            # Lista dos campos válidos no esquema
            campos_validos = {
                "nome", "apresentacao", "classe_terapeutica", "tarja", 
                "restricao_hospitalar", "tipo_produto", "laboratorio_id", 
                "registro_id", "substancias", "historico_precos"
            }

            # Filtra apenas as colunas que existem tanto no CSV quanto no modelo
            colunas_para_usar = {csv_col: model_col for csv_col, model_col in COLUNAS_MEDICAMENTO.items() if csv_col in df.columns}
            
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
                    med_dict = {}
                    
                    # Transfere campos válidos
                    for campo in campos_validos:
                        if campo in row_dict:
                            med_dict[campo] = row_dict[campo]
                    
                    # Verifica campos obrigatórios
                    if "nome" not in med_dict or not med_dict["nome"]:
                        erros.append(f"Linha {index+2}: Nome do medicamento não encontrado ou vazio")
                        continue
                    
                    # Processa valores do campo restricao_hospitalar (converter de texto para boolean)
                    if "restricao_hospitalar" in med_dict:
                        valor = str(med_dict["restricao_hospitalar"]).lower()
                        med_dict["restricao_hospitalar"] = valor in ["sim", "true", "1", "yes"]
                    
                    # Busca laboratorio pelo CNPJ e substitui por ID
                    if "cnpj" in row_dict:
                        laboratorio = await self.laboratorio_collection.find_one({"CNPJ": row_dict["cnpj"]})
                        if laboratorio:
                            med_dict["laboratorio_id"] = str(laboratorio["_id"])
                        else:
                            erros.append(f"Linha {index+2}: Laboratório com CNPJ {row_dict['cnpj']} não encontrado")
                            continue
                    
                    # Inicializa arrays
                    med_dict.setdefault("substancias", [])
                    med_dict.setdefault("historico_precos", [])
                    
                    # Busca substância pelo nome e adiciona ID ao array de substâncias
                    if "substancia" in row_dict:
                        substancia = await self.substancia_collection.find_one({"nome": row_dict["substancia"]})
                        if substancia:
                            if str(substancia["_id"]) not in med_dict["substancias"]:
                                med_dict["substancias"].append(str(substancia["_id"]))
                    
                    # Verifica se o medicamento já existe (pela combinação de nome, apresentação e laboratório)
                    filtro_busca = {
                        "nome": med_dict["nome"],
                        "apresentacao": med_dict.get("apresentacao", ""),
                        "laboratorio_id": med_dict["laboratorio_id"]
                    }
                    
                    existing_med = await self.collection.find_one(filtro_busca)
                    
                    if existing_med:
                        # Se existe, atualiza os campos
                        update_data = {}
                        for key, value in med_dict.items():
                            if key == "substancias" and existing_med.get("substancias"):
                                # Para substâncias, mescla os arrays sem duplicatas
                                existing_substancias = existing_med.get("substancias", [])
                                for subst_id in med_dict["substancias"]:
                                    if subst_id not in existing_substancias:
                                        existing_substancias.append(subst_id)
                                update_data["substancias"] = existing_substancias
                            elif key not in ["nome", "apresentacao", "laboratorio_id"]:
                                update_data[key] = value
                        
                        if update_data:
                            result = await self.collection.update_one(
                                {"_id": existing_med["_id"]},
                                {"$set": update_data}
                            )
                            if result.modified_count > 0:
                                atualizados += 1
                                
                                # Atualiza relacionamento reverso (adiciona medicamento às substâncias)
                                med_id = str(existing_med["_id"])
                                for subst_id in med_dict["substancias"]:
                                    await self.substancia_collection.update_one(
                                        {"_id": ObjectId(subst_id)},
                                        {"$addToSet": {"medicamentos": med_id}}
                                    )
                                
                                # Atualiza relacionamento reverso (adiciona medicamento ao laboratório)
                                await self.laboratorio_collection.update_one(
                                    {"_id": ObjectId(med_dict["laboratorio_id"])},
                                    {"$addToSet": {"medicamentos": med_id}}
                                )
                    else:
                        # Se não existe, cria um novo medicamento
                        # Garante campos obrigatórios
                        if "apresentacao" not in med_dict:
                            med_dict["apresentacao"] = ""
                        if "classe_terapeutica" not in med_dict:
                            med_dict["classe_terapeutica"] = ""
                        if "tarja" not in med_dict:
                            med_dict["tarja"] = ""
                        if "tipo_produto" not in med_dict:
                            med_dict["tipo_produto"] = ""
                        
                        result = await self.collection.insert_one(med_dict)
                        if result.inserted_id:
                            inseridos += 1
                            med_id = str(result.inserted_id)
                            
                            # Atualiza relacionamento reverso (adiciona medicamento às substâncias)
                            for subst_id in med_dict["substancias"]:
                                await self.substancia_collection.update_one(
                                    {"_id": ObjectId(subst_id)},
                                    {"$addToSet": {"medicamentos": med_id}}
                                )
                            
                            # Atualiza relacionamento reverso (adiciona medicamento ao laboratório)
                            await self.laboratorio_collection.update_one(
                                {"_id": ObjectId(med_dict["laboratorio_id"])},
                                {"$addToSet": {"medicamentos": med_id}}
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
