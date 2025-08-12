# 3RD PARTY APPLICATIONS
import psycopg2 
import random
import string

# APPLICATION IMPORTS
from application import postsqldb
import config

def getUUID(n):
    random_string = ''.join(random.choices(string.ascii_letters + string.digits, k=n))
    return random_string

def getModalSKUs(site, payload, convert=True):
    database_config = config.config()
    with psycopg2.connect(**database_config) as conn:
        with conn.cursor() as cur:
            with open("application/recipes/sql/itemsModal.sql") as file:
                 sql = file.read().replace("%%site_name%%", site)
            cur.execute(sql, payload)
            rows = cur.fetchall()

            if rows and convert:
                rows = [postsqldb.tupleDictionaryFactory(cur.description, row) for row in rows]
            
            with open("application/recipes/sql/itemsModalCount.sql") as file:
                sql = file.read().replace("%%site_name%%", site)

            cur.execute(sql)
            count = cur.fetchone()[0]

            if rows and count:
                return rows, count
    return [], 0

def getItemData(site:str, payload:tuple, convert:bool=True):
    database_config = config.config()
    record = ()
    try:
        with psycopg2.connect(**database_config) as conn:
            with conn.cursor() as cur:
                with open("application/recipes/sql/getItemData.sql") as file:
                    sql = file.read().replace("%%site_name%%", site)
                cur.execute(sql, payload)
                rows = cur.fetchone()
                if rows and convert:
                    record = postsqldb.tupleDictionaryFactory(cur.description, rows) 
                if rows and not convert:
                    record = rows
                return record
    except (Exception, psycopg2.DatabaseError) as error:
        raise postsqldb.DatabaseError(error, payload, sql)

def getUnits(convert:bool=True):
    database_config = config.config()
    recordset = ()
    sql = f"SELECT id, fullname FROM units;"
    try:
        with psycopg2.connect(**database_config) as conn:
            with conn.cursor() as cur:
                cur.execute(sql)
                rows = cur.fetchall()
                if rows and convert:
                    recordset = [postsqldb.tupleDictionaryFactory(cur.description, row) for row in rows]
                if rows and not convert:
                    recordset = rows
                return recordset
    except (Exception, psycopg2.DatabaseError) as error:
        raise postsqldb.DatabaseError(error, (), sql)

def getRecipes(site:str, payload:tuple, convert=True):
    recordset = []
    count = 0
    with open("application/recipes/sql/getRecipes.sql", "r+") as file:
        sql = file.read().replace("%%site_name%%", site)
    with open(f"application/recipes/sql/getRecipesCount.sql", "r+") as file:
        sqlcount = file.read().replace("%%site_name%%", site)
    try:
        database_config = config.config()
        with psycopg2.connect(**database_config) as conn:
            with conn.cursor() as cur:
                cur.execute(sql, payload)
                rows = cur.fetchall()
                if rows and convert:
                    recordset = [postsqldb.tupleDictionaryFactory(cur.description, row) for row in rows]
                if rows and not convert:
                    recordset = rows
                cur.execute(sqlcount)
                count = cur.fetchone()[0]
    except (Exception, psycopg2.DatabaseError) as error:
        raise postsqldb.DatabaseError(error, payload, sql)
    return recordset, count

def getRecipe(site, payload:tuple, convert=True, conn=None):
    self_conn = False
    record = ()
    with open(f"application/recipes/sql/getRecipeByID.sql", "r+") as file:
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
            if rows and not convert:
                record = rows

        if self_conn:
            conn.close()

        return record
    except (Exception, psycopg2.DatabaseError) as error:
        raise postsqldb.DatabaseError(error, payload, sql)

def getPicturePath(site:str, payload:tuple):
    database_config = config.config()
    with psycopg2.connect(**database_config) as conn:
        with conn.cursor() as cur:
            cur.execute(f"SELECT picture_path FROM {site}_recipes WHERE id=%s;", payload)
            rows = cur.fetchone()[0]
            return rows
        
