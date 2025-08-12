import psycopg2

from application import postsqldb
import config

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