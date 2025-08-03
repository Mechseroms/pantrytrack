# 3RD PARTY IMPORTS
import psycopg2
import datetime

# APPLICATION IMPORTS
from application import postsqldb
import config


def getTransactions(site:str, payload: tuple, convert:bool=True):
    """ payload (tuple): (logistics_id, limit, offset) """
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

def getItemAllByBarcode(site:str, payload: tuple, convert:bool=True):
    database_config = config.config()
    with open('application/items/sql/getItemAllByBarcode.sql', 'r+') as file:
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

def getModalSKUs(site:str, payload:tuple, convert:bool=True):
    database_config = config.config()
    with open("application/items/sql/itemsModal.sql") as file:
        sql = file.read().replace("%%site_name%%", site)
    with open("application/items/sql/itemsModalCount.sql") as file:
        sql_count = file.read().replace("%%site_name%%", site)
    recordset = []
    count = 0
    try:
        with psycopg2.connect(**database_config) as conn:
            with conn.cursor() as cur:
                print(payload)
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
        raise postsqldb.DatabaseError(error, payload, sql)
    
def getPrefixes(site:str, payload:tuple, convert:bool=True):
    database_config = config.config()
    recordset = []
    count = 0
    with open(f"application/items/sql/getSkuPrefixes.sql", "r+") as file:
        sql = file.read().replace("%%site_name%%", site)
    try:
        with psycopg2.connect(**database_config) as conn:
            with conn.cursor() as cur:
                cur.execute(sql, payload)
                rows = cur.fetchall()
                if rows and convert:
                    recordset = [postsqldb.tupleDictionaryFactory(cur.description, row) for row in rows]
                if rows and not convert:
                    recordset = rows

                cur.execute(f"SELECT COUNT(*) FROM {site}_sku_prefix;")
                count = cur.fetchone()[0]
                return recordset, count
    except (Exception, psycopg2.DatabaseError) as error:
        raise postsqldb.DatabaseError(error, payload, sql)

def getItemLink(site: str, payload:tuple, convert:bool=True):
    database_config = config.config()
    item_link = ()
    sql = f"SELECT * FROM {site}_itemlinks WHERE id=%s;"
    try:
        with psycopg2.connect(**database_config) as conn:
            with conn.cursor() as cur:
                cur.execute(sql, payload)
                rows = cur.fetchone()
                if rows and convert:
                    item_link = postsqldb.tupleDictionaryFactory(cur.description, rows)
                elif rows and not convert:
                    item_link = rows
                return item_link 
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

def getItemLocations(site, payload, convert=True, conn=None):
    locations = []
    count = 0
    self_conn = False
    with open(f"application/items/sql/getItemLocations.sql", "r+") as file:
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
                locations = [postsqldb.tupleDictionaryFactory(cur.description, row) for row in rows]
            if rows and not convert:
                locations = rows

            cur.execute(f"SELECT COUNT(*) FROM {site}_item_locations WHERE part_id=%s;", (payload[0],))
            count = cur.fetchone()[0]
        
        if self_conn:
            conn.close()

        return locations, count

    except (Exception, psycopg2.DatabaseError) as error:
        raise postsqldb.DatabaseError(error, payload, sql)

def getItemInfoTuple(site:str, payload:tuple, convert=True):
    """ payload (_type_): (item_info_id,) """
    selected = ()
    database_config = config.config()
    sql = f"SELECT * FROM {site}_item_info WHERE id=%s;"
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

def selectItemLocationsTuple(site_name, payload, convert=True):
    """ payload (tuple): [item_id, location_id] """
    item_locations = ()
    database_config = config.config()
    select_item_location_sql = f"SELECT * FROM {site_name}_item_locations WHERE part_id = %s AND location_id = %s;"
    try:
        with psycopg2.connect(**database_config) as conn:
            with conn.cursor() as cur:
                cur.execute(select_item_location_sql, payload)
                rows = cur.fetchone()
                if rows and convert:
                    item_locations = postsqldb.tupleDictionaryFactory(cur.description, rows)
                elif rows and not convert:
                    item_locations = rows
        return item_locations
    except Exception as error:
        return error

def selectCostLayersTuple(site_name, payload, convert=True):
    """ payload (tuple): (item_locations_id, ) """
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

