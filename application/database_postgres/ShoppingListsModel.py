from dataclasses import dataclass, field
import datetime
from application.database_postgres.BaseModel import BasePayload, BaseModel

class ShoppingListsModel(BaseModel):
    table_name = "shopping_lists"

    @dataclass
    class Payload(BasePayload):
        name: str
        description: str
        author: int
        sub_type: str = "plain"
        creation_date: datetime.datetime = field(init=False)
        list_type: str = "temporary"

        def __post_init__(self):
            self.creation_date = datetime.datetime.now()