def getFuzzyMatch(site: str, payload, convert=True, conn=None):
    matches = []
    self_conn = False
    sql = f"SELECT id, item_name FROM {site}_items WHERE LOWER(item_name) ILIKE '%%' || LOWER(TRIM(%s)) || '%%';"
    try:
        if not conn:
            database_config = config.config()
            conn = psycopg2.connect(**database_config)
            conn.autocommit = True
            self_conn = True
        print(payload)
        with conn.cursor() as cur:
            cur.execute(sql, (payload,))
            rows = cur.fetchall()
            print(rows)
            if rows and convert:
                matches = [postsqldb.tupleDictionaryFactory(cur.description, row) for row in rows]
            elif rows and not convert:
                matches = rows

        if self_conn:
            conn.close()

        return matches
    except Exception as error:
        return error

def selectSiteTuple(payload, convert=True):
    """ payload (tuple): (site_name,) """
    site = ()
    database_config = config.config()
    select_site_sql = f"SELECT * FROM sites WHERE site_name = %s;"
    try:
        with psycopg2.connect(**database_config) as conn:
            with conn.cursor() as cur:
                cur.execute(select_site_sql, payload)
                rows = cur.fetchone()
                if rows and convert:
                    site = postsqldb.tupleDictionaryFactory(cur.description, rows)
                elif rows and not convert:
                    site = rows
    except Exception as error:
        raise postsqldb.DatabaseError(error, payload, select_site_sql)
    return site

def getZone(site:str, payload:tuple, convert:bool=True):
    selected = ()
    database_config = config.config()
    sql = f"SELECT * FROM {site}_zones WHERE id=%s;"
    try:
        with psycopg2.connect(**database_config) as conn:
            with conn.cursor() as cur:
                cur.execute(sql, payload)
                rows = cur.fetchone()
                if rows and convert:
                    selected = postsqldb.tupleDictionaryFactory(cur.description, rows)
                elif rows and not convert:
                    selected = rows
        return selected
    except Exception as error:
        raise postsqldb.DatabaseError(error, payload, sql)
    

def getLocation(site:str, payload:tuple, convert:bool=True):
    selected = ()
    database_config = config.config()
    sql = f"SELECT * FROM {site}_locations WHERE id=%s;"
    try:
        with psycopg2.connect(**database_config) as conn:
            with conn.cursor() as cur:
                cur.execute(sql, payload)
                rows = cur.fetchone()
                if rows and convert:
                    selected = postsqldb.tupleDictionaryFactory(cur.description, rows)
                elif rows and not convert:
                    selected = rows
        return selected
    except Exception as error:
        raise postsqldb.DatabaseError(error, payload, sql)

def selectItemLocationsTuple(site_name, payload, convert=True, conn=None):
    item_locations = ()
    self_conn = False
    select_item_location_sql = f"SELECT * FROM {site_name}_item_locations WHERE part_id = %s AND location_id = %s;"
    try:
        if not conn:
            database_config = config.config()
            conn = psycopg2.connect(**database_config)
            conn.autocommit = True
            self_conn = True

        with conn.cursor() as cur:
            cur.execute(select_item_location_sql, payload)
            rows = cur.fetchone()
            if rows and convert:
                item_locations = postsqldb.tupleDictionaryFactory(cur.description, rows)
            elif rows and not convert:
                item_locations = rows

        if self_conn:
            conn.commit()
            conn.close()

        return item_locations
    except Exception as error:
        return error