def paginateZonesBySku(site: str, payload: tuple, convert=True):
    database_config = config.config()
    zones, count = (), 0
    with open(f"application/items/sql/paginateZonesBySku.sql", "r+") as file:
        sql = file.read().replace("%%site_name%%", site)
    with open(f"application/items/sql/paginateZonesBySkuCount.sql", "r+") as file:
        sql_count = file.read().replace("%%site_name%%", site)
    try:
        with psycopg2.connect(**database_config) as conn:
            with conn.cursor() as cur:
                cur.execute(sql, payload)
                rows = cur.fetchall()
                if rows and convert:
                    zones = [postsqldb.tupleDictionaryFactory(cur.description, row) for row in rows]
                elif rows and not convert:
                    zones = rows
                cur.execute(sql_count, payload)
                count = cur.fetchone()[0]
                return zones, count  
    except Exception as error:
        raise postsqldb.DatabaseError(error, payload, sql)

def paginateLocationsWithZone(site:str, payload:tuple, convert:bool=True):
    recordset, count = (), 0
    database_config = config.config()
    with open(f"application/items/sql/getLocationsWithZone.sql", "r+") as file:
        sql = file.read().replace("%%site_name%%", site)
    try:
        with psycopg2.connect(**database_config) as conn:            
            with conn.cursor() as cur:
                cur.execute(sql, payload)
                rows = cur.fetchall()
                if rows and convert:
                    recordset = [postsqldb.tupleDictionaryFactory(cur.description, row) for row in rows]
                elif rows and not convert:
                    recordset = rows
                cur.execute(f"SELECT COUNT(*) FROM {site}_locations;")
                count = cur.fetchone()[0]
                return recordset, count
    except Exception as error:
        raise postsqldb.DatabaseError(error, (), sql)

def paginateLocationsBySkuZone(site: str, payload: tuple, convert=True):
    database_config = config.config()
    locations, count = (), 0
    with open(f"application/items/sql/paginateLocationsBySkuZone.sql", "r+") as file:
        sql = file.read().replace("%%site_name%%", site)
    with open(f"application/items/sql/paginateLocationsBySkuZoneCount.sql", "r+") as file:
        sql_count = file.read().replace("%%site_name%%", site)
    try:
        with psycopg2.connect(**database_config) as conn:
            with conn.cursor() as cur:
                cur.execute(sql, payload)
                rows = cur.fetchall()
                if rows and convert:
                    locations = [postsqldb.tupleDictionaryFactory(cur.description, row) for row in rows]
                elif rows and not convert:
                    locations = rows
                cur.execute(sql_count, payload)
                count = cur.fetchone()[0]
                return locations, count
    except Exception as error:
        raise postsqldb.DatabaseError(error, payload, sql)

def paginateBrands(site:str, payload:tuple, convert:bool=True):
    database_config = config.config()
    recordset, count = [], 0
    sql = f"SELECT brand.id, brand.name FROM {site}_brands brand LIMIT %s OFFSET %s;"
    try:
        with psycopg2.connect(**database_config) as conn:
            with conn.cursor() as cur:
                cur.execute(sql, payload)
                rows = cur.fetchall()
                if rows and convert:
                    recordset = [postsqldb.tupleDictionaryFactory(cur.description, row) for row in rows]
                if rows and not convert:
                    recordset = rows
                cur.execute(f"SELECT COUNT(*) FROM {site}_brands")
                count = cur.fetchone()[0]
                return recordset, count
    except Exception as error:
        raise postsqldb.DatabaseError(error, payload, sql)

def insertCostLayersTuple(site, payload, convert=True, conn=None):
    cost_layer = ()
    self_conn = False

    with open(f"application/items/sql/insertCostLayersTuple.sql", "r+") as file:
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
    
def insertItemLocationsTuple(site, payload, convert=True, conn=None):
    """ payload (tuple): (part_id[int], location_id[int], quantity_on_hand[float], cost_layers[lst2pgarr]) """
    location = ()
    self_conn = False
    database_config = config.config()
    with open(f"application/items/sql/insertItemLocationsTuple.sql", "r+") as file:
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

