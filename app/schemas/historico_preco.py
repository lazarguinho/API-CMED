from pydantic import BaseModel, Field
from typing import Optional

class HistoricoPrecoSchema(BaseModel):
    id: Optional[str] = Field(None, alias="_id")
    data_comercializacao: str
    pf_sem_impostos: float
    pf_0: float
    pf_12: float
    pf_17: float
    pf_18: float
    pmc_sem_imposto: float
    pmc_0: float
    pmc_12: float
    pmc_17: float
    pmc_18: float

    medicamento_id: str

    class Config:
        json_schema_extra = {
            "example": {
                "data_comercializacao": "2023-01-01",
                "pf_sem_impostos": 10.0,
                "pf_0": 10.0,
                "pf_12": 10.0,
                "pf_17": 10.0,
                "pf_18": 10.0,
                "pmc_sem_imposto": 10.0,
                "pmc_0": 10.0,
                "pmc_12": 10.0,
                "pmc_17": 10.0,
                "pmc_18": 10.0
            }
        }