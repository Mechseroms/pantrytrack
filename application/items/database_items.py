from application import postsqldb
import config
import psycopg2
import datetime


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

def postUpdateItem(site:str, payload:dict):
    """ POST and update to an item

    Args:
        site (str): name of the site the item exists in.
        payload (dict): STRICT FORMAT
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
    
def postUpdateItemLink(site: str, payload: dict):
    """ POST update to ItemLink

    Args:
        site (str): _description_
        payload (dict): {id, update, old_conv_factor, user_id}
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

