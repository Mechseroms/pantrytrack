import psycopg2


import config
from application import postsqldb

def getItemsWithQOH(site, payload, convert=True, conn=None):
    recordset = []
    count = 0
    self_conn = False
    with open(f"application/receipts/sql/getItemsWithQOH.sql", "r+") as file:
        sql = file.read().replace("%%site_name%%", site).replace("%%sort_order%%", payload[3])

    payload = list(payload)
    payload.pop(3)
    try:
        if not conn:
            database_config = config.config()
            conn = psycopg2.connect(**database_config)
            conn.autocommit = True
            self_conn = True

        if convert:
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                cur.execute(sql, payload)
                recordset = cur.fetchall()
                recordset = [dict(record) for record in recordset]
                cur.execute(f"SELECT COUNT(*) FROM {site}_items WHERE search_string LIKE '%%' || %s || '%%';", (payload[0], ))
                count = cur.fetchone()
        else:   
            with conn.cursor() as cur:
                cur.execute(sql, payload)
                recordset = cur.fetchall()
                cur.execute(f"SELECT COUNT(*) FROM {site}_items WHERE search_string LIKE '%%' || %s || '%%';", (payload[0], ))
                count = cur.fetchone()
        
        if self_conn:
            conn.close()
        
        return recordset, count
    except Exception as error:
        raise postsqldb.DatabaseError(error, payload, sql)

def getItemAllByID(site, payload, convert=True, conn=None):
    item = ()
    self_conn = False

    with open(f"application/receipts/sql/getItemAllByID.sql", "r+") as file:
        getItemAllByID_sql = file.read().replace("%%site_name%%", site)
    try:
        if not conn:
            database_config = config.config()
            conn = psycopg2.connect(**database_config)
            conn.autocommit = True
            self_conn = True

        with conn.cursor() as cur:
            cur.execute(getItemAllByID_sql, payload)
            rows = cur.fetchone()
            if rows and convert:
                item = postsqldb.tupleDictionaryFactory(cur.description, rows)
            if rows and not convert:
                item = rows
        
        if self_conn:
            conn.close()
        
        return item
    except (Exception, psycopg2.DatabaseError) as error:
        raise postsqldb.DatabaseError(error, payload, getItemAllByID_sql)
    


def insertReceiptItemsTuple(site, payload, convert=True, conn=None):
    receipt_item = ()
    self_conn = False
    with open(f"application/receipts/sql/insertReceiptItemsTuple.sql", "r+") as file:
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
                receipt_item = postsqldb.tupleDictionaryFactory(cur.description, rows)
            elif rows and not convert:
                receipt_item = rows
        
        if self_conn:
            conn.commit()
            conn.close()
        
        return receipt_item
    except Exception as error:
        raise postsqldb.DatabaseError(error, payload, sql)