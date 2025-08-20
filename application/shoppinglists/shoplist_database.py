# 3rd Party imports
import psycopg2

# applications imports
import config
from application import postsqldb

def getShoppingList(site, payload, convert=True, conn=None):
    recordset = []
    self_conn = False

    with open(f"application/shoppinglists/sql/getShoppingListByID.sql", "r+") as file:
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
                recordset = postsqldb.tupleDictionaryFactory(cur.description, rows)
            if rows and not convert:
                recordset = rows
        
        if self_conn:
            conn.close()

        return recordset

    except (Exception, psycopg2.DatabaseError) as error:
        raise postsqldb.DatabaseError(error, payload, sql)

def getShoppingLists(site, payload, convert=True, conn=None):
    recordset = []
    count = 0
    self_conn = False
    with open(f"application/shoppinglists/sql/getShoppingLists.sql", "r+") as file:
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
                recordset = [postsqldb.tupleDictionaryFactory(cur.description, row) for row in rows]
            if rows and not convert:
                recordset = rows

            cur.execute(f"SELECT COUNT(*) FROM {site}_shopping_lists;")
            count = cur.fetchone()[0]

        if self_conn:
            conn.close()

        return recordset, count
    except (Exception, psycopg2.DatabaseError) as error:
        raise postsqldb.DatabaseError(error, payload, sql)

def getItemsSafetyStock(site, convert=True, conn=None):
    recordsets = []
    self_conn = False
    with open(f"application/shoppinglists/sql/getItemsSafetyStock.sql", "r+") as file:
        sql = file.read().replace("%%site_name%%", site)
    try:
        if not conn:
            database_config = config.config()
            conn = psycopg2.connect(**database_config)
            conn.autocommit = True
            self_conn = True

        with conn.cursor() as cur:
            cur.execute(sql)
            rows = cur.fetchall()
            if rows and convert:
                recordsets = [postsqldb.tupleDictionaryFactory(cur.description, row) for row in rows]
            if rows and not convert:
                recordsets = rows
        
        if self_conn:
            conn.close()

        return recordsets

    except (Exception, psycopg2.DatabaseError) as error:
        raise postsqldb.DatabaseError(error, None, sql)

def getShoppingListItem(site, payload, convert=True, conn=None):
    record = ()
    self_conn = False
    with open('application/shoppinglists/sql/selectShoppingListItem.sql', 'r') as file:
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
                record = postsqldb.tupleDictionaryFactory(cur.description, rows)
            elif rows and not convert:
                record = rows
        
        if self_conn:
            conn.close()

        return record
    except Exception as error:
        raise postsqldb.DatabaseError(error, payload, sql)

def getRecipeItemsByUUID(site, payload, convert=True, conn=None):
    recordset = ()
    self_conn = False
    with open('application/shoppinglists/sql/getRecipeItemsByUUID.sql', 'r') as file:
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
                recordset = [postsqldb.tupleDictionaryFactory(cur.description, row) for row in rows]
            elif rows and not convert:
                recordset = rows
        
        if self_conn:
            conn.close()

        return recordset
    except Exception as error:
        raise postsqldb.DatabaseError(error, payload, sql)

def getItemsWithQOH(site, payload, convert=True, conn=None):
    recordset = []
    count = 0
    self_conn = False

    with open(f"application/shoppinglists/sql/getItemsWithQOH.sql", "r+") as file:
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
    
def getRecipesModal(site, payload, convert=True, conn=None):
    recordsets = []
    count = 0
    self_conn = False

    
    sql = f"SELECT recipes.recipe_uuid, recipes.name FROM {site}_recipes recipes WHERE recipes.name LIKE '%%' || %s || '%%' LIMIT %s OFFSET %s;"
    sql_count = f"SELECT COUNT(*) FROM {site}_recipes recipes WHERE recipes.name LIKE '%%' || %s || '%%';"
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
                recordsets = [postsqldb.tupleDictionaryFactory(cur.description, row) for row in rows]
            if rows and not convert:
                recordsets = rows
            

            cur.execute(sql_count, (payload[0], ))
            count = cur.fetchone()[0]
           
        if self_conn:
            conn.close()

        return recordsets, count

    except Exception as error:
        raise postsqldb.DatabaseError(error, payload, sql)