def selectCostLayersTuple(site_name, payload, convert=True):
    cost_layers = ()
    database_config = config.config()
    select_cost_layers_sql = f"SELECT cl.* FROM {site_name}_item_locations il JOIN {site_name}_cost_layers cl ON cl.id = ANY(il.cost_layers) where il.id=%s;"
    try:
        with psycopg2.connect(**database_config) as conn:
            with conn.cursor() as cur:
                cur.execute(select_cost_layers_sql, payload)
                rows = cur.fetchall()
                if rows and convert:
                    cost_layers = rows
                    cost_layers = [postsqldb.tupleDictionaryFactory(cur.description, layer) for layer in rows]
                elif rows and not convert:
                    cost_layers = rows
        return cost_layers
    except Exception as error:
        return error

def selectLocationsTuple(site, payload, convert=True, conn=None):
    selected = ()
    self_conn = False
    sql = f"SELECT * FROM {site}_locations WHERE id=%s;"
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
            elif rows and not convert:
                selected = rows

        if self_conn:
            conn.commit()
            conn.close()

        return selected
    except Exception as error:
        raise postsqldb.DatabaseError(error, payload, sql)
    
def selectItemTupleByUUID(site, payload, convert=True, conn=None):
    selected = ()
    self_conn = False
    with open(f"application/recipes/sql/getItemTupleByUUID.sql", "r+") as file:
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
                selected = postsqldb.tupleDictionaryFactory(cur.description, rows)
            elif rows and not convert:
                selected = rows

        if self_conn:
            conn.commit()
            conn.close()

        return selected
    except Exception as error:
        raise postsqldb.DatabaseError(error, payload, sql)
    
def selectConversionTuple(site, payload, convert=True, conn=None):
    """payload=(item_id, uom_id)"""
    selected = ()
    self_conn = False
    sql = f"SELECT conversions.conv_factor FROM {site}_conversions conversions WHERE item_id = %s AND uom_id = %s;"
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
            elif rows and not convert:
                selected = rows

        if self_conn:
            conn.close()

        return selected
    except Exception as error:
        raise postsqldb.DatabaseError(error, payload, sql)


def insertCostLayersTuple(site, payload, convert=True, conn=None):
    cost_layer = ()
    self_conn = False

    with open(f"application/recipes/sql/insertCostLayersTuple.sql", "r+") as file:
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
                cost_layer = postsqldb.tupleDictionaryFactory(cur.description, rows)
            elif rows and not convert:
                cost_layer = rows
        
        if self_conn:
            conn.commit()
            conn.close()

        return cost_layer
    except Exception as error:
        raise postsqldb.DatabaseError(error, payload, sql)

def insertTransactionsTuple(site, payload, convert=True, conn=None):
    # payload (tuple): (timestamp[timestamp], logistics_info_id[int], barcode[str], name[str], 
    transaction = ()
    self_conn = False
    with open(f"application/recipes/sql/insertTransactionsTuple.sql", "r+") as file:
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
                transaction = postsqldb.tupleDictionaryFactory(cur.description, rows)
            elif rows and not convert:
                transaction = rows
        
        if self_conn:
            conn.commit()
            conn.close()

    except Exception as error:
        raise postsqldb.DatabaseError(error, payload, sql)
    return transaction

def insertLogisticsInfoTuple(site, payload, convert=True, conn=None):
    """ payload (tuple): (barcode[str], primary_location[str], auto_issue_location[str], dynamic_locations[jsonb], 
                        location_data[jsonb], quantity_on_hand[float]) """
    logistics_info = ()
    self_conn = False

    with open(f"application/recipes/sql/insertLogisticsInfoTuple.sql", "r+") as file:
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
                logistics_info = postsqldb.tupleDictionaryFactory(cur.description, rows)
            elif rows and not convert:
                logistics_info = rows

        if self_conn:
            conn.commit()
            conn.close()
        
        return logistics_info
    
    except Exception as error:
        raise postsqldb.DatabaseError(error, payload, sql)

