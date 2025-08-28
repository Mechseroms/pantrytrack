from dataclasses import dataclass, field
from application.database_postgres.BaseModel import BasePayload, BaseModel, lst2pgarr

class ItemLocationsModel(BaseModel):
    table_name = "item_locations"
    primary_key = "item_location_uuid"
    primary_key_type = 'uuid'

    @dataclass
    class Payload(BasePayload):
        item_uuid: str
        location_uuid: str
        item_quantity_on_hand: float = 0.0
            