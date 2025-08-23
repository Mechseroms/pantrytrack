from dataclasses import dataclass

from application.database_postgres.BaseModel import BasePayload, BaseModel

class ZonesModel(BaseModel):
    table_name = "zones"

    @dataclass
    class Payload(BasePayload):
        name: str
        description: str = ""
    