def insertLogisticsInfoTuple(site, payload, convert=True, conn=None):
    """ payload (tuple): (barcode[str], primary_location[str], auto_issue_location[str], dynamic_locations[jsonb], 
                        location_data[jsonb], quantity_on_hand[float]) """
    logistics_info = ()
    self_conn = False

    with open(f"application/items/sql/insertLogisticsInfoTuple.sql", "r+") as file:
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
    with open(f"application/items/sql/insertItemInfoTuple.sql", "r+") as file:
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
    with open(f"application/items/sql/insertFoodInfoTuple.sql", "r+") as file:
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
    with open(f"application/items/sql/insertItemTuple.sql", "r+") as file:
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

def insertSKUPrefixtuple(site:str, payload:tuple, convert=True, conn=None):
    """ payload (tuple): (name[str],) """
    prefix = ()
    self_conn = False
    with open(f"application/items/sql/insertSKUPrefixTuple.sql", "r+") as file:
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
                prefix = postsqldb.tupleDictionaryFactory(cur.description, rows)
            elif rows and not convert:
                prefix = rows

        if self_conn:
            conn.commit()
            conn.close()

        return prefix
    except Exception as error:
        raise postsqldb.DatabaseError(error, payload, sql)

def insertConversionTuple(site: str, payload: list, convert=True, conn=None):
    """ payload (tuple): (item_id, uom_id, conversion_factor) """
    record = ()
    self_conn = False
    with open(f"sql/INSERT/insertConversionsTuple.sql", "r+") as file:
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
            conn.commit()
            conn.close()

        return record
    
    except Exception as error:
        raise postsqldb.DatabaseError(error, payload, sql)    

def postDeleteCostLayer(site_name, payload, convert=True, conn=None):
    """ payload (tuple): (table_to_delete_from, tuple_id) """
    deleted = ()
    self_conn = False
    sql = f"WITH deleted_rows AS (DELETE FROM {site_name}_cost_layers WHERE id IN ({','.join(['%s'] * len(payload))}) RETURNING *) SELECT * FROM deleted_rows;"
    
    try:
        if not conn:
            database_config = config.config()
            conn = psycopg2.connect(**database_config)
            conn.autocommit = False
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

def deleteConversionTuple(site_name: str, payload: tuple, convert=True, conn=None):
    """ payload (tuple): (tuple_id,...) """
    deleted = ()
    self_conn = False
    sql = f"WITH deleted_rows AS (DELETE FROM {site_name}_conversions WHERE id IN ({','.join(['%s'] * len(payload))}) RETURNING *) SELECT * FROM deleted_rows;"
    try:
        if not conn:
            database_config = config.config()
            conn = psycopg2.connect(**database_config)
            conn.autocommit = False
            self_conn = True
            
        with conn.cursor() as cur:
            cur.execute(sql, payload)
            rows = cur.fetchone()
            if rows and convert:
                deleted = postsqldb.tupleDictionaryFactory(cur.description, rows)
            elif rows and not convert:
                deleted = rows
        
        if self_conn:
            conn.commit()
            conn.close()

        return deleted
    
    except Exception as error:
        raise postsqldb.DatabaseError(error, payload, sql)

def updateConversionTuple(site:str, payload: dict, convert=True, conn=None):
    """ payload (dict): {'id': row_id, 'update': {... column_to_update: value_to_update_to...}} """
    updated = ()
    self_conn = False
    set_clause, values = postsqldb.updateStringFactory(payload['update'])
    values.append(payload['id'])
    sql = f"UPDATE {site}_conversions SET {set_clause} WHERE id=%s RETURNING *;"
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

def updateItemInfoTuple(site:str, payload: dict, convert=True, conn=None):
    """ payload (dict): {'id': row_id, 'update': {... column_to_update: value_to_update_to...}} """
    updated = ()
    self_conn = False
    set_clause, values = postsqldb.updateStringFactory(payload['update'])
    values.append(payload['id'])
    sql = f"UPDATE {site}_item_info SET {set_clause} WHERE id=%s RETURNING *;"
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

def postUpdateItemLocation(site: str, payload: tuple, conn=None):

    item_location = ()
    self_conn = False
    with open(f"sql/updateItemLocation.sql", "r+") as file:
        sql = file.read().replace("%%site_name%%", site)
    try:
        if not conn:
            database_config = config.config()
            conn = psycopg2.connect(**database_config)
            conn.autocommit = False
            self_conn = True
        
        with conn.cursor() as cur:
            cur.execute(sql, payload)
            rows = cur.fetchone()
            if rows:
                item_location = rows

        if self_conn:
            conn.commit()
            conn.close()

        return item_location
    except Exception as error:
        return error