def insertItemInfoTuple(site, payload, convert=True, conn=None):
    """ payload (tuple): (barcode[str], linked_items[lst2pgarr], shopping_lists[lst2pgarr], recipes[lst2pgarr], groups[lst2pgarr], 
                            packaging[str], uom[str], cost[float], safety_stock[float], lead_time_days[float], ai_pick[bool]) """
    item_info = ()
    self_conn = False
    with open(f"application/recipes/sql/insertItemInfoTuple.sql", "r+") as file:
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
                item_info = postsqldb.tupleDictionaryFactory(cur.description, rows)
            elif rows and not convert:
                item_info = rows
        if self_conn:
            conn.commit()
            conn.close()

        return item_info
    except Exception as error:
        raise postsqldb.DatabaseError(error, payload, sql)

def insertFoodInfoTuple(site, payload, convert=True, conn=None):
    """ payload (_type_): (ingrediants[lst2pgarr], food_groups[lst2pgarr], nutrients[jsonstr], expires[bool]) """
    food_info = ()
    self_conn = False
    with open(f"application/recipes/sql/insertFoodInfoTuple.sql", "r+") as file:
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
                food_info = postsqldb.tupleDictionaryFactory(cur.description, rows)
            elif rows and not convert:
                food_info = rows
        
        if self_conn:
            conn.commit()
            conn.close()

        return food_info
    except Exception as error:
        raise postsqldb.DatabaseError(error, payload, sql)
    
def insertItemTuple(site, payload, convert=True, conn=None):
    """ payload (tuple): (barcode[str], item_name[str], brand[int], description[str], 
        tags[lst2pgarr], links[jsonb], item_info_id[int], logistics_info_id[int], 
        food_info_id[int], row_type[str], item_type[str], search_string[str]) """
    item = ()
    self_conn = False
    with open(f"application/recipes/sql/insertItemTuple.sql", "r+") as file:
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
                item = postsqldb.tupleDictionaryFactory(cur.description, rows)
            elif rows and not convert:
                item = rows

        if self_conn:
            conn.commit()
            conn.close()
        
        return item
    except Exception as error:
        raise postsqldb.DatabaseError(error, payload, sql)


def insertItemLocationsTuple(site, payload, convert=True, conn=None):
    """ payload (tuple): (part_id[int], location_id[int], quantity_on_hand[float], cost_layers[lst2pgarr]) """
    location = ()
    self_conn = False
    database_config = config.config()
    with open(f"application/recipes/sql/insertItemLocationsTuple.sql", "r+") as file:
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
                location = postsqldb.tupleDictionaryFactory(cur.description, rows)
            elif rows and not convert:
                location = rows
        
        if self_conn:
            conn.commit()
            conn.close()

        return location
    except Exception as error:
        raise postsqldb.DatabaseError(error, payload, sql)

def postAddRecipe(site:str, payload:tuple, convert:bool=True):
    database_config = config.config()
    record = ()
    with open("application/recipes/sql/postRecipe.sql") as file:
        sql = file.read().replace("%%site_name%%", site)
    try:
        with psycopg2.connect(**database_config) as conn:
            with conn.cursor() as cur:
                cur.execute(sql, payload)
                rows = cur.fetchone()
                if rows and convert:
                    record = postsqldb.tupleDictionaryFactory(cur.description, rows)
                elif rows and not convert:
                    record = rows
                return record
    except (Exception, psycopg2.DatabaseError) as error:
        raise postsqldb.DatabaseError(error, payload, sql)
    
def postAddRecipeItem(site:str, payload:tuple, convert:bool=True):
    database_config = config.config()
    record = ()
    with open("application/recipes/sql/postRecipeItem.sql") as file:
        sql = file.read().replace("%%site_name%%", site)
    try:
        with psycopg2.connect(**database_config) as conn:
            with conn.cursor() as cur:
                cur.execute(sql, payload)
                rows = cur.fetchone()
                if rows and convert:
                    record = postsqldb.tupleDictionaryFactory(cur.description, rows)
                elif rows and not convert:
                    record = rows
                return record
    except (Exception, psycopg2.DatabaseError) as error:
        raise postsqldb.DatabaseError(error, payload, sql)

