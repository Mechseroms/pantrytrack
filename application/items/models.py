import psycopg2

from application.database_postgres.TransactionsModel import TransactionsModel
from application.database_postgres.ItemsModel import ItemsModel
from application.database_postgres.BaseModel import tupleDictionaryFactory, DatabaseError
import config

class ExtendedItemsModel(ItemsModel):
    @classmethod
    def get_item_for_transactions(self, site: str, payload: dict, convert=True, conn=None):
        with open('application/items/sql/getItemForTransaction.sql', 'r+') as file:
            sql = file.read().replace("%%site_name%%", site)

        record = ()
        self_conn = False
        
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
                conn.close()
            
            return record
        except Exception as error:
            raise DatabaseError(error, {}, sql)

class ExtendedTransactionModel(TransactionsModel):
    @classmethod
    def paginate_transactions_by_item_uuid(self, site:str, payload:dict, convert=True, conn=None):
        sql = f"SELECT * FROM {site}_transactions WHERE item_uuid = %(item_uuid)s::uuid LIMIT %(limit)s OFFSET %(offset)s;"
        sql_count = f"SELECT COUNT(*) FROM {site}_transactions WHERE item_uuid=%(item_uuid)s::uuid;"
        records = ()
        self_conn = False
        
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
                    records = [tupleDictionaryFactory(cur.description, row) for row in rows]
                elif rows and not convert:
                    records = rows

                cur.execute(sql_count, payload)
                count = cur.fetchone()[0]

            if self_conn:
                conn.commit()
                conn.close()

            return records, count
        
        except Exception as error:
            raise DatabaseError(error, {}, sql)