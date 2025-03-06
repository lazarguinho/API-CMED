from pydantic import BaseModel, Field
from typing import Optional

class RegistroSchema(BaseModel):
    id: Optional[str] = Field(None, alias="_id")
    codigo_ggrem: str
    registro_anvisa: str
    ean1: str
    ean2: str
    ean3: str

    medicamento_id: str

    class Config:
        json_schema_extra = {
            "example": {
                "codigo_ggrem": "123456",
                "registro_anvisa": "123456",
                "ean1": "123456",
                "ean2": "123456",
                "ean3": "123456"
            }
        }