def postUpdateRecipe(site:str, payload:tuple, convert:bool=True):
    database_config = config.config()
    updated = ()
    with psycopg2.connect(**database_config) as conn:
        with conn.cursor() as cur:
            set_clause, values = postsqldb.updateStringFactory(payload['update'])
            with open("application/recipes/sql/postUpdateRecipe.sql") as file:
                 sql = file.read().replace("%%site_name%%", site).replace("%%set_clause%%", set_clause)
            values.append(payload['id'])
            cur.execute(sql, values)
            rows = cur.fetchone()
            if rows and convert:
                updated = postsqldb.tupleDictionaryFactory(cur.description, rows)
            elif rows and not convert:
                updated = rows
    return updated

def postUpdateRecipeItem(site:str, payload:tuple, convert:bool=True):
    database_config = config.config()
    updated = ()
    with psycopg2.connect(**database_config) as conn:
        with conn.cursor() as cur:
            set_clause, values = postsqldb.updateStringFactory(payload['update'])
            with open("application/recipes/sql/postUpdateRecipeItem.sql") as file:
                 sql = file.read().replace("%%site_name%%", site).replace("%%set_clause%%", set_clause)
            values.append(payload['id'])
            cur.execute(sql, values)
            rows = cur.fetchone()
            if rows and convert:
                updated = postsqldb.tupleDictionaryFactory(cur.description, rows)
            elif rows and not convert:
                updated = rows
    return updated

def postDeleteRecipeItem(site:str, payload:tuple, convert:bool=True):
    database_config = config.config()
    deleted = ()
    sql = f"DELETE FROM {site}_recipe_items WHERE id=%s RETURNING *;"
    with psycopg2.connect(**database_config) as conn:
        with conn.cursor() as cur:
            cur.execute(sql, payload)
            rows = cur.fetchone()
            if rows and convert:
                deleted = postsqldb.tupleDictionaryFactory(cur.description, rows)
            elif rows and not convert:
                deleted = rows
    return deleted

def updateCostLayersTuple(site, payload, convert=True, conn=None):
    cost_layer = ()
    self_conn = False

    set_clause, values = postsqldb.updateStringFactory(payload['update'])
    values.append(payload['id'])
    sql = f"UPDATE {site}_cost_layers SET {set_clause} WHERE id=%s RETURNING *;"

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
                cost_layer = postsqldb.tupleDictionaryFactory(cur.description, rows)
            elif rows and not convert:
                cost_layer = rows

        if self_conn:
            conn.commit()
            conn.close()
        
        return cost_layer
    except Exception as error:
        return error

def updateItemLocation(site, payload, convert=True, conn=None):
    item_location = ()
    self_conn = False

    with open(f"application/recipes/sql/updateItemLocation.sql", "r+") as file:
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
                item_location = postsqldb.tupleDictionaryFactory(cur.description, rows)
            elif rows and not convert:
                item_location = rows
        
        if self_conn:
            conn.commit()
            conn.close()
        
        return item_location
    except Exception as error:
        return error

def deleteCostLayersTuple(site, payload, convert=True, conn=None):
    deleted = ()
    self_conn = False
    sql = f"WITH deleted_rows AS (DELETE FROM {site}_cost_layers WHERE id IN ({','.join(['%s'] * len(payload))}) RETURNING *) SELECT * FROM deleted_rows;"
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

def deleteRecipe(site:str, payload:tuple, convert:bool=True):
    database_config = config.config()
    deleted = ()
    sql = f"DELETE FROM {site}_recipes WHERE id=%s RETURNING *;"
    with psycopg2.connect(**database_config) as conn:
        with conn.cursor() as cur:
            cur.execute(sql, payload)
            rows = cur.fetchone()
            if rows and convert:
                deleted = postsqldb.tupleDictionaryFactory(cur.description, rows)
            elif rows and not convert:
                deleted = rows
    return deleted