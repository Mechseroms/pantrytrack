from dataclasses import dataclass, field
import json

from application.database_postgres.BaseModel import BasePayload, BaseModel

class RecipeItemsModel(BaseModel):
    table_name = "recipe_items"

    @dataclass
    class Payload(BasePayload):
        uuid: str
        rp_id: int
        item_type: str
        item_name:str
        uom: str
        qty: float = 0.0
        item_id: int = None
        links: dict = field(default_factory=dict)
        
        def payload_dictionary(self):
            payload = super().payload_dictionary()
            payload['links'] = json.dumps(self.links)
            return payload