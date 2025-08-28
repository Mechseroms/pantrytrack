from dataclasses import dataclass

from application.database_postgres.BaseModel import BasePayload, BaseModel

class LogisticsInfoModel(BaseModel):
    table_name = "logistics_info"
    primary_key_type = "uuid"
    primary_key = "item_uuid"

    @dataclass
    class Payload(BasePayload):
        item_uuid: str
        item_primary_location: str = None
        item_primary_zone: str = None
        item_auto_issue_location: str = None
        item_auto_issue_zone: str = None
    