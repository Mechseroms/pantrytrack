from dataclasses import dataclass, field
import json
import datetime
import psycopg2

from application.database_postgres.BaseModel import BasePayload, BaseModel, lst2pgarr, tupleDictionaryFactory, DatabaseError
import config

class UsersModel(BaseModel):
    table_name = "users"
    primary_key = "user_uuid"
    primary_key_type = "uuid"
    site_agnostic = True

    @dataclass
    class Payload(BasePayload):
        user_name:str
        user_password:str
        user_email: str
        user_flags: dict = field(default_factory=dict)
        user_favorites: dict = field(default_factory=dict)
        user_sites: list = field(default_factory=list)
        user_roles: list = field(default_factory=list)
        user_is_system_admin: bool = False
        user_row_type: str = "user"
        user_profile_pic_url: str = ""
        user_login_type: str = "Internal"
        user_joined_on: datetime.datetime = field(init=False)

        def __post_init__(self):
            self.creation_date = datetime.datetime.now()
        
        def payload_dictionary(self):
            payload = super().payload_dictionary()
            payload['user_flags'] = json.dumps(self.user_flags)
            payload['user_favorites'] = json.dumps(self.user_favorites)
            payload['user_sites'] = lst2pgarr(self.user_sites)
            payload['user_roles'] = lst2pgarr(self.user_roles)
            return payload
    
    @staticmethod
    def washUserDictionary(user):
        return {
            'user_uuid': user['user_uuid'],
            'user_name': user['user_name'],
            'user_sites': user['user_sites'],
            'user_roles': user['user_roles'],
            'user_is_system_admin': user['user_is_system_admin'],
            'user_flags': user['user_flags'],
            'user_profile_pic_url': user['user_profile_pic_url'],
            'user_login_type': user['user_login_type']
        }
    
    @classmethod
    def select_tuple_by_username(self, payload: dict, convert: bool = True, conn=None):
        record = ()
        self_conn = False
        sql = f"SELECT * FROM {self.table_name} WHERE user_name = %(key)s"
        
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
                    record = tupleDictionaryFactory(cur.description, rows)
                elif rows and not convert:
                    record = rows

            if self_conn:
                conn.commit()
                conn.close()

            return record
        
        except Exception as error:
            raise DatabaseError(error, payload, sql)