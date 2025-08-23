from dataclasses import dataclass, field
import datetime

from application.database_postgres.BaseModel import BasePayload, BaseModel

class VendorsModel(BaseModel):
    table_name = "vendors"

    @dataclass
    class Payload(BasePayload):
        vendor_name: str
        created_by: int
        vendor_address: str = ""
        creation_date: datetime.datetime = field(init=False)
        phone_number: str = ""
        
        def __post_init__(self):
            self.creation_date = datetime.datetime.now()