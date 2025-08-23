from dataclasses import dataclass, field
import json
import datetime

from application.database_postgres.BaseModel import BasePayload, BaseModel

class ReceiptsModel(BaseModel):
    table_name = "receipts"

    @dataclass
    class Payload(BasePayload):
        receipt_id: str
        receipt_status: str = "Unresolved"
        date_submitted: datetime.datetime = field(init=False)
        submitted_by: int = 0
        vendor_id: int = 1
        files: dict = field(default_factory=dict)

        def __post_init__(self):
            self.date_submitted = datetime.datetime.now()
        
        def payload_dictionary(self):
            payload = super().payload_dictionary()
            payload['files'] = json.dumps(self.files)
            return payload