from pydantic import BaseModel, Field
from typing import Optional, List

class MedicamentoSchema(BaseModel):
    id: Optional[str] = Field(None, alias="_id")
    nome: str
    apresentacao: str
    classe_terapeutica: str
    tarja: str
    restricao_hospitalar: bool
    tipo_produto: str

    laboratorio_id: str
    registro_id: Optional[str]
    substancias: List[str] = []
    historico_precos: Optional[List[str]] = []

    class Config:
        json_schema_extra = {
            "example": {
                "nome": "TANDENE",
                "apresentacao": "(125,0 + 50,0 + 300,0 + 30,0) MG COM CT BL AL PLAS TRANS X 15",
                "classe_terapeutica": "M3B - RELAXANTE MUSCULAR DE AÇÃO CENTRAL",
                "tarja": "Tarja Vermelha",
                "restricao_hospitalar": False,
                "tipo_produto": "Similar",
                "laboratorio_id": "string",
                "substancias": []
            }
        }