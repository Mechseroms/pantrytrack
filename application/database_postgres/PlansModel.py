from dataclasses import dataclass
from application.database_postgres.BaseModel import BasePayload, BaseModel

class PlansModel(BaseModel):
    table_name = "plans"

    @dataclass
    class Payload(BasePayload):
        plan_shortname: str
        plan_description: str
        created_by: int
            
