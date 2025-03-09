from motor.motor_asyncio import AsyncIOMotorDatabase
from fastapi import Depends, HTTPException, UploadFile, File
from bson import ObjectId
from app.schemas.laboratorio import LaboratorioSchema
from app.config.database import get_database
import pandas as pd
import io
import unidecode
import datetime


COLUNAS_LABORATORIO = {
    "cnpj": "CNPJ",
    "razao_social": "nome",
    "nome_fantasia": "nome",
    "telefone": "telefone",
    "email": "email",
    "endereco": "endereco",
    "atividade_principal": "atividade_principal",
    "natureza_juridica": "natureza_juridica",
    "status": "status"
}

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
    
    def normalizar_nome_coluna(self, nome: str) -> str:
        """
        Normaliza o nome de uma coluna removendo acentos, 
        convertendo para minúsculas e substituindo espaços por underscores.
        """
        nome = unidecode.unidecode(nome).lower().strip()
        nome = nome.replace(" ", "_").replace("-", "_")
        return nome

    def get_object_id(self):
        """
        Gera um ObjectId do MongoDB como string
        """
        return str(ObjectId())
    
    async def upload_csv(self, file: UploadFile):
        """
        Recebe um arquivo CSV, processa os dados e insere os registros na coleção de laboratórios.

        - Lê o arquivo CSV.
        - Normaliza os nomes das colunas para garantir compatibilidade.
        - Insere os registros na base de dados.
        """
        try:
            # Lê o arquivo CSV e converte em DataFrame do Pandas
            contents = await file.read()
            df = pd.read_csv(io.BytesIO(contents))

            # Normaliza os nomes das colunas
            df.columns = [self.normalizar_nome_coluna(col) for col in df.columns]

            # Lista dos campos válidos no esquema
            campos_validos = {
                "nome", "CNPJ", "endereco", "telefone", "email", 
                "data_cadastro", "atividade_principal", "natureza_juridica", 
                "status", "medicamentos"
            }

            # Filtra apenas as colunas que existem tanto no CSV quanto no modelo
            colunas_para_usar = {csv_col: model_col for csv_col, model_col in COLUNAS_LABORATORIO.items() if csv_col in df.columns}
            
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
                    lab_dict = {k: v for k, v in row_dict.items() if k in campos_validos}
                    
                    # Verifica se CNPJ existe para evitar duplicações
                    if "CNPJ" in lab_dict and lab_dict["CNPJ"]:
                        # Verifica se o laboratório já existe
                        existing_lab = await self.collection.find_one({"CNPJ": lab_dict["CNPJ"]})
                        
                        if existing_lab:
                            # Se existe, atualiza os campos, mantendo apenas campos válidos
                            update_data = {}
                            for key, value in lab_dict.items():
                                if value is not None and key != "CNPJ" and key in campos_validos:
                                    update_data[key] = value
                            
                            if update_data:
                                result = await self.collection.update_one(
                                    {"CNPJ": lab_dict["CNPJ"]},
                                    {"$set": update_data}
                                )
                                if result.modified_count > 0:
                                    atualizados += 1
                        else:
                            # Se não existe, cria um novo laboratório
                            # Define valores padrão para campos obrigatórios ausentes
                            if "nome" not in lab_dict or not lab_dict["nome"]:
                                lab_dict["nome"] = f"Laboratório {lab_dict['CNPJ']}"
                            
                            # Adiciona campos padrão se não existirem
                            lab_dict.setdefault("endereco", "")
                            lab_dict.setdefault("telefone", "")
                            lab_dict.setdefault("email", "")
                            lab_dict.setdefault("atividade_principal", "")
                            lab_dict.setdefault("natureza_juridica", "")
                            lab_dict.setdefault("status", "Ativo")
                            lab_dict.setdefault("data_cadastro", datetime.datetime.now().strftime("%Y-%m-%d"))
                            lab_dict.setdefault("medicamentos", [])
                            
                            # Insere o novo laboratório
                            result = await self.collection.insert_one(lab_dict)
                            if result.inserted_id:
                                inseridos += 1
                    else:
                        # Registra erro para registros sem CNPJ
                        erros.append(f"Linha {index+2}: CNPJ não encontrado ou vazio")
                
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