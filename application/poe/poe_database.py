import psycopg2
import config
from application import postsqldb

def request_receipt_id(conn, site_name):
    """gets the next id for receipts_id, currently returns a 8 digit number

    Args:
        site (str): site to get the next id for

    Returns:
        json: receipt_id, message, error keys
    """
    next_receipt_id = None
    sql = f"SELECT receipt_id FROM {site_name}_receipts ORDER BY id DESC LIMIT 1;"
    try:
        database_config = config.config()
        with psycopg2.connect(**database_config) as conn:
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
    except (Exception, psycopg2.DatabaseError) as error:
        raise postsqldb.DatabaseError(error, payload=(), sql=sql)
    
    return next_receipt_id

def selectItemLocationsTuple(site_name, payload, convert=True):
    """select a single tuple from ItemLocations table for site_name

    Args:
        conn (_T_connector@connect): 
        site_name (str): 
        payload (tuple): [item_id, location_id]
        convert (bool): defaults to False, used to determine return of tuple/dict

    Returns:
        tuple: the row that was returned from the table
    """
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
    """select a single or series of cost layers from the database for site_name

    Args:
        conn (_T_connector@connect): 
        site_name (str): 
        payload (tuple): (item_locations_id, )
        convert (bool): defaults to False, used for determining return as tuple/dict

    Returns:
        list: list of tuples/dict from the cost_layers table for site_name
    """
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

def selectItemLocationsTuple(site_name, payload, convert=True, conn=None):
    """select a single tuple from ItemLocations table for site_name

    Args:
        conn (_T_connector@connect): 
        site_name (str): 
        payload (tuple): [item_id, location_id]
        convert (bool): defaults to False, used to determine return of tuple/dict

    Returns:
        tuple: the row that was returned from the table
    """
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

def selectLinkedItemByBarcode(site, payload, convert=True, conn=None):
    item = ()
    self_conn = False
    sql = f"SELECT * FROM {site}_itemlinks WHERE barcode=%s;"
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
            if rows and not convert:
                item = rows
        
        if self_conn:
            conn.commit()
            conn.close()

        return item
    except (Exception, psycopg2.DatabaseError) as error:
        raise postsqldb.DatabaseError(error, payload, sql)

def selectItemAllByID(site, payload, convert=True, conn=None):
    item = ()
    self_conn = False

    with open(f"application/poe/sql/getItemAllByID.sql", "r+") as file:
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
            conn.commit()
            conn.close()

        return item
    except (Exception, psycopg2.DatabaseError) as error:
        raise postsqldb.DatabaseError(error, payload, getItemAllByID_sql)

def selectItemAllByBarcode(site, payload, convert=True, conn=None):
    item = ()
    self_conn = False
    linked_item = selectLinkedItemByBarcode(site, (payload[0],))

    if len(linked_item) > 1:
        item = selectItemAllByID(site, payload=(linked_item['link'], ), convert=convert)
        item['item_info']['uom_quantity'] = linked_item['conv_factor']
    else:
        with open(f"application/poe/sql/getItemAllByBarcode.sql", "r+") as file:
            getItemAllByBarcode_sql = file.read().replace("%%site_name%%", site)
        try:
            if not conn:
                database_config = config.config()
                conn = psycopg2.connect(**database_config)
                conn.autocommit = True
                self_conn = True

            with conn.cursor() as cur:
                cur.execute(getItemAllByBarcode_sql, payload)
                rows = cur.fetchone()
                if rows and convert:
                    item = postsqldb.tupleDictionaryFactory(cur.description, rows)
                if rows and not convert:
                    item = rows
        
            if self_conn:
                conn.commit()
                conn.close()

        except (Exception, psycopg2.DatabaseError) as error:
            raise postsqldb.DatabaseError(error, payload, getItemAllByBarcode_sql)
    return item
    
def insertCostLayersTuple(site, payload, convert=True, conn=None):
    cost_layer = ()
    self_conn = False

    with open(f"application/poe/sql/insertCostLayersTuple.sql", "r+") as file:
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
    """insert payload into transactions table for site

    Args:
        conn (_T_connector@connect): Postgresql Connector
        site (str):
        payload (tuple): (timestamp[timestamp], logistics_info_id[int], barcode[str], name[str], 
        transaction_type[str], quantity[float], description[str], user_id[int], data[jsonb]) 
        convert (bool, optional): Determines if to return tuple as dictionary. Defaults to False.

    Raises:
        DatabaseError:

    Returns:
        tuple or dict: inserted tuple
    """
    transaction = ()
    self_conn = False
    with open(f"application/poe/sql/insertTransactionsTuple.sql", "r+") as file:
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

def insertReceiptsTuple(site, payload, convert=True, conn=None):
    """insert payload into receipt table of site

    Args:
        conn (_T_connector@connect): Postgresql Connector
        site (str):
        payload (tuple):
        convert (bool, optional): Determines if to return tuple as dictionary. Defaults to False.

    Raises:
        DatabaseError:

    Returns:
        tuple or dict: inserted tuple
    """
    receipt = ()
    self_conn = False
    with open(f"application/poe/sql/insertReceiptsTuple.sql", "r+") as file:
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

def insertReceiptItemsTuple(site, payload, convert=True, conn=None):
    """insert payload into receipt_items table of site

    Args:
        conn (_T_connector@connect): Postgresql Connector
        site (str):
        payload (tuple): (type[str], receipt_id[int], barcode[str], name[str], 
                        qty[float], data[jsonb], status[str])
        convert (bool, optional): Determines if to return tuple as dictionary. Defaults to False.

    Raises:
        DatabaseError:

    Returns:
        tuple or dict: inserted tuple
    """
    receipt_item = ()
    self_conn = False
    
    with open(f"application/poe/sql/insertReceiptItemsTuple.sql", "r+") as file:
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

def updateCostLayersTuple(site, payload, convert=True, conn=None):
    """_summary_

    Args:
        conn (_type_): _description_
        site (_type_): _description_
        payload (_type_): {'id': cost_layer_id, 'update': {column: data...}}

    Returns:
        _type_: _description_
    """
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

    with open(f"application/poe/sql/updateItemLocation.sql", "r+") as file:
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
    """This is a basic funtion to delete a tuple from a table in site with an id. All
    tables in this database has id's associated with them.

    Args:
        conn (_T_connector@connect): Postgresql Connector
        site_name (str):
        payload (tuple): (tuple_id,)
        convert (bool, optional): Determines if to return tuple as dictionary. Defaults to True.

    Raises:
        DatabaseError:

    Returns:
        tuple or dict: deleted tuple
    """
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
