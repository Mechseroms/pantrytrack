from dataclasses import dataclass

from application.database_postgres.BaseModel import BasePayload, BaseModel

class LogisticsInfoModel(BaseModel):
    table_name = "logistics_info"

    @dataclass
    class Payload(BasePayload):
        barcode: str
        primary_location: int
        primary_zone: int
        auto_issue_location: int
        auto_issue_zone: int
    