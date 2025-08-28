from dataclasses import dataclass

from application.database_postgres.BaseModel import BasePayload, BaseModel

class LocationsModel(BaseModel):
    table_name = "locations"

    @dataclass
    class Payload(BasePayload):
        location_shortname: str
        location_name: str
        zone_uuid: str

    