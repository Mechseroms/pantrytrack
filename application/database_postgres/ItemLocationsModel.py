from dataclasses import dataclass, field
from application.database_postgres.BaseModel import BasePayload, BaseModel, lst2pgarr

class ItemLocationsModel(BaseModel):
    table_name = "item_locations"

    @dataclass
    class Payload(BasePayload):
        part_id: int
        location_id: int
        quantity_on_hand: float = 0.0
        cost_layers: list = field(default_factory=list)

        def payload_dictionary(self):
            payload = super().payload_dictionary()
            payload['cost_layers'] = lst2pgarr(self.cost_layers)
            return payload
            