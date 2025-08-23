from dataclasses import dataclass, field
import json

from application.database_postgres.BaseModel import BasePayload, BaseModel

class ShoppingListItemsModel(BaseModel):
    table_name = "shopping_list_items"

    @dataclass
    class Payload(BasePayload):
        list_uuid: str
        item_type: str
        item_name: str
        uom: int
        qty: float
        item_uuid: str = None
        links: dict = field(default_factory=dict)
        
        def payload_dictionary(self):
            payload = super().payload_dictionary()
            payload['links'] = json.dumps(self.links)
            return payload