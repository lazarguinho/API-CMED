from pydantic import BaseModel, Field
from typing import Optional, List

class SubstanciaSchema(BaseModel):
    id: Optional[str] = Field(None, alias="_id")
    nome: str
    classificacao_terapeutica: str

    medicamentos: Optional[List[str]] = []

    class Config:
        json_schema_extra = {
            "example": {
                "nome": "TANDENE",
                "classificacao_terapeutica": "M3B - RELAXANTE MUSCULAR DE AÇÃO CENTRAL"
            }
        }