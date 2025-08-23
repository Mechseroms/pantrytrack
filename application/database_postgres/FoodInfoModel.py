from dataclasses import dataclass, field
import json

from application.database_postgres.BaseModel import BasePayload, BaseModel, lst2pgarr

class FoodInfoModel(BaseModel):
    table_name = "food_info"

    @dataclass
    class Payload(BasePayload):
        food_groups: list = field(default_factory=list)
        ingrediants: list = field(default_factory=list)
        nutrients: dict = field(default_factory=dict)
        expires: bool = False
        default_expiration: float = 0.0
    
        def payload_dictionary(self):
            return {
                'food_groups': lst2pgarr(self.food_groups),
                'ingrediants': lst2pgarr(self.ingrediants),
                'nutrients': json.dumps(self.nutrients),
                'expires': self.expires,
                'default_expiration': self.default_expiration
            }