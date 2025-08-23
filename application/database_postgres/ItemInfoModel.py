from dataclasses import dataclass, field
import json

from application.database_postgres.BaseModel import BasePayload, BaseModel, lst2pgarr

class ItemInfoModel(BaseModel):
    table_name = "item_info"

    @dataclass
    class Payload(BasePayload):
        barcode: str
        packaging: str = ""
        uom_quantity: float = 1.0
        uom: int = 1
        cost: float = 0.0
        safety_stock: float = 0.0
        lead_time_days: float = 0.0
        ai_pick: bool = False
        prefixes: list = field(default_factory=list)

        def payload_dictionary(self):
            payload = super().payload_dictionary()
            payload['prefixes'] = lst2pgarr(self.prefixes)
            return payload