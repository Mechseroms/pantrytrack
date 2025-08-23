from dataclasses import dataclass, field
import json
import datetime

from application.database_postgres.BaseModel import BasePayload, BaseModel

class TransactionsModel(BaseModel):
    table_name = "transactions"

    @dataclass
    class Payload(BasePayload):
        timestamp: datetime.datetime
        logistics_info_id: int
        barcode: str
        name: str
        transaction_type: str
        quantity: float
        description: str
        user_id: int
        data: dict = field(default_factory=dict)

        def payload_dictionary(self):
            payload = super().payload_dictionary()
            payload['data'] = json.dumps(self.data)
            return payload