from dataclasses import dataclass, field
import datetime

from application.database_postgres.BaseModel import BasePayload, BaseModel

class VendorsModel(BaseModel):
    table_name = "vendors"

    @dataclass
    class Payload(BasePayload):
        vendor_name: str
        vendor_created_by: str
        vendor_address: str = ""
        vendor_creation_date: datetime.datetime = field(init=False)
        vendor_phone_number: str = ""
        
        def __post_init__(self):
            self.vendor_creation_date = datetime.datetime.now()