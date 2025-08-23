from dataclasses import dataclass
from application.database_postgres.BaseModel import BasePayload, BaseModel

class ConversionsModel(BaseModel):
    table_name = "conversions"

    @dataclass
    class Payload(BasePayload):
        item_id: int
        uom_id: int
        conv_factor: float
            