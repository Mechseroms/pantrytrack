from dataclasses import dataclass, field
import json
import config
import psycopg2

from application.database_postgres.BaseModel import BasePayload, BaseModel, DatabaseError, tupleDictionaryFactory

class RolesModel(BaseModel):
    table_name = "roles"
    primary_key = "role_uuid"

    @dataclass
    class Payload(BasePayload):
        role_name: str
        role_description: str
        role_site_uuid: str
        role_flags: dict = field(default_factory=dict)
        
        def payload_dictionary(self):
            payload = super().payload_dictionary()
            payload['role_flags'] = json.dumps(self.role_flags)
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