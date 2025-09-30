from dataclasses import dataclass
import datetime

import config
import psycopg2
from application.database_postgres.BaseModel import BasePayload, BaseModel, tupleDictionaryFactory, DatabaseError, updateStringFactory

class CostLayersModel(BaseModel):
    table_name = "cost_layers"
    primary_key = "item_location_uuid"
    primary_key_type = "uuid"

    @dataclass
    class Payload(BasePayload):
        item_location_uuid: str
        layer_aquisition_date: datetime.datetime
        layer_quantity: float
        layer_cost: float
        layer_currency_type: str
        layer_vendor: str = None
        layer_expires: datetime.datetime = None

    @classmethod
    def delete_by_layer_id(self, site: str, payload: tuple, convert: bool = True, conn=None):
        """ Pass a tuple of layer_ids to remove from the database.

        Args:
            site (str): name of the site to delete from
            payload (tuple): a tuple of layer_ids
            convert (bool, optional): whether to return the deleted rows as dictionaries. Defaults to True.
            conn (_type_, optional): postgresql connector object. Defaults to None.

        Raises:
            DatabaseError: raised for all errors with database handling, logs to database.log

        Returns:
            dict, list: returns a list of all deleted rows. 
        """
        deleted = ()
        self_conn = False
        sql = f"WITH deleted_rows AS (DELETE FROM {site}_{self.table_name} WHERE layer_id IN ({','.join(['%s'] * len(payload))}) RETURNING *) SELECT * FROM deleted_rows;"
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
    def update_by_layer_id(self, site: str, payload:dict, convert=True, conn=None):
        updated = ()
        self_conn = False
        set_clause, values = updateStringFactory(payload['update'])
        values.append(payload['key'])
        sql = f"UPDATE {site}_{self.table_name} SET {set_clause} WHERE layer_id=%s RETURNING *;"
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