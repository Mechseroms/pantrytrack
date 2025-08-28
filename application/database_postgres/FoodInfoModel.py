from dataclasses import dataclass, field
import json

from application.database_postgres.BaseModel import BasePayload, BaseModel, lst2pgarr

class FoodInfoModel(BaseModel):
    table_name = "food_info"
    primary_key = "item_uuid"
    primary_key_type = "uuid"

    @dataclass
    class Payload(BasePayload):
        item_uuid: str
        item_food_groups: list = field(default_factory=list)
        item_ingredients: list = field(default_factory=list)
        item_nutrients: dict = field(default_factory=dict)
        item_expires: bool = False
        item_default_expiration: float = 0.0
    
        def payload_dictionary(self):
            payload = super().payload_dictionary()
            payload['item_food_groups'] = lst2pgarr(self.item_food_groups)
            payload['item_ingredients'] = lst2pgarr(self.item_ingredients)
            payload['item_nutrients'] = json.dumps(self.item_nutrients)
            return payload
            
            