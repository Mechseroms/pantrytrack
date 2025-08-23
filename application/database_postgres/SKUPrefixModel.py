from dataclasses import dataclass
from application.database_postgres.BaseModel import BasePayload, BaseModel

class SKUPrefixModel(BaseModel):
    table_name = "sku_prefix"

    @dataclass
    class Payload(BasePayload):
        uuid: str
        name: str
        description: str
            