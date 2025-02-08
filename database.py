class DatabaseError(Exception):
    def __init__(self, message, payload=[], sql=""):
        super().__init__(message)
        self.payload = payload
        self.message = message
        self.sql = sql

    def __str__(self):
        return f"DatabaseError(message='{self.message}', payload={self.payload}, sql='{self.sql}')"

def tupleDictionaryFactory(columns, row):
    columns = [desc[0] for desc in columns]
    return dict(zip(columns, row))

def lst2pgarr(alist):
    return '{' + ','.join(alist) + '}'

# -------------------------
# Insert Database Functions
# -------------------------
def insertLoginsTuple(conn, payload, convert=False):
    """Inserts payload into logins table

    Args:
        conn (_T_connector@connect): Postgresql Connector
        payload (tuple): (username[str], password[str], email[str])
        convert (bool, optional): deteremines if to return tuple as dictionary. Defaults to False.

    Raises:
        DatabaseError: 

    Returns:
        tuple or dict: inserted login
    """
    login = ()
    with open(f"sql/INSERT/insertLoginsTuple.sql", "r+") as file:
        sql = file.read()
    try:
        with conn.cursor() as cur:
            cur.execute(sql, payload)
            rows = cur.fetchone()
            if rows and convert:
                login = tupleDictionaryFactory(cur.description, rows)
            elif rows and not convert:
                login = rows
    except Exception as error:
        raise DatabaseError(error, payload, sql)
    
    return login

def insertGroupsTuple(conn, site, payload, convert=False):
    """insert into groups table for site

    Args:
        conn (_T_connector@connect): Postgresql Connector
        site (stre):
        payload (tuple): (name[str], description[str], included_items[lst2pgarr], group_type[str])
        convert (bool, optional): Determines if to return tuple as a dictionary. Defaults to False.

    Raises:
        DatabaseError:

    Returns:
        tuple or dict: inserted tuple
    """
    group = ()
    with open(f"sql/INSERT/insertGroupsTuple.sql", "r+") as file:
        sql = file.read().replace("%%site_name%%", site)
    try:
        with conn.cursor() as cur:
            cur.execute(sql, payload)
            rows = cur.fetchone()
            if rows and convert:
                group = tupleDictionaryFactory(cur.description, rows)
            elif rows and not convert:
                group = rows
    except Exception as error:
        raise DatabaseError(error, payload, sql)
    return group

def insertLogisticsInfoTuple(conn, site, payload, convert=False):
    """insert payload into logistics_info table for site

    Args:
        conn (_T_connector@connect): Postgresql Connector
        site (str):
        payload (tuple): (barcode[str], primary_location[str], auto_issue_location[str], dynamic_locations[jsonb], 
                        location_data[jsonb], quantity_on_hand[float]) 
        convert (bool, optional): Determines if to return tuple as dictionary. Defaults to False.

    Raises:
        DatabaseError:

    Returns:
        tuple or dict: inserted tuple
    """
    logistics_info = ()
    with open(f"sql/INSERT/insertLogisticsInfoTuple.sql", "r+") as file:
        sql = file.read().replace("%%site_name%%", site)
    try:
        with conn.cursor() as cur:
            cur.execute(sql, payload)
            rows = cur.fetchone()
            if rows and convert:
                logistics_info = tupleDictionaryFactory(cur.description, rows)
            elif rows and not convert:
                logistics_info = rows
    except Exception as error:
        raise DatabaseError(error, payload, sql)

    return logistics_info

def insertItemInfoTuple(conn, site, payload, convert=False):
    """inserts payload into the item_info table of site

    Args:
        conn (_T_connector@connect): Postgresql Connector
        site_name (str): 
        payload (tuple): (barcode[str], linked_items[lst2pgarr], shopping_lists[lst2pgarr], recipes[lst2pgarr], groups[lst2pgarr], 
                            packaging[str], uom[str], cost[float], safety_stock[float], lead_time_days[float], ai_pick[bool]) 
        convert (bool optional): Determines if to return tuple as dictionary. DEFAULTS to False.

    Raises:
        DatabaseError:

    Returns:
        tuple or dict: inserted tuple
    """
    item_info = ()
    with open(f"sql/INSERT/insertItemInfoTuple.sql", "r+") as file:
        sql = file.read().replace("%%site_name%%", site)
    try:
        with conn.cursor() as cur:
            cur.execute(sql, payload)
            rows = cur.fetchone()
            if rows and convert:
                item_info = tupleDictionaryFactory(cur.description, rows)
            elif rows and not convert:
                item_info = rows
    except Exception as error:
        raise DatabaseError(error, payload, sql)
    return item_info

