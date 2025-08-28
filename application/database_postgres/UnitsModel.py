from dataclasses import dataclass, field

from application.database_postgres.BaseModel import BasePayload, BaseModel, lst2pgarr, tupleDictionaryFactory, DatabaseError

class UnitsModel(BaseModel):
    table_name = "units"
    primary_key = "units_uuid"
    primary_key_type = "uuid"
    site_agnostic = True

    @dataclass
    class Payload(BasePayload):
        unit_plural:str
        unit_single:str
        unit_fullname: str
        unit_description: str
    