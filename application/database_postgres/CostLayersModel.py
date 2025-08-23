from dataclasses import dataclass
import datetime

from application.database_postgres.BaseModel import BasePayload, BaseModel

class CostLayersModel(BaseModel):
    table_name = "cost_layers"

    @dataclass
    class Payload(BasePayload):
        aquisition_date: datetime.datetime
        quantity: float
        cost: float
        currency_type: str
        vendor: int = 0
        expires: datetime.datetime = None
    