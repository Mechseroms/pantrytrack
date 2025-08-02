import psycopg2

import config
from application import postsqldb

def requestNextReceiptID(site_name, conn=None):
    """gets the next id for receipts_id, currently returns a 8 digit number

    Args:
        site (str): site to get the next id for

    Returns:
        json: receipt_id, message, error keys
    """
    next_receipt_id = None
    self_conn = False
    sql = f"SELECT receipt_id FROM {site_name}_receipts ORDER BY id DESC LIMIT 1;"
    try:
        if not conn:
            database_config = config.config()
            conn = psycopg2.connect(**database_config)
            conn.autocommit = True
            self_conn = True

        with conn.cursor() as cur:
            cur.execute(sql)
            next_receipt_id = cur.fetchone()
            if next_receipt_id == None:
                next_receipt_id = "00000001"
            else:
                next_receipt_id = next_receipt_id[0]
                next_receipt_id = int(next_receipt_id.split("-")[1]) + 1
                y = str(next_receipt_id)
                len_str = len(y)
                x = "".join(["0" for _ in range(8 - len_str)])
                next_receipt_id = x + y
        
        if self_conn:
            conn.commit()
            conn.close()

        return next_receipt_id
    except (Exception, psycopg2.DatabaseError) as error:
        raise postsqldb.DatabaseError(error, payload=(), sql=sql)
    
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

def getReceiptByID(site, payload, convert=True, conn=None):
    receipt = []
    self_conn = False
    with open(f"application/receipts/sql/getReceiptByID.sql", "r+") as file:
        sql = file.read().replace("%%site_name%%", site)
    try:
        if not conn:
            database_config = config.config()
            conn = psycopg2.connect(**database_config)
            conn.autocommit = True
            self_conn = True

        with conn.cursor() as cur:
            cur.execute(sql, payload)
            row = cur.fetchone()
            if row and convert:
                receipt = postsqldb.tupleDictionaryFactory(cur.description, row)
            if row and not convert:
                receipt = row

        if self_conn:
            conn.close()

        return receipt
    except (Exception, psycopg2.DatabaseError) as error:
        raise postsqldb.DatabaseError(error, payload, sql)

def paginateReceiptsTuples(site, payload, convert=True, conn=None):
    """payload=(limit, offset)"""
    receipts = []
    count = 0
    self_conn = False
    with open(f"application/receipts/sql/getReceipts.sql", "r+") as file:
        sql = file.read().replace("%%site_name%%", site)
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
                receipts = [postsqldb.tupleDictionaryFactory(cur.description, row) for row in rows]
            if rows and not convert:
                receipts = rows

            cur.execute(f"SELECT COUNT(*) FROM {site}_receipts;")
            count = cur.fetchone()[0]
        
        if self_conn:
            conn.commit()
            conn.close()

        return receipts, count

    except (Exception, psycopg2.DatabaseError) as error:
        raise postsqldb.DatabaseError(error, payload, sql)

def paginateVendorsTuples(site, payload, convert=True, conn=None):
        """payload (tuple): (limit, offset)"""
        recordset = ()
        count = 0
        self_conn = False
        sql = f"SELECT * FROM {site}_vendors LIMIT %s OFFSET %s;"
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
                    recordset = [postsqldb.tupleDictionaryFactory(cur.description, row) for row in rows]
                elif rows and not convert:
                    recordset = rows

                cur.execute(f"SELECT COUNT(*) FROM {site}_vendors;")
                count = cur.fetchone()[0]
            
            if self_conn:
                conn.close()

            return recordset, count
        except Exception as error:
            raise postsqldb.DatabaseError(error, (), sql)

def paginateLinkedLists(site, payload, convert=True, conn=None):
        records = []
        count = 0
        self_conn = False
        sql = f"SELECT * FROM {site}_items WHERE row_type = 'list' LIMIT %s OFFSET %s;"
        sql_count = f"SELECT COUNT(*) FROM {site}_items WHERE row_type = 'list' LIMIT %s OFFSET %s;"
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
                    records = [postsqldb.tupleDictionaryFactory(cur.description, row) for row in rows]
                if rows and not convert:
                    records = rows

                cur.execute(sql_count, payload)
                count = cur.fetchone()[0]

            if self_conn:
                conn.close()

            return records, count
        except (Exception, psycopg2.DatabaseError) as error:
            raise postsqldb.DatabaseError(error, payload, sql)

def selectReceiptItemsTuple(site, payload, convert=True, conn=None):
    selected = ()
    self_conn = False
    sql = f"SELECT * FROM {site}_receipt_items WHERE id=%s;"

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
                selected = postsqldb.tupleDictionaryFactory(cur.description, rows)
            if rows and not convert:
                selected = rows
        
        if self_conn:
            conn.close()
        
        return selected
    except (Exception, psycopg2.DatabaseError) as error:
        raise postsqldb.DatabaseError(error, payload, sql)

def deleteReceiptItemsTuple(site, payload, convert=True, conn=None):
    deleted = ()
    self_conn = False
    sql = f"WITH deleted_rows AS (DELETE FROM {site}_receipt_items WHERE id IN ({','.join(['%s'] * len(payload))}) RETURNING *) SELECT * FROM deleted_rows;"
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
                deleted = [postsqldb.tupleDictionaryFactory(cur.description, r) for r in rows]
            elif rows and not convert:
                deleted = rows
        
        if self_conn:
            conn.commit()
            conn.close()

        return deleted
    except Exception as error:
        raise postsqldb.DatabaseError(error, payload, sql)

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

def insertReceiptsTuple(site, payload, convert=True, conn=None):
    receipt = ()
    self_conn = False
    with open(f"application/receipts/sql/insertReceiptsTuple.sql", "r+") as file:
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
                receipt = postsqldb.tupleDictionaryFactory(cur.description, rows)
            elif rows and not convert:
                receipt = rows
        
        if self_conn:
            conn.commit()
            conn.close()
        
        return receipt
    except Exception as error:
        raise postsqldb.DatabaseError(error, payload, sql)

def updateReceiptItemsTuple(site, payload, convert=True, conn=None):
    """_summary_

    Args:
        conn (_T_connector@connect): Postgresql Connector
        site (str):
        payload (dict): {'id': row_id, 'update': {... column_to_update: value_to_update_to...}}
        convert (bool, optional): determines if to return tuple as dictionary. Defaults to True.

    Raises:
        DatabaseError:

    Returns:
        tuple or dict: updated tuple
    """
    updated = ()
    self_conn = False

    set_clause, values = postsqldb.updateStringFactory(payload['update'])
    values.append(payload['id'])
    sql = f"UPDATE {site}_receipt_items SET {set_clause} WHERE id=%s RETURNING *;"
    try:

        if not conn:
            database_config = config.config()
            conn = psycopg2.connect(**database_config)
            conn.autocommit = True
            self_conn = True

        with conn.cursor() as cur:
            cur.execute(sql, values)
            rows = cur.fetchone()
            if rows and convert:
                updated = postsqldb.tupleDictionaryFactory(cur.description, rows)
            elif rows and not convert:
                updated = rows
        
        if self_conn:
            conn.commit()
            conn.close()

        return updated
    
    except Exception as error:
        raise postsqldb.DatabaseError(error, payload, sql)