# TODO: This should be in the item's process module
def postUpdateItem(site:str, payload:dict):
    """ payload (dict): STRICT FORMAT
        {id: item_id, data: SEE BELOW, user_id: updater}

        data is complex structure
        top level keys should be a combo of: ['item', 'item_info', 'logistics_info', 'food_info']
        with in each of these top levels there are key value pairs in this format
        {'column_name': 'new_value'}
    """
    def postUpdateData(conn, table, payload, convert=True):
        updated = ()

        set_clause, values = postsqldb.updateStringFactory(payload['update'])
        values.append(payload['id'])
        sql = f"UPDATE {table} SET {set_clause} WHERE id=%s RETURNING *;"
        try:
            with conn.cursor() as cur:
                cur.execute(sql, values)
                rows = cur.fetchone()
                if rows and convert:
                    updated = postsqldb.tupleDictionaryFactory(cur.description, rows)
                elif rows and not convert:
                    updated = rows
        except Exception as error:
            raise postsqldb.DatabaseError(error, payload, sql)
        return updated
    
    def postAddTransaction(conn, site, payload, convert=False):
        transaction = ()
        with open(f"application/items/sql/insertTransactionsTuple.sql", "r+") as file:
            sql = file.read().replace("%%site_name%%", site)
        try:
            with conn.cursor() as cur:
                cur.execute(sql, payload)
                rows = cur.fetchone()
                if rows and convert:
                    transaction = postsqldb.tupleDictionaryFactory(cur.description, rows)
                elif rows and not convert:
                    transaction = rows
        except Exception as error:
            raise postsqldb.DatabaseError(error, payload, sql)
        return transaction

    transaction_data = {}
    database_config = config.config()
    data = payload['update']
    for key in data.keys():
        for key_2 in data[key].keys():
            transaction_data[f"{key_2}_new"] = data[key][key_2]
    try:
        with psycopg2.connect(**database_config) as conn:
            item = getItemAllByID(site, (payload['id'], ))
            if 'item_info' in data.keys() and data['item_info'] != {}:
                for key in data['item_info'].keys():
                    transaction_data[f"{key}_old"] = item['item_info'][key]
                postUpdateData(conn, f"{site}_item_info", {'id': item['item_info_id'], 'update': data['item_info']})
            
            if 'food_info' in data.keys() and data['food_info'] != {}:
                for key in data['food_info'].keys():
                    transaction_data[f"{key}_old"] = item['food_info'][key]
                postUpdateData(conn, f"{site}_food_info", {'id': item['food_info_id'], 'update': data['food_info']})
            
            if 'logistics_info' in data.keys() and data['logistics_info'] != {}:
                for key in data['logistics_info'].keys():
                    transaction_data[f"{key}_old"] = item['logistics_info'][key]
                postUpdateData(conn, f"{site}_logistics_info", {'id': item['logistics_info_id'], 'update': data['logistics_info']})
            
            if 'item' in data.keys() and data['item'] != {}:
                for key in data['item'].keys():
                    if key == "brand":
                        transaction_data[f"{key}_old"] = item['brand']['id']
                    else:
                        transaction_data[f"{key}_old"] = item[key]
                postUpdateData(conn, f"{site}_items", {'id': payload['id'], 'update': data['item']})

            trans = postsqldb.TransactionPayload(
                timestamp=datetime.datetime.now(),
                logistics_info_id=item['logistics_info_id'],
                barcode=item['barcode'],
                name=item['item_name'],
                transaction_type="UPDATE",
                quantity=0.0,
                description="Item was updated!",
                user_id=payload['user_id'],
                data=transaction_data
            )
            postAddTransaction(conn, site, trans.payload())
    except Exception as error:
        raise postsqldb.DatabaseError(error, payload, "MULTICALL!")

