from application import postsqldb
import config
import psycopg2 


def getTransactions(site:str, payload: tuple, convert:bool=True):
    database_config = config.config()
    sql = f"SELECT * FROM {site}_transactions WHERE logistics_info_id=%s LIMIT %s OFFSET %s;"
    sql_count = f"SELECT COUNT(*) FROM {site}_transactions WHERE logistics_info_id=%s;"
    recordset = ()
    count = 0
    try:
        with psycopg2.connect(**database_config) as conn:
            with conn.cursor() as cur:
                cur.execute(sql, payload)
                rows = cur.fetchall()
                if rows and convert:
                    recordset = [postsqldb.tupleDictionaryFactory(cur.description, row) for row in rows]
                if rows and not convert:
                    recordset = rows
                cur.execute(sql_count, (payload[0],))
                count = cur.fetchone()[0]
            return recordset, count
    except Exception as error:
        postsqldb.DatabaseError(error, payload, sql)

def getTransaction(site:str, payload: tuple, convert:bool=True):
    database_config = config.config()
    sql = f"SELECT * FROM {site}_transactions WHERE id=%s;"
    record = ()
    try:
        with psycopg2.connect(**database_config) as conn:
            with conn.cursor() as cur:
                cur.execute(sql, payload)
                rows = cur.fetchone()
                if rows and convert:
                    record = postsqldb.tupleDictionaryFactory(cur.description, rows)
                if rows and not convert:
                    record = rows
            return record
    except Exception as error:
        postsqldb.DatabaseError(error, payload, sql)

def getItemAllByID(site:str, payload: tuple, convert:bool=True):
    database_config = config.config()
    with open('application/items/sql/getItemAllByID.sql', 'r+') as file:
        sql = file.read().replace("%%site_name%%", site)
    record = ()
    try:
        with psycopg2.connect(**database_config) as conn:
            with conn.cursor() as cur:
                cur.execute(sql, payload)
                rows = cur.fetchone()
                if rows and convert:
                    record = postsqldb.tupleDictionaryFactory(cur.description, rows)
                if rows and not convert:
                    record = rows
            return record
    except Exception as error:
        postsqldb.DatabaseError(error, payload, sql)

def getItemsWithQOH(site:str, payload: tuple, convert:bool=True):
    database_config = config.config()
    with open('application/items/sql/getItemsWithQOH.sql', 'r+') as file:
        sql = file.read().replace("%%site_name%%", site).replace("%%sort_order%%", payload[3])
    payload = list(payload)
    payload.pop(3)
    sql_count = f"SELECT COUNT(*) FROM {site}_items WHERE search_string LIKE '%%' || %s || '%%';"
    recordset = ()
    count = 0
    try:
        with psycopg2.connect(**database_config) as conn:
            with conn.cursor() as cur:
                cur.execute(sql, payload)
                rows = cur.fetchall()
                if rows and convert:
                    recordset = [postsqldb.tupleDictionaryFactory(cur.description, row) for row in rows]
                if rows and not convert:
                    recordset = rows
                cur.execute(sql_count, (payload[0],))
                count = cur.fetchone()[0]
            return recordset, count
    except Exception as error:
        postsqldb.DatabaseError(error, payload, sql)