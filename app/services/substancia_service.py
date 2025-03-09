from motor.motor_asyncio import AsyncIOMotorDatabase
from fastapi import Depends, HTTPException, UploadFile, File
from bson import ObjectId
from app.schemas.substancia import SubstanciaSchema
from app.config.database import get_database
import pandas as pd
import io
import unidecode
import datetime

COLUNAS_SUBSTANCIA = {
    "substancia": "nome",
    "classe_terapeutica": "classificacao_terapeutica"
}

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
    
    def normalizar_nome_coluna(self, nome: str) -> str:
        """
        Normaliza o nome de uma coluna removendo acentos, 
        convertendo para minúsculas e substituindo espaços por underscores.
        """
        nome = unidecode.unidecode(nome).lower().strip()
        nome = nome.replace(" ", "_").replace("-", "_")
        return nome

    async def upload_csv(self, file: UploadFile):
        """
        Recebe um arquivo CSV, processa os dados e insere os registros na coleção de substâncias.
        """
        try:
            # Lê o arquivo CSV e converte em DataFrame do Pandas
            contents = await file.read()
            df = pd.read_csv(io.BytesIO(contents))

            # Normaliza os nomes das colunas
            df.columns = [self.normalizar_nome_coluna(col) for col in df.columns]

            # Lista dos campos válidos no esquema
            campos_validos = {
                "nome", "classificacao_terapeutica", "medicamentos"
            }

            # Contadores para resultados
            inseridos = 0
            atualizados = 0
            erros = []
            
            # Extrair substâncias únicas do CSV
            # Na coluna "substancia" do CSV estão os nomes das substâncias
            substancias_unicas = df[['substancia', 'classe_terapeutica']].drop_duplicates()
            
            # Processa cada substância única
            for index, row in substancias_unicas.iterrows():
                try:
                    # Converte dados da linha para dicionário
                    row_dict = {k: v for k, v in row.to_dict().items() if pd.notna(v)}
                    
                    # Mapeia as colunas para os nomes do modelo
                    substancia_dict = {}
                    if 'substancia' in row_dict and row_dict['substancia']:
                        substancia_dict['nome'] = row_dict['substancia']
                    else:
                        # Pula se não tiver nome de substância
                        erros.append(f"Linha {index+2}: Nome da substância não encontrado ou vazio")
                        continue
                        
                    # Adiciona classe terapêutica se disponível
                    if 'classe_terapeutica' in row_dict and row_dict['classe_terapeutica']:
                        substancia_dict['classificacao_terapeutica'] = row_dict['classe_terapeutica']
                    else:
                        substancia_dict['classificacao_terapeutica'] = ""
                    
                    # Inicializa lista de medicamentos
                    substancia_dict['medicamentos'] = []
                    
                    # Verifica se a substância já existe
                    existing_substancia = await self.collection.find_one({"nome": substancia_dict['nome']})
                    
                    if existing_substancia:
                        # Se existe, atualiza os campos
                        update_data = {}
                        for key, value in substancia_dict.items():
                            if value is not None and key != "nome" and key in campos_validos:
                                update_data[key] = value
                        
                        if update_data:
                            result = await self.collection.update_one(
                                {"nome": substancia_dict['nome']},
                                {"$set": update_data}
                            )
                            if result.modified_count > 0:
                                atualizados += 1
                    else:
                        # Se não existe, cria uma nova substância
                        result = await self.collection.insert_one(substancia_dict)
                        if result.inserted_id:
                            inseridos += 1
                
                except Exception as e:
                    # Registra erro para esta linha específica
                    erros.append(f"Erro na linha {index+2}: {str(e)}")
            
            return {
                "message": "Processamento concluído",
                "total_processado": len(substancias_unicas),
                "inseridos": inseridos,
                "atualizados": atualizados,
                "erros": erros
            }
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Erro ao processar arquivo: {str(e)}")