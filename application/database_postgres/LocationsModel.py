from dataclasses import dataclass

from application.database_postgres.BaseModel import BasePayload, BaseModel

class LocationsModel(BaseModel):
    table_name = "locations"

    @dataclass
    class Payload(BasePayload):
        uuid: str
        name: str
        zone_id: int
    