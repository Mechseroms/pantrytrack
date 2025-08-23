from dataclasses import dataclass
import datetime

from application.database_postgres.BaseModel import BasePayload, BaseModel

class PlanEventsModel(BaseModel):
    table_name = "plan_events"

    @dataclass
    class Payload(BasePayload):
        plan_uuid: str
        event_shortname: str
        event_description: str
        event_date_start: datetime.datetime
        event_date_end: datetime.datetime
        created_by: int
        recipe_uuid: str
        receipt_uuid: str
        event_type: str
            
