from dataclasses import dataclass, field
import datetime

from application.database_postgres.BaseModel import BasePayload, BaseModel, lst2pgarr

class RecipesModel(BaseModel):
    table_name = "recipes"

    @dataclass
    class Payload(BasePayload):
        name: str
        author: int
        description: str
        creation_date: datetime.datetime = field(init=False)
        instructions: list = field(default_factory=list)
        picture_path: str = ""

        def __post_init__(self):
            self.creation_date = datetime.datetime.now()

        def payload_dictionary(self):
            payload = super().payload_dictionary()
            payload['instructions'] = lst2pgarr(self.instructions)
            return payload