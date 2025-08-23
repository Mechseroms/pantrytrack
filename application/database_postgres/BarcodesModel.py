from dataclasses import dataclass
from application.database_postgres.BaseModel import BasePayload, BaseModel

class BarcodesModel(BaseModel):
    table_name = "barcodes"
    primary_key = "barcode"

    @dataclass
    class Payload(BasePayload):
        barcode: str
        item_uuid: str
        in_exchange: float
        out_exchange: float
        descriptor: str
            
