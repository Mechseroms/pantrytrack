from dataclasses import dataclass, field
import json
import datetime
import psycopg2

from application.database_postgres.BaseModel import (
    BasePayload, BaseModel, tupleDictionaryFactory, DatabaseError, updateStringFactory
    )
import config

class SitesModel(BaseModel):
    table_name = "sites"
    primary_key = "site_uuid"
    primary_key_type = "uuid"
    site_agnostic = True
    
    @dataclass
    class Payload(BasePayload):
        site_name: str
        site_description: str
        site_created_by: str
        site_default_zone_uuid: str = None
        site_default_auto_issue_location_uuid: str = None
        site_default_primary_location_uuid: str = None
        site_created_on: datetime.datetime = field(init=False)
        site_flags: dict = field(default_factory=dict)

        def __post_init__(self):
            self.site_created_on = datetime.datetime.now()
        
        def payload_dictionary(self):
            payload = super().payload_dictionary()
            payload['site_flags'] = json.dumps(self.site_flags)
            return payload
    
    @classmethod
    def delete_tuples(self, payload: tuple, convert: bool = True, conn=None):
        deleted = ()
        self_conn = False
        sql = f"WITH deleted_rows AS (DELETE FROM {self.table_name} WHERE {self.primary_key} IN ({','.join(['%s'] * len(payload))}) RETURNING *) SELECT * FROM deleted_rows;"
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
                    deleted = [tupleDictionaryFactory(cur.description, r) for r in rows]
                elif rows and not convert:
                    deleted = rows
            
            if self_conn:
                conn.commit()
                conn.close()

            return deleted
        except Exception as error:
            raise DatabaseError(error, payload, sql)

    @classmethod
    def update_tuple(self, payload: dict, convert=True, conn=None):
        """ payload (dict): {'key': row_id, 'update': {... column_to_update: value_to_update_to...}} """
        updated = ()
        self_conn = False
        set_clause, values = updateStringFactory(payload['update'])
        values.append(payload['key'])
        sql = f"UPDATE {self.table_name} SET {set_clause} WHERE {self.primary_key}=%s RETURNING *;"
        try:
            if not conn:
                database_config = config.config()
                conn = psycopg2.connect(**database_config)
                conn.autocommit = False
                self_conn = True

            with conn.cursor() as cur:
                cur.execute(sql, values)
                rows = cur.fetchone()
                if rows and convert:
                    updated = tupleDictionaryFactory(cur.description, rows)
                elif rows and not convert:
                    updated = rows
            
            if self_conn:
                conn.commit()
                conn.close()

            return updated
        except Exception as error:
            raise DatabaseError(error, payload, sql)
        
    @classmethod
    def select_all(self, payload: dict, convert=True, conn=None):
        record = ()
        self_conn = False
        sql = f"SELECT * FROM {self.table_name} WHERE {self.primary_key}=%(key)s;"
        try:
            if not conn:
                database_config = config.config()
                conn = psycopg2.connect(**database_config)
                conn.autocommit = False
                self_conn = True

            with conn.cursor() as cur:
                cur.execute(sql, payload)
                rows = cur.fetchone()
                if rows and convert:
                    record = tupleDictionaryFactory(cur.description, rows)
                elif rows and not convert:
                    record = rows
            
            if self_conn:
                conn.commit()
                conn.close()

            return record
        except Exception as error:
            raise DatabaseError(error, payload, sql)