def getListsModal(site, payload, convert=True, conn=None):
    recordsets = []
    count = 0
    self_conn = False

    
    sql = f"SELECT lists.list_uuid, lists.name FROM {site}_shopping_lists lists WHERE lists.name LIKE '%%' || %s || '%%' LIMIT %s OFFSET %s;"
    sql_count = f"SELECT COUNT(*) FROM {site}_shopping_lists lists WHERE lists.name LIKE '%%' || %s || '%%';"
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
                recordsets = [postsqldb.tupleDictionaryFactory(cur.description, row) for row in rows]
            if rows and not convert:
                recordsets = rows
            

            cur.execute(sql_count, (payload[0], ))
            count = cur.fetchone()[0]
           
        if self_conn:
            conn.close()

        return recordsets, count

    except Exception as error:
        raise postsqldb.DatabaseError(error, payload, sql)

def getItemsModal(site, payload, convert=True, conn=None):
    recordsets = []
    count = 0
    self_conn = False
    with open(f"application/shoppinglists/sql/getItemsForModal.sql", "r+") as file:
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
                recordsets = [postsqldb.tupleDictionaryFactory(cur.description, row) for row in rows]
            if rows and not convert:
                recordsets = rows

            cur.execute(f"SELECT COUNT(*) FROM {site}_items WHERE search_string LIKE '%%' || %s || '%%';", (payload[0], ))
            count = cur.fetchone()[0]
           
        if self_conn:
            conn.close()

        return recordsets, count

    except Exception as error:
        raise postsqldb.DatabaseError(error, payload, sql)

def getItemByUUID(site, payload:dict, convert=True, conn=None):
    """ payload: dict = {'item_uuid'}"""
    record = ()
    self_conn = False
    with open('application/shoppinglists/sql/getItemByUUID.sql', 'r') as file:
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
                record = postsqldb.tupleDictionaryFactory(cur.description, rows)
            elif rows and not convert:
                record = rows
        
        if self_conn:
            conn.close()

        return record
    except Exception as error:
        raise postsqldb.DatabaseError(error, payload, sql)

def getEventRecipes(site, payload, convert=True, conn=None):
    """ payload: dict = {'plan_uuid', 'start_date', 'end_date'}"""
    records = ()
    self_conn = False
    with open('application/shoppinglists/sql/getEventsRecipes.sql', 'r') as file:
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
                records = [postsqldb.tupleDictionaryFactory(cur.description, row) for row in rows]
            elif rows and not convert:
                records = rows
        
        if self_conn:
            conn.close()

        return records
    except Exception as error:
        raise postsqldb.DatabaseError(error, payload, sql)
    
def deleteShoppingListsTuple(site_name, payload, convert=True, conn=None):
    deleted = ()
    self_conn = False
    sql = f"WITH deleted_rows AS (DELETE FROM {site_name}_shopping_lists WHERE {site_name}_shopping_lists.list_uuid IN ({','.join(['%s'] * len(payload))}) RETURNING *) SELECT * FROM deleted_rows;"
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

def deleteShoppingListItemsTuple(site_name, payload, convert=True, conn=None):
    deleted = ()
    self_conn = False
    sql = f"WITH deleted_rows AS (DELETE FROM {site_name}_shopping_list_items WHERE {site_name}_shopping_list_items.list_item_uuid IN ({','.join(['%s'] * len(payload))}) RETURNING *) SELECT * FROM deleted_rows;"
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

def insertShoppingListsTuple(site, payload, convert=True, conn=None):
    shopping_list = ()
    self_conn = False
    with open(f"application/shoppinglists/sql/insertShoppingListsTuple.sql", "r+") as file:
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
                shopping_list = postsqldb.tupleDictionaryFactory(cur.description, rows)
            elif rows and not convert:
                shopping_list = rows
        
        if self_conn:
            conn.commit()
            conn.close()

        return shopping_list
    except Exception as error:
        raise postsqldb.DatabaseError(error, payload, sql)

def insertShoppingListItemsTuple(site, payload, convert=True, conn=None):
    shopping_list_item = ()
    self_conn = False
    with open(f"application/shoppinglists/sql/insertShoppingListItemsTuple.sql", "r+") as file:
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
                shopping_list_item = postsqldb.tupleDictionaryFactory(cur.description, rows)
            elif rows and not convert:
                shopping_list_item = rows
        
        if self_conn:
            conn.commit()
            conn.close()

        return shopping_list_item
        
    except Exception as error:
        raise postsqldb.DatabaseError(error, payload, sql)

def updateShoppingListItemsTuple(site, payload, convert=True, conn=None):
    updated = ()
    self_conn = False
    set_clause, values = postsqldb.updateStringFactory(payload['update'])
    values.append(payload['uuid'])
    sql = f"UPDATE {site}_shopping_list_items SET {set_clause} WHERE list_item_uuid=%s::uuid RETURNING *;"
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