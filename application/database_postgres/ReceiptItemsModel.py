from dataclasses import dataclass, field
import json

from application.database_postgres.BaseModel import BasePayload, BaseModel

class ReceiptItemsModel(BaseModel):
    table_name = "receipt_items"

    @dataclass
    class Payload(BasePayload):
        type: str
        receipt_id: int
        barcode: str
        item_uuid: str
        name: str
        qty: float = 1.0
        uom: str = "each"
        data: dict = field(default_factory=dict)
        status: str = "Unresolved"
        
        def payload_dictionary(self):
            payload = super().payload_dictionary()
            payload['data'] = json.dumps(self.data)
            return payload