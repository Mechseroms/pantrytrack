from dataclasses import dataclass, field
import json

from application.database_postgres.BaseModel import BasePayload, BaseModel, lst2pgarr

class ItemInfoModel(BaseModel):
    table_name = "item_info"
    primary_key = "item_uuid"
    primary_key_type = "uuid"

    @dataclass
    class Payload(BasePayload):
        item_uuid: str
        item_uom: str = None
        item_packaging: str = ""
        item_uom_quantity: float = 1.0
        item_cost: float = 0.0
        item_safety_stock: float = 0.0
        item_lead_time_days: float = 0.0
        item_ai_pick: bool = False
        item_prefixes: list = field(default_factory=list)

        def payload_dictionary(self):
            payload = super().payload_dictionary()
            payload['item_prefixes'] = lst2pgarr(self.item_prefixes)
            return payload