# TODO: This should be in the item's process module
def postUpdateItemLink(site: str, payload: dict):
    """ payload (dict): {id, update, old_conv_factor, user_id} """
    def postUpdateData(conn, table, payload, convert=True):
        updated = ()
        set_clause, values = postsqldb.updateStringFactory(payload['update'])
        values.append(payload['id'])
        sql = f"UPDATE {table} SET {set_clause} WHERE id=%s RETURNING *;"
        try:
            with conn.cursor() as cur:
                cur.execute(sql, values)
                rows = cur.fetchone()
                if rows and convert:
                    updated = postsqldb.tupleDictionaryFactory(cur.description, rows)
                elif rows and not convert:
                    updated = rows
        except Exception as error:
            raise postsqldb.DatabaseError(error, payload, sql)
        return updated
    
    def postAddTransaction(conn, site, payload, convert=False):
        transaction = ()
        with open(f"application/items/sql/insertTransactionsTuple.sql", "r+") as file:
            sql = file.read().replace("%%site_name%%", site)
        try:
            with conn.cursor() as cur:
                cur.execute(sql, payload)
                rows = cur.fetchone()
                if rows and convert:
                    transaction = postsqldb.tupleDictionaryFactory(cur.description, rows)
                elif rows and not convert:
                    transaction = rows
        except Exception as error:
            raise postsqldb.DatabaseError(error, payload, sql)
        return transaction

    database_config = config.config()
    transaction_time = datetime.datetime.now()
    barcode = payload['barcode']
    with psycopg2.connect(**database_config) as conn:
        linkedItem = getItemAllByBarcode(site, (barcode, ))

        transaction = postsqldb.TransactionPayload(
            timestamp=transaction_time,
            logistics_info_id=linkedItem['logistics_info_id'],
            barcode=barcode,
            name=linkedItem['item_name'],
            transaction_type='UPDATE',
            quantity=0.0,
            description='Link updated!',
            user_id=payload['user_id'],
            data={'new_conv_factor': payload['update']['conv_factor'], 'old_conv_factor': payload['old_conv_factor']}
        )

        postUpdateData(conn, f"{site}_itemlinks", {'id': payload['id'], 'update': {'conv_factor': payload['update']['conv_factor']}})
        postAddTransaction(conn, site, transaction.payload())

def postUpdateCostLayer(site, payload, convert=True, conn=None):
    """ payload (dict): {'id': row_id, 'update': {... column_to_update: value_to_update_to...}} """
    updated = ()
    self_conn = False
        
    set_clause, values = postsqldb.updateStringFactory(payload['update'])
    values.append(payload['id'])
    sql = f"UPDATE {site}_cost_layers SET {set_clause} WHERE id=%s RETURNING *;"
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

def postAddTransaction(site, payload, convert=False, conn=None):
    transaction = ()
    self_conn = False

    with open(f"application/items/sql/insertTransactionsTuple.sql", "r+") as file:
        sql = file.read().replace("%%site_name%%", site)
    try:
        if not conn:
            database_config = config.config()
            conn = psycopg2.connect(**database_config)
            conn.autocommit = False
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
        
        return transaction
    except Exception as error:
        raise postsqldb.DatabaseError(error, payload, sql)

def postInsertItemLink(site, payload, convert=True, conn=None):
    """ payload (tuple): (barcode[str], link[int], data[jsonb], conv_factor[float]) """
    link = ()
    self_conn = False

    with open(f"application/items/sql/insertItemLinksTuple.sql", "r+") as file:
        sql = file.read().replace("%%site_name%%", site)
    try:
        if not conn:
            database_config = config.config()
            conn = psycopg2.connect(**database_config)
            conn.autocommit = False
            self_conn = True

        with conn.cursor() as cur:
            cur.execute(sql, payload)
            rows = cur.fetchone()
            if rows and convert:
                link = postsqldb.tupleDictionaryFactory(cur.description, rows)
            elif rows and not convert:
                link = rows
        
        if self_conn:
            conn.commit()
            conn.close()

        return link, conn
    except Exception as error:
        raise postsqldb.DatabaseError(error, payload, sql)

def postUpdateItemByID(site, payload, convert=True, conn=None):
    """ payload (dict): {'id': row_id, 'update': {... column_to_update: value_to_update_to...}} """
    updated = ()
    self_conn = False
    set_clause, values = postsqldb.updateStringFactory(payload['update'])
    values.append(payload['id'])
    sql = f"UPDATE {site}_items SET {set_clause} WHERE id=%s RETURNING *;"
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

        return updated, conn
    except Exception as error:
        raise postsqldb.DatabaseError(error, payload, sql)
