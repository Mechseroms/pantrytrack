from dataclasses import dataclass, field
import json

from application.database_postgres.BaseModel import BasePayload, BaseModel, lst2pgarr

class ItemsModel(BaseModel):
    table_name = "items"

    @dataclass
    class Payload(BasePayload):
        item_info_id: int
        item_info_uuid: str
        logistics_info_id: int
        logistics_info_uuid: str
        food_info_id: int
        food_info_uuid: str
        barcode: str = ""
        item_name: str = ""
        brand: int = 0
        description: str = ""
        tags: list = field(default_factory=list)
        links: dict = field(default_factory=dict)
        row_type: str = ""
        item_type: str = ""
        search_string: str =""

        def payload_dictionary(self):
            payload = super().payload_dictionary()
            payload['tags'] = lst2pgarr(self.tags)
            payload['links'] = json.dumps(self.links)
            return payload