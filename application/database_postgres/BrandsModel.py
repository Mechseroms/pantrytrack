from dataclasses import dataclass

from application.database_postgres.BaseModel import BasePayload, BaseModel

class BrandsModel(BaseModel):
    table_name = "brands"

    @dataclass
    class Payload(BasePayload):
        brand_name: str
    