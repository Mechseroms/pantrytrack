from dataclasses import dataclass, field
from application.database_postgres.BaseModel import BasePayload, BaseModel, lst2pgarr, tupleDictionaryFactory, DatabaseError

import config

import psycopg2

class ItemLocationsModel(BaseModel):
    table_name = "item_locations"
    primary_key = "item_location_uuid"
    primary_key_type = 'uuid'

    @dataclass
    class Payload(BasePayload):
        item_uuid: str
        location_uuid: str
        item_quantity_on_hand: float = 0.0
    
    @classmethod
    def select_by_location_and_item(self, site:str, payload:dict, convert: bool=True, conn = None):
        recordset = ()
        self_conn = False
        sql = f"SELECT * FROM {site}_item_locations WHERE item_uuid = %(item_uuid)s AND location_uuid = %(location_uuid)s;"
        try:
            if not conn:
                database_config = config.config()
                conn = psycopg2.connect(**database_config)
                conn.autocommit = True
                self_conn = True

            with conn.cursor() as cur:
                cur.execute(sql, payload)
                rows = cur.fetchone()
                if rows and convert:
                    recordset = tupleDictionaryFactory(cur.description, rows)
                if rows and not convert:
                    recordset = rows


            if self_conn:
                conn.close()

            return recordset
        
        except Exception as error:
            raise DatabaseError(error, payload, sql)