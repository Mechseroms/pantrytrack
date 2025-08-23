import psycopg2

from application import postsqldb
import config

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

def paginateRecipesTuples(site: str, payload: tuple, convert=True, conn=None):
    self_conn = False
    recipes = ()
    count = 0
    sql = f"SELECT * FROM {site}_recipes ORDER BY name ASC LIMIT %s OFFSET %s;"
    sql_count = f"SELECT COUNT(*) FROM {site}_recipes;"
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
                recipes = [postsqldb.tupleDictionaryFactory(cur.description, row) for row in rows]
            if rows and not convert:
                recipes = rows

            cur.execute(sql_count)
            count = cur.fetchone()[0]

        if self_conn:
            conn.close()

        return recipes, count
    except Exception as error:
        raise postsqldb.DatabaseError(error, payload, sql)

def paginateVendorsTuples(site: str, payload: tuple, convert=True, conn=None):
    self_conn = False
    recipes = ()
    count = 0
    sql = f"SELECT * FROM {site}_vendors ORDER BY vendor_name ASC LIMIT %s OFFSET %s;"
    sql_count = f"SELECT COUNT(*) FROM {site}_vendors;"
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
                recipes = [postsqldb.tupleDictionaryFactory(cur.description, row) for row in rows]
            if rows and not convert:
                recipes = rows

            cur.execute(sql_count)
            count = cur.fetchone()[0]

        if self_conn:
            conn.close()

        return recipes, count
    except Exception as error:
        raise postsqldb.DatabaseError(error, payload, sql)

def selectPlanEventsByMonth(site: str, payload: tuple, convert=True, conn=None):
    """payload=(year, month)"""
    self_conn = False
    event_tuples = ()


    with open('application/meal_planner/sql/selectPlanEventsByMonth.sql', 'r+') as file:
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
                event_tuples = [postsqldb.tupleDictionaryFactory(cur.description, row) for row in rows]
            if rows and not convert:
                event_tuples = rows


        if self_conn:
            conn.close()

        return event_tuples
    except Exception as error:
        raise postsqldb.DatabaseError(error, payload, sql)

def selectPlanEventByUUID(site: str, payload: tuple, convert=True, conn=None):
    """payload=(event_uuid,)"""
    self_conn = False
    event_tuple = ()

    sql = f"SELECT * FROM {site}_plan_events WHERE event_uuid = %s;"

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
                event_tuple = postsqldb.tupleDictionaryFactory(cur.description, rows)
            if rows and not convert:
                event_tuple = rows


        if self_conn:
            conn.close()

        return event_tuple
    except Exception as error:
        raise postsqldb.DatabaseError(error, payload, sql)

def selectConversionsTuple(site: str, payload: tuple, convert=True, conn=None):
    """payload=(event_uuid,)"""
    self_conn = False
    conversions = ()

    sql = f"SELECT * FROM {site}_conversions WHERE item_id = %s AND uom_id = %s;"

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
                conversions = postsqldb.tupleDictionaryFactory(cur.description, rows)
            if rows and not convert:
                conversions = rows


        if self_conn:
            conn.close()

        return conversions
    except Exception as error:
        raise postsqldb.DatabaseError(error, payload, sql)

def insertPlanEventTuple(site: str, payload: tuple, convert=True, conn=None):
    self_conn = False
    event_tuple = ()

    with open('application/meal_planner/sql/insertPlanEvent.sql', 'r+') as file:
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
                event_tuple = postsqldb.tupleDictionaryFactory(cur.description, rows)
            if rows and not convert:
                event_tuple = rows


        if self_conn:
            conn.commit()
            conn.close()

        return event_tuple
    except Exception as error:
        raise postsqldb.DatabaseError(error, payload, sql)

def insertReceiptItemsTuple(site, payload, convert=True, conn=None):
    receipt_item = ()
    self_conn = False
    with open(f"application/meal_planner/sql/insertReceiptItemsTuple.sql", "r+") as file:
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
    with open(f"application/meal_planner/sql/insertReceiptsTuple.sql", "r+") as file:
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

def updatePlanEventTuple(site:str, payload: dict, convert=True, conn=None):
    """ payload (dict): {'barcode': row_id, 'update': {... column_to_update: value_to_update_to...}} """
    updated = ()
    self_conn = False
    set_clause, values = postsqldb.updateStringFactory(payload['update'])
    values.append(payload['uuid'])
    sql = f"UPDATE {site}_plan_events SET {set_clause} WHERE event_uuid=%s RETURNING *;"
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
                updated = postsqldb.tupleDictionaryFactory(cur.description, rows)
            elif rows and not convert:
                updated = rows
        
        if self_conn:
            conn.commit()
            conn.close()

        return updated

    except Exception as error:
        raise postsqldb.DatabaseError(error, payload, sql)
    
def deletePlanEventTuple(site, payload, convert=True, conn=None):
    """ payload = (ids...)"""
    deleted = ()
    self_conn = False
    sql = f"WITH deleted_rows AS (DELETE FROM {site}_plan_events WHERE event_uuid IN ({','.join(['%s'] * len(payload))}) RETURNING *) SELECT * FROM deleted_rows;"
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