def insertFoodInfoTuple(conn, site, payload, convert=False):
    """insert payload into food_info table for site

    Args:
        conn (_T_connector@connect): Postgresql Connector
        site (str): 
        payload (_type_): (ingrediants[lst2pgarr], food_groups[lst2pgarr], nutrients[jsonstr], expires[bool]) 
        convert (bool, optional): Determines if to return tuple as dictionary. Defaults to False.

    Raises:
        DatabaseError: 

    Returns:
        tuple or dict: inserted tuple
    """
    food_info = ()
    with open(f"sql/INSERT/insertFoodInfoTuple.sql", "r+") as file:
        sql = file.read().replace("%%site_name%%", site)
    try:
        with conn.cursor() as cur:
            cur.execute(sql, payload)
            rows = cur.fetchone()
            if rows and convert:
                food_info = tupleDictionaryFactory(cur.description, rows)
            elif rows and not convert:
                food_info = rows
    except Exception as error:
        raise DatabaseError(error, payload, sql)
    return food_info

def insertBrandsTuple(conn, site, payload, convert=False):
    """insert payload into brands table for site

    Args:
        conn (_T_connector@connect): Postgresql Connector
        site (str):
        payload (tuple): (brand_name[str], )
        convert (bool, optional): Determines if the tuple is returned as a dictionary. Defaults to False.

    Raises:
        DatabaseError:

    Returns:
        tuple or dict: inserted tuple
    """
    brand = ()
    with open(f"sql/INSERT/insertBrandsTuple.sql", "r+") as file:
        sql = file.read().replace("%%site_name%%", site)
    try:
        with conn.cursor() as cur:
            cur.execute(sql, payload)
            rows = cur.fetchone()
            if rows and convert:
                brand = tupleDictionaryFactory(cur.description, rows)
            elif rows and not convert:
                brand = rows
    except Exception as error:
        raise DatabaseError(error, payload, sql)
    return brand

def insertItemTuple(conn, site, payload, convert=False):
    """insert payload into items table for site

    Args:
        conn (_T_connector@connect): Postgresql Connector
        site (str):
        payload (tuple): (barcode[str], item_name[str], brand[int], description[str], 
        tags[lst2pgarr], links[jsonb], item_info_id[int], logistics_info_id[int], 
        food_info_id[int], row_type[str], item_type[str], search_string[str]) 
        convert (bool, optional): Determines if to return tuple as a dictionary. Defaults to False.

    Raises:
        DatabaseError:

    Returns:
        tuple or dict: inserted tuple
    """
    item = ()
    with open(f"sql/INSERT/insertItemTuple.sql", "r+") as file:
        sql = file.read().replace("%%site_name%%", site)
    try:
        with conn.cursor() as cur:
            cur.execute(sql, payload)
            rows = cur.fetchone()
            if rows and convert:
                item = tupleDictionaryFactory(cur.description, rows)
            elif rows and not convert:
                item = rows
    except Exception as error:
        raise DatabaseError(error, payload, sql)
    
    return item

def insertItemLocationsTuple(conn, site, payload, convert=False):
    """insert payload into item_locations table for site

    Args:
        conn (_T_connector@connect): Postgresql Connector
        site (str):
        payload (tuple): (part_id[int], location_id[int], quantity_on_hand[float], cost_layers[lst2pgarr]) 
        convert (bool, optional): Determines if to return tuple as dictionary. Defaults to False.

    Raises:
        DatabaseError:

    Returns:
        tuple or dict: inserted tuple
    """
    location = ()
    with open(f"sql/INSERT/insertItemLocationsTuple.sql", "r+") as file:
        sql = file.read().replace("%%site_name%%", site)
    try:
        with conn.cursor() as cur:
            cur.execute(sql, payload)
            rows = cur.fetchone()
            if rows and convert:
                location = tupleDictionaryFactory(cur.description, rows)
            elif rows and not convert:
                location = rows
    except Exception as error:
        raise DatabaseError(error, payload, sql)
    return location

def insertCostLayersTuple(conn, site, payload, convert=False):
    """insert payload into cost_layers table for site

    Args:
        conn (_T_connector@connect): Postgresql Connector
        site (str): 
        payload (tuple): (aquisition_date[timestamp], quantity[float], cost[float], currency_type[str], expires[timestamp/None], vendor[int]) 
        convert (bool, optional): Determines if tuple is returned as a dictionary. Defaults to False.

    Raises:
        DatabaseError:

    Returns:
        tuple or dict: inserted tuple
    """
    cost_layer = ()
    with open(f"sql/INSERT/insertCostLayersTuple.sql", "r+") as file:
        sql = file.read().replace("%%site_name%%", site)
    try:
        with conn.cursor() as cur:
            cur.execute(sql, payload)
            rows = cur.fetchone()
            if rows and convert:
                cost_layer = tupleDictionaryFactory(cur.description, rows)
            elif rows and not convert:
                cost_layer = rows
    except Exception as error:
        raise DatabaseError(error, payload, sql)
    return cost_layer

def insertTransactionsTuple(conn, site, payload, convert=False):
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
    with open(f"sql/INSERT/insertTransactionsTuple.sql", "r+") as file:
        sql = file.read().replace("%%site_name%%", site)
    try:
        with conn.cursor() as cur:
            cur.execute(sql, payload)
            rows = cur.fetchone()
            if rows and convert:
                transaction = tupleDictionaryFactory(cur.description, rows)
            elif rows and not convert:
                transaction = rows
    except Exception as error:
        raise DatabaseError(error, payload, sql)
    return transaction

# -------------------------
# Update Database Functions
# -------------------------
def updateItemLocation(conn, site, payload):
    item_location = ()
    with open(f"sql/updateItemLocation.sql", "r+") as file:
        sql = file.read().replace("%%site_name%%", site)
    try:
        with conn.cursor() as cur:
            cur.execute(sql, payload)
            rows = cur.fetchone()
            if rows:
                item_location = rows
    except Exception as error:
        return error
    return item_location

def updateCostLayersTuple(conn, site, payload):
    """_summary_

    Args:
        conn (_type_): _description_
        site (_type_): _description_
        payload (_type_): _description_

    Returns:
        _type_: _description_
    """
    cost_layer = ()
    with open(f"sql/updateCostLayersTuple.sql", "r+") as file:
        sql = file.read().replace("%%site_name%%", site)
    try:
        with conn.cursor() as cur:
            cur.execute(sql, payload)
            rows = cur.fetchone()
            if rows:
                cost_layer = rows
    except Exception as error:
        return error
    return cost_layer

# -------------------------
# Delete Database Functions
# -------------------------
def deleteCostLayersTuple(conn, site_name, payload):
    """deletes tuple from cost_layers table for site_name

    Args:
        conn (_T_connector@connect): Postgresql Connector
        site (str):
        payload (tuple): (cost_layer_id, )

    Raises:
        DatabaseError: returns all database errors and encompasses payload and sql info.
        
    Returns:
        tuple: deleted row returned as a tuple
    """
    cost_layer = ()
    sql = f"WITH deleted_row AS (DELETE FROM {site_name}_cost_layers WHERE id=%s RETURNING *) SELECT * FROM deleted_row;"
    try:
        with conn.cursor() as cur:
            cur.execute(sql, payload)
            rows = cur.fetchone()
            if rows:
                cost_layer = rows
    except Exception as error:
        raise DatabaseError(error, payload, sql)
    return cost_layer

# -------------------------
# Select Database Functions
# -------------------------
def selectItemLocationsTuple(conn, site_name, payload, convert=False):
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
    select_item_location_sql = f"SELECT * FROM {site_name}_item_locations WHERE part_id = %s AND location_id = %s;"
    try:
        with conn.cursor() as cur:
            cur.execute(select_item_location_sql, payload)
            rows = cur.fetchone()
            if rows and convert:
                item_locations = tupleDictionaryFactory(cur.description, rows)
            elif rows and not convert:
                item_locations = rows
    except Exception as error:
        return error
    
    return item_locations

def selectCostLayersTuple(conn, site_name, payload, convert=False):
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
    select_cost_layers_sql = f"SELECT cl.* FROM {site_name}_item_locations il JOIN {site_name}_cost_layers cl ON cl.id = ANY(il.cost_layers) where il.id=%s;"
    try:
        with conn.cursor() as cur:
            cur.execute(select_cost_layers_sql, payload)
            rows = cur.fetchall()
            if rows and convert:
                cost_layers = rows
                cost_layers = [tupleDictionaryFactory(cur.description, layer) for layer in rows]
            elif rows and not convert:
                cost_layers = rows
    except Exception as error:
        return error
    return cost_layers

# -------------------------
# Custom Database Functions
# -------------------------
def getItemLocation(conn, site_name, payload):
    """This functions returns the bundled ItemLocation of item_id and location_id, with the cost_layers pulled from the database as tuples.

    Args:
        conn (_T_connector@connect): 
        site_name (str): 
        payload (tuple): [item_id, location_id]

    Returns:
        list: list of the itemLocation with cost_layers selected

    """
    item_location = list(selectItemLocationsTuple(conn, site_name, payload))
    print(item_location)
    item_location[4] = selectCostLayersTuple(conn, site_name, (item_location[0], ))

    return item_location