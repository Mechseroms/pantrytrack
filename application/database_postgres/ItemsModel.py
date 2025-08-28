from dataclasses import dataclass, field
import json
import psycopg2
import datetime

from application.database_postgres.BaseModel import BasePayload, BaseModel, lst2pgarr, DatabaseError, tupleDictionaryFactory
import config
class ItemsModel(BaseModel):
    table_name = "items"
    primary_key = "item_uuid"
    primary_key_type = "uuid"

    @dataclass
    class Payload(BasePayload):
        item_category: str
        item_name: str
        item_created_at: datetime.datetime = field(init=False)
        item_updated_at: datetime.datetime = field(init=False)
        item_description: str = ""
        item_tags: list = field(default_factory=list)
        item_links: dict = field(default_factory=dict)
        item_brand_uuid: str = None
        item_search_string: str = ""
        item_inactive: bool = False

        def __post_init__(self):
            self.item_created_at = datetime.datetime.now()
            self.item_updated_at = datetime.datetime.now()

        def payload_dictionary(self):
            payload = super().payload_dictionary()
            payload['item_tags'] = lst2pgarr(self.item_tags)
            payload['item_links'] = json.dumps(self.item_links)
            return payload

    @classmethod 
    def paginate_items_with_qoh(self, site:str, payload: dict, convert: bool=True, conn = None):
        recordset = ()
        count = 0
        self_conn = False
        with open('application/database_postgres/sql/ItemsModel/paginateItemsWithQOH.sql', 'r+') as file:
            sql = file.read().replace("%%site_name%%", site).replace("%%sort_order%%", payload['sort_order'])
        sql_count = f"SELECT COUNT(*) FROM {site}_{self.table_name} items WHERE items.item_search_string LIKE '%%' || %(search_string)s || '%%';"
        recordset = ()
        count = 0
        try:
            if not conn:
                database_config = config.config()
                conn = psycopg2.connect(**database_config)
                conn.autocommit = True
                self_conn = True

            with conn.cursor() as cur:
                cur.execute(sql, payload)
                rows = cur.fetchall()
                if rows and convert:
                    recordset = [tupleDictionaryFactory(cur.description, row) for row in rows]
                if rows and not convert:
                    recordset = rows

                cur.execute(sql_count, payload)
                count = cur.fetchone()[0]

            if self_conn:
                conn.close()

            return recordset, count
        
        except Exception as error:
            raise DatabaseError(error, payload, sql)
    
    @classmethod 
    def paginate_items_for_modal(self, site:str, payload: dict, convert: bool=True, conn = None):
        recordset = ()
        count = 0
        self_conn = False
        with open('application/database_postgres/sql/ItemsModel/paginateItemsForModal.sql', 'r+') as file:
            sql = file.read().replace("%%site_name%%", site).replace("%%sort_order%%", payload['sort_order'])
        sql_count = f"SELECT COUNT(*) FROM {site}_{self.table_name} items WHERE items.item_search_string LIKE '%%' || %(search_string)s || '%%';"
        recordset = ()
        count = 0
        try:
            if not conn:
                database_config = config.config()
                conn = psycopg2.connect(**database_config)
                conn.autocommit = True
                self_conn = True

            with conn.cursor() as cur:
                cur.execute(sql, payload)
                rows = cur.fetchall()
                if rows and convert:
                    recordset = [tupleDictionaryFactory(cur.description, row) for row in rows]
                if rows and not convert:
                    recordset = rows

                cur.execute(sql_count, payload)
                count = cur.fetchone()[0]

            if self_conn:
                conn.close()

            return recordset, count
        
        except Exception as error:
            raise DatabaseError(error, payload, sql)