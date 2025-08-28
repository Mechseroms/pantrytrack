from dataclasses import dataclass, field
import json
import datetime

from application.database_postgres.BaseModel import BasePayload, BaseModel

class TransactionsModel(BaseModel):
    table_name = "transactions"
    primary_key = "item_uuid"
    primary_key_type = "uuid"

    @dataclass
    class Payload(BasePayload):
        item_uuid: str
        transaction_created_by: str
        transaction_name: str
        transaction_type: str
        transaction_created_at: datetime.datetime = field(init=False)
        transaction_quantity: float = 0.00
        transaction_description: str = ''
        transaction_cost: float = 0.00
        transaction_data: dict = field(default_factory=dict)

        def __post_init__(self):
            self.transaction_created_at = datetime.datetime.now()

        def payload_dictionary(self):
            payload = super().payload_dictionary()
            payload['transaction_data'] = json.dumps(self.transaction_data)
            return payload