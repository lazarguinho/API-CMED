from pydantic import BaseModel, Field
from typing import Optional, List

class LaboratorioSchema(BaseModel):
    id: Optional[str] = Field(None, alias="_id")
    nome: str
    CNPJ: str
    endereco: str
    telefone: str
    email: str
    data_cadastro: str
    atividade_principal: str
    natureza_juridica: str
    status: str

    medicamentos: Optional[List[str]] = []

    class Config:
        json_schema_extra = {
            "example": {
                "nome": "LABORATÓRIO DE ANALISES CLÍNICAS",
                "CNPJ": "00.000.000/0000-00",
                "endereco": "AV. BRASIL, 100",
                "telefone": "(00) 0000-0000",
                "email": "TtH5u@example.com",
                "data_cadastro": "2023-01-01",
                "atividade_principal": "Analises Clinicas",
                "natureza_juridica": "Sociedade Limitada",
                "status": "Ativo"
            }
        }
