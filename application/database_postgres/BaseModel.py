from abc import ABC
import psycopg2
import datetime
import uuid
import json
import random
import string
from copy import deepcopy

import config


def validateUUID(uuid_string, version):
    try:
        u = uuid.UUID(uuid_string, version=version)
        return u.version == version
    except ValueError:
        return False

class DatabaseError(Exception):
    def __init__(self, message, payload=[], sql=""):
        super().__init__(message)
        self.payload = payload
        self.message = str(message).replace("\n", "")
        self.sql = sql.replace("\n", "")
        self.log_error()

    def log_error(self):
        with open("logs/database.log", "a+") as file:
            file.write("\n")
            file.write(f"{datetime.datetime.now()} --- ERROR --- DatabaseError(message='{self.message}',\n")
            file.write(f"{" "*41}payload={self.payload},\n")
            file.write(f"{" "*41}sql='{self.sql}')")

    def __str__(self):
        return f"DatabaseError(message='{self.message}', payload={self.payload}, sql='{self.sql}')"

def tupleDictionaryFactory(columns, row):
    columns = [desc[0] for desc in columns]
    return dict(zip(columns, row))

def lst2pgarr(alist):
    return '{' + ','.join(alist) + '}'

def updateStringFactory(updated_values: dict):
    set_clause = ', '.join([f"{key} = %s" for key in updated_values.keys()])
    values = []
    for value in updated_values.values():
        if isinstance(value, dict):
            value = json.dumps(value)
        values.append(value)

    return set_clause, values

def getUUID(n):
    random_string = ''.join(random.choices(string.ascii_letters + string.digits, k=n))
    return random_string

class BasePayload(ABC):
    """BasePayloads holds the bare minimum methods required of a Payload. """
    def payload_dictionary(self):
        return deepcopy(self.__dict__)

class BaseModel(ABC):
    """Base Model holds the CRUD functionality for database management. Anything beyond what is built in this
    model must be built into the specific models Class that extends this Class. 
    
    For each of these CRUD methods to work there must be a SQL file named {table_name}.sql inside of the 
    sql/INSERT, sql/CREATE, and sql/DROP that defines basic operations.

    Inheritors MUST assign a 'table_name' and 'primary_key' class level variable. They must also define
    a 'Payload' inner dataclass that returns a matching data scheme for INSERT basic funtions. You can
    have any payloads inherit the BasePayload class in order to get basic payload functions intended to
    be used in these basic operations.

    """
    table_name: str = None # All extended class must assign a table name that CRUD uses to call upon
    primary_key: str = 'id' # All extended class can assign a different primary key/cloumn which is used to call delete and update queries on.

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        if not hasattr(cls, 'Payload'):
            raise NotImplementedError(
                f"{cls.__name__} must define an inner Payload class."
            )
        if not hasattr(cls, 'table_name') or cls.table_name is None:
            raise NotImplementedError(f"{cls.__name__} must define 'table_name' class variable.")
        if not hasattr(cls, 'primary_key') or cls.primary_key is None:
            raise NotImplementedError(f"{cls.__name__} must define 'primary_key' class variable.")
        if not isinstance(cls.table_name, str):
            raise ValueError(f"{cls.__name__} must have table_name that is of type str")
        if not isinstance(cls.primary_key, str):
            raise ValueError(f"{cls.__name__} must have primary_key that is of type str")
        
    @classmethod
    def create_table(self, site, conn=None):
        self_conn = False
        with open(f"application/database_postgres/sql/CREATE/{self.table_name}.sql", 'r') as file:
            sql = file.read().replace("%%site_name%%", site)
        try:
            if not conn:
                database_config = config.config()
                conn = psycopg2.connect(**database_config)
                conn.autocommit = True
                self_conn = True

            with conn.cursor() as cur:
                cur.execute(sql)
            
            if self_conn:
                conn.commit()
                conn.close()

        except Exception as error: 
            raise DatabaseError(error, sql, self.table_name)

    @classmethod
    def drop_table(self, site, conn=None):
        self_conn = False
        with open(f"application/database_postgres/sql/DROP/{self.table_name}.sql", 'r') as file:
            sql = file.read().replace("%%site_name%%", site)
        try:
            if not conn:
                database_config = config.config()
                conn = psycopg2.connect(**database_config)
                conn.autocommit = True
                self_conn = True

            with conn.cursor() as cur:
                cur.execute(sql)

            if self_conn:
                conn.commit()
                conn.close()

        except Exception as error: 
            raise DatabaseError(error, sql, self.table_name)

    @classmethod
    def delete_tuples(self, site: str, payload: tuple, convert: bool = True, conn=None):
        deleted = ()
        self_conn = False
        sql = f"WITH deleted_rows AS (DELETE FROM {site}_{self.table_name} WHERE {self.primary_key} IN ({','.join(['%s'] * len(payload))}) RETURNING *) SELECT * FROM deleted_rows;"
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
    def update_tuple(self, site: str, payload: dict, convert: bool = True, conn=None):
        """ payload (dict): {'key': row_id, 'update': {... column_to_update: value_to_update_to...}} """
        updated = ()
        self_conn = False
        set_clause, values = updateStringFactory(payload['update'])
        values.append(payload['key'])
        sql = f"UPDATE {site}_{self.table_name} SET {set_clause} WHERE {self.primary_key}=%s RETURNING *;"
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
    def insert_tuple(self, site: str, payload: dict, convert: bool = True, conn=None):
        record = ()
        self_conn = False
        
        with open(f"application/database_postgres/sql/INSERT/{self.table_name}.sql", 'r') as file:
            sql = file.read().replace("%%site_name%%", site)
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
