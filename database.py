from datetime import datetime
import psycopg2, json
import psycopg2.extras
from dataclasses import dataclass, field
import random
import string

class DatabaseError(Exception):
    def __init__(self, message, payload=[], sql=""):
        super().__init__(message)
        self.payload = payload
        self.message = str(message).replace("\n", "")
        self.sql = sql.replace("\n", "")
        self.log_error()

    def log_error(self):
        with open("database.log", "a+") as file:
            file.write("\n")
            file.write(f"{datetime.now()} --- ERROR --- DatabaseError(message='{self.message}',\n")
            file.write(f"{" "*41}payload={self.payload},\n")
            file.write(f"{" "*41}sql='{self.sql}')")

    def __str__(self):
        return f"DatabaseError(message='{self.message}', payload={self.payload}, sql='{self.sql}')"

def tupleDictionaryFactory(columns, row):
    columns = [desc[0] for desc in columns]
    return dict(zip(columns, row))

def lst2pgarr(alist):
    return '{' + ','.join(alist) + '}'

def updateStringFactory(updated_values: dict):
    set_clause = ', '.join([f"{key} = %s" for key in updated_values.keys()])
    values = []
    for value in updated_values.values():
        if isinstance(value, dict):
            value = json.dumps(value)
        values.append(value)

    return set_clause, values

def getUUID(n):
    random_string = ''.join(random.choices(string.ascii_letters + string.digits, k=n))
    return random_string

# -------------------------
# Insert Database Functions
# -------------------------
def insertShoppingListsTuple(conn, site, payload, convert=False):
    """insert payload into shopping_lists table of site

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
    shopping_list = ()
    with open(f"sql/INSERT/insertShoppingListsTuple.sql", "r+") as file:
        sql = file.read().replace("%%site_name%%", site)
    try:
        with conn.cursor() as cur:
            cur.execute(sql, payload)
            rows = cur.fetchone()
            if rows and convert:
                shopping_list = tupleDictionaryFactory(cur.description, rows)
            elif rows and not convert:
                shopping_list = rows
    except Exception as error:
        raise DatabaseError(error, payload, sql)
    return shopping_list

def insertShoppingListItemsTuple(conn, site, payload, convert=False):
    """insert payload into shopping_list_items table of site

    Args:
        conn (_T_connector@connect): Postgresql Connector
        site (str):
        payload (tuple): (uuid[str], sl_id[int], item_type[str], item_name[str], uom[str],
          qty[float], item_id[int], links[jsonb]) 
        convert (bool, optional): Determines if to return tuple as dictionary. Defaults to False.

    Raises:
        DatabaseError:

    Returns:
        tuple or dict: inserted tuple
    """
    shopping_list_item = ()
    with open(f"sql/INSERT/insertShoppingListItemsTuple.sql", "r+") as file:
        sql = file.read().replace("%%site_name%%", site)
    try:
        with conn.cursor() as cur:
            cur.execute(sql, payload)
            rows = cur.fetchone()
            if rows and convert:
                shopping_list_item = tupleDictionaryFactory(cur.description, rows)
            elif rows and not convert:
                shopping_list_item = rows
    except Exception as error:
        raise DatabaseError(error, payload, sql)
    return shopping_list_item

def insertReceiptsTuple(conn, site, payload, convert=False):
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
    with open(f"sql/INSERT/insertReceiptsTuple.sql", "r+") as file:
        sql = file.read().replace("%%site_name%%", site)
    try:
        with conn.cursor() as cur:
            cur.execute(sql, payload)
            rows = cur.fetchone()
            if rows and convert:
                receipt = tupleDictionaryFactory(cur.description, rows)
            elif rows and not convert:
                receipt = rows
    except Exception as error:
        raise DatabaseError(error, payload, sql)
    return receipt

def insertReceiptItemsTuple(conn, site, payload, convert=False):
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
    with open(f"sql/INSERT/insertReceiptItemsTuple.sql", "r+") as file:
        sql = file.read().replace("%%site_name%%", site)
    try:
        with conn.cursor() as cur:
            cur.execute(sql, payload)
            rows = cur.fetchone()
            if rows and convert:
                receipt_item = tupleDictionaryFactory(cur.description, rows)
            elif rows and not convert:
                receipt_item = rows
    except Exception as error:
        raise DatabaseError(error, payload, sql)
    return receipt_item

def insertItemLinksTuple(conn, site, payload, convert=False):
    """insert payload into itemlinks table of site

    Args:
        conn (_T_connector@connect): Postgresql Connector
        site (str):
        payload (tuple): (barcode[str], link[int], data[jsonb], conv_factor[float]) 
        convert (bool, optional): Determines if to return tuple as dictionary. Defaults to False.

    Raises:
        DatabaseError:

    Returns:
        tuple or dict: inserted tuple
    """
    link = ()
    with open(f"sql/INSERT/insertItemLinksTuple.sql", "r+") as file:
        sql = file.read().replace("%%site_name%%", site)
    try:
        with conn.cursor() as cur:
            cur.execute(sql, payload)
            rows = cur.fetchone()
            if rows and convert:
                link = tupleDictionaryFactory(cur.description, rows)
            elif rows and not convert:
                link = rows
    except Exception as error:
        raise DatabaseError(error, payload, sql)
    return link

def insertVendorsTuple(conn, site, payload, convert=False):
    """insert payload into vendors table of site

    Args:
        conn (_T_connector@connect): Postgresql Connector
        site (str): (vendor_name[str], vendor_address[str], creation_date[timestampe], 
        created_by[int], phone_number[str])
        payload (tuple): (vendor_name[str], vendor_address[str], creation_date[timestamp], created_by[int], phone_number[str])
        convert (bool, optional): Determines if to return tuple as dictionary. Defaults to False.

    Raises:
        DatabaseError:

    Returns:
        tuple or dict: inserted tuple
    """
    vendor = ()
    with open(f"sql/INSERT/insertVendorsTuple.sql", "r+") as file:
        sql = file.read().replace("%%site_name%%", site)
    try:
        with conn.cursor() as cur:
            cur.execute(sql, payload)
            rows = cur.fetchone()
            if rows and convert:
                vendor = tupleDictionaryFactory(cur.description, rows)
            elif rows and not convert:
                vendor = rows
    except Exception as error:
        raise DatabaseError(error, payload, sql)
    return vendor

def insertZonesTuple(conn, site, payload, convert=False):
    """insert payload into zones table of site

    Args:
        conn (_T_connector@connect): Postgresql Connector
        site (str):
        payload (tuple): (name[str],)
        convert (bool, optional): Determines if to return tuple as dictionary. Defaults to False.

    Raises:
        DatabaseError:

    Returns:
        tuple or dict: inserted tuple
    """
    zone = ()
    with open(f"sql/INSERT/insertZonesTuple.sql", "r+") as file:
        sql = file.read().replace("%%site_name%%", site)
    try:
        with conn.cursor() as cur:
            cur.execute(sql, payload)
            rows = cur.fetchone()
            if rows and convert:
                zone = tupleDictionaryFactory(cur.description, rows)
            elif rows and not convert:
                zone = rows
    except Exception as error:
        raise DatabaseError(error, payload, sql)
    return zone

def insertLocationsTuple(conn, site, payload, convert=False):
    """insert payload into locations table of site

    Args:
        conn (_T_connector@connect): Postgresql Connector
        site (str):
        payload (tuple): (uuid[str], name[str], zone_id[int], items[jsonb])
        convert (bool, optional): Determines if to return tuple as dictionary. Defaults to False.

    Raises:
        DatabaseError:

    Returns:
        tuple or dict: inserted tuple
    """
    location = ()
    with open(f"sql/INSERT/insertLocationsTuple.sql", "r+") as file:
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

def insertRecipeItemsTuple(conn, site, payload, convert=False):
    """insert into recipe_items table for site

    Args:
        conn (_T_connector@connect): Postgresql Connector
        site (stre):
        payload (tuple): (uuid[str], rp_id[int], item_type[str], item_name[str], uom[str], qty[float], item_id[int], links[jsonb]) 
        convert (bool, optional): Determines if to return tuple as a dictionary. Defaults to False.

    Raises:
        DatabaseError:

    Returns:
        tuple or dict: inserted tuple
    """
    recipe_item = ()
    with open(f"sql/INSERT/insertRecipeItemsTuple.sql", "r+") as file:
        sql = file.read().replace("%%site_name%%", site)
    try:
        with conn.cursor() as cur:
            cur.execute(sql, payload)
            rows = cur.fetchone()
            if rows and convert:
                recipe_item = tupleDictionaryFactory(cur.description, rows)
            elif rows and not convert:
                recipe_item = rows
    except Exception as error:
        raise DatabaseError(error, payload, sql)
    return recipe_item

def insertRecipesTuple(conn, site, payload, convert=False):
    """insert into recipes table for site

    Args:
        conn (_T_connector@connect): Postgresql Connector
        site (stre):
        payload (tuple): (name[str], author[int], description[str], creation_date[timestamp], instructions[list], picture_path[str]) 
        convert (bool, optional): Determines if to return tuple as a dictionary. Defaults to False.

    Raises:
        DatabaseError:

    Returns:
        tuple or dict: inserted tuple
    """
    recipe = ()
    with open(f"sql/INSERT/insertRecipesTuple.sql", "r+") as file:
        sql = file.read().replace("%%site_name%%", site)
    try:
        with conn.cursor() as cur:
            cur.execute(sql, payload)
            rows = cur.fetchone()
            if rows and convert:
                recipe = tupleDictionaryFactory(cur.description, rows)
            elif rows and not convert:
                recipe = rows
    except Exception as error:
        raise DatabaseError(error, payload, sql)
    return recipe

def insertGroupItemsTuple(conn, site, payload, convert=False):
    """insert into group_items table for site

    Args:
        conn (_T_connector@connect): Postgresql Connector
        site (stre):
        payload (tuple): (uuid[str], gr_id[int], item_type[str], item_name[str], uom[str], qty[float], item_id[int], links[jsonb]) 
        convert (bool, optional): Determines if to return tuple as a dictionary. Defaults to False.

    Raises:
        DatabaseError:

    Returns:
        tuple or dict: inserted tuple
    """
    group_item = ()
    with open(f"sql/INSERT/insertGroupItemsTuple.sql", "r+") as file:
        sql = file.read().replace("%%site_name%%", site)
    try:
        with conn.cursor() as cur:
            cur.execute(sql, payload)
            rows = cur.fetchone()
            if rows and convert:
                group_item = tupleDictionaryFactory(cur.description, rows)
            elif rows and not convert:
                group_item = rows
    except Exception as error:
        raise DatabaseError(error, payload, sql)
    return group_item

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

def insertSitesTuple(conn, payload, convert=False):
    """inserts payload into sites table

    Args:
        conn (_T_connector@connect): Postgresql Connector
        payload (tuple): (site_name[str], site_description[str], creation_date[timestamp], site_owner_id[int],
          flags[dict], default_zone[str], default_auto_issue_location[str], default_primary_location[str])
        convert (bool, optional): Determines if to return tuple as dictionary. Defaults to False.

    Raises:
        DatabaseError:

    Returns:
        tuple or dict: inserted tuple
    """
    site_tuple = ()
    with open(f"sql/INSERT/insertSitesTuple.sql", "r+") as file:
        sql = file.read()
    try:
        with conn.cursor() as cur:
            cur.execute(sql, payload)
            rows = cur.fetchone()
            if rows and convert:
                site_tuple = tupleDictionaryFactory(cur.description, rows)
            elif rows and not convert:
                site_tuple = rows
    except Exception as error:
        raise DatabaseError(error, payload, sql)
    return site_tuple

def insertRolesTuple(conn, payload, convert=False):
    """inserts payload into roles table

    Args:
        conn (_T_connector@connect): Postgresql Connector
        payload (tuple): (role_name[str], role_description[str], site_id[int], flags[jsonb])
        convert (bool, optional): Determines if to return tuple as dictionary. Defaults to False.

    Raises:
        DatabaseError:

    Returns:
        tuple or dict: inserted tuple
    """
    role_tuple = ()
    with open(f"sql/INSERT/insertRolesTuple.sql", "r+") as file:
        sql = file.read()
    try:
        with conn.cursor() as cur:
            cur.execute(sql, payload)
            rows = cur.fetchone()
            if rows and convert:
                role_tuple = tupleDictionaryFactory(cur.description, rows)
            elif rows and not convert:
                role_tuple = rows
    except Exception as error:
        raise DatabaseError(error, payload, sql)
    return role_tuple

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
def __deleteTupleById(conn, site_name, payload, table, convert=False):
    """This is a basic funtion to delete a tuple from a table in site with an id. All
    tables in this database has id's associated with them.

    Args:
        conn (_T_connector@connect): Postgresql Connector
        site_name (str):
        payload (tuple): (table_to_delete_from, tuple_id)
        convert (bool, optional): Determines if to return tuple as dictionary. Defaults to False.

    Raises:
        DatabaseError:

    Returns:
        tuple or dict: deleted tuple
    """
    deleted = ()
    sql = f"WITH deleted_rows AS (DELETE FROM {table} WHERE id IN ({','.join(['%s'] * len(payload))}) RETURNING *) SELECT * FROM deleted_rows;"
    try:
        with conn.cursor() as cur:
            cur.execute(sql, payload)
            rows = cur.fetchall()
            if rows and convert:
                deleted = [tupleDictionaryFactory(cur.description, r) for r in rows]
            elif rows and not convert:
                deleted = rows
    except Exception as error:
        raise DatabaseError(error, payload, sql)
    return deleted

def deleteItemsTuple(conn, site, payload, convert=False):
    """deletes tuple/s with ids from items table for site

    Args:
        conn (_T_connector@connect): Postgresql Connector
        site (str):
        payload (tuple): (id1, id2, id3, ...)
        convert (bool, optional): Determines if to return tuple as dictionary. Defaults to False.

    Returns:
        tuple or dict: deleted tuple 
    """
    table = f"{site}_items"
    return __deleteTupleById(conn, site, payload, table, convert)

def deleteCostLayersTuple(conn, site, payload, convert=False):
    """deletes tuple/s with ids from cost_layers table for site

    Args:
        conn (_T_connector@connect): Postgresql Connector
        site (str):
        payload (tuple): (id1, id2, id3, ...)
        convert (bool, optional): Determines if to return tuple as dictionary. Defaults to False.

    Returns:
        tuple or dict: deleted tuple 
    """
    table = f"{site}_cost_layers"
    return __deleteTupleById(conn, site, payload, table, convert)

def deleteLoginsTuple(conn, site, payload, convert=False):
    """deletes tuple/s with ids from cost_layers table for site

    Args:
        conn (_T_connector@connect): Postgresql Connector
        site (str):
        payload (tuple): (id1, id2, id3, ...)
        convert (bool, optional): Determines if to return tuple as dictionary. Defaults to False.

    Returns:
        tuple or dict: deleted tuple 
    """
    table = "logins"
    return __deleteTupleById(conn, site, payload, table, convert)

def deleteZonesTuple(conn, site, payload, convert=False):
    """deletes tuple/s with ids from zones table for site

    Args:
        conn (_T_connector@connect): Postgresql Connector
        site (str):
        payload (tuple): (id1, id2, id3, ...)
        convert (bool, optional): Determines if to return tuple as dictionary. Defaults to False.

    Returns:
        tuple or dict: deleted tuple 
    """
    table = f"{site}_zones"
    return __deleteTupleById(conn, site, payload, table, convert)

def deleteRolesTuple(conn, site, payload, convert=False):
    """deletes tuple/s with ids from roles table

    Args:
        conn (_T_connector@connect): Postgresql Connector
        site (str):
        payload (tuple): (id1, id2, id3, ...)
        convert (bool, optional): Determines if to return tuple as dictionary. Defaults to False.

    Returns:
        tuple or dict: deleted tuple 
    """
    table = f"roles"
    return __deleteTupleById(conn, site, payload, table, convert)

def deleteBrandsTuple(conn, site, payload, convert=False):
    """deletes tuple/s with ids from brands table for site

    Args:
        conn (_T_connector@connect): Postgresql Connector
        site (str):
        payload (tuple): (id1, id2, id3, ...)
        convert (bool, optional): Determines if to return tuple as dictionary. Defaults to False.

    Returns:
        tuple or dict: deleted tuple 
    """
    table = f"{site}_brands"
    return __deleteTupleById(conn, site, payload, table, convert)

def deleteFoodInfoTuple(conn, site, payload, convert=False):
    """deletes tuple/s with ids from food_info table for site

    Args:
        conn (_T_connector@connect): Postgresql Connector
        site (str):
        payload (tuple): (id1, id2, id3, ...)
        convert (bool, optional): Determines if to return tuple as dictionary. Defaults to False.

    Returns:
        tuple or dict: deleted tuple 
    """
    table = f"{site}_food_info"
    return __deleteTupleById(conn, site, payload, table, convert)

def deleteGroupsTuple(conn, site, payload, convert=False):
    """deletes tuple/s with ids from groups table for site

    Args:
        conn (_T_connector@connect): Postgresql Connector
        site (str):
        payload (tuple): (id1, id2, id3, ...)
        convert (bool, optional): Determines if to return tuple as dictionary. Defaults to False.

    Returns:
        tuple or dict: deleted tuple 
    """
    table = f"{site}_groups"
    return __deleteTupleById(conn, site, payload, table, convert)

def deleteGroupItemsTuple(conn, site, payload, convert=False):
    """deletes tuple/s with ids from group_items table for site

    Args:
        conn (_T_connector@connect): Postgresql Connector
        site (str):
        payload (tuple): (id1, id2, id3, ...)
        convert (bool, optional): Determines if to return tuple as dictionary. Defaults to False.

    Returns:
        tuple or dict: deleted tuple 
    """
    table = f"{site}_group_items"
    return __deleteTupleById(conn, site, payload, table, convert)

def deleteItemInfoTuple(conn, site, payload, convert=False):
    """deletes tuple/s with ids from item_info table for site

    Args:
        conn (_T_connector@connect): Postgresql Connector
        site (str):
        payload (tuple): (id1, id2, id3, ...)
        convert (bool, optional): Determines if to return tuple as dictionary. Defaults to False.

    Returns:
        tuple or dict: deleted tuple 
    """
    table = f"{site}_item_info"
    return __deleteTupleById(conn, site, payload, table, convert)

def deleteItemLocationsTuple(conn, site, payload, convert=False):
    """deletes tuple/s with ids from item_locations table for site

    Args:
        conn (_T_connector@connect): Postgresql Connector
        site (str):
        payload (tuple): (id1, id2, id3, ...)
        convert (bool, optional): Determines if to return tuple as dictionary. Defaults to False.

    Returns:
        tuple or dict: deleted tuple 
    """
    table = f"{site}_item_locations"
    return __deleteTupleById(conn, site, payload, table, convert)

def deleteItemLinksTuple(conn, site, payload, convert=False):
    """deletes tuple/s with ids from itemlinks table for site

    Args:
        conn (_T_connector@connect): Postgresql Connector
        site (str):
        payload (tuple): (id1, id2, id3, ...)
        convert (bool, optional): Determines if to return tuple as dictionary. Defaults to False.

    Returns:
        tuple or dict: deleted tuple 
    """
    table = f"{site}_itemlinks"
    return __deleteTupleById(conn, site, payload, table, convert)

def deleteLocationsTuple(conn, site, payload, convert=False):
    """deletes tuple/s with ids from locations table for site

    Args:
        conn (_T_connector@connect): Postgresql Connector
        site (str):
        payload (tuple): (id1, id2, id3, ...)
        convert (bool, optional): Determines if to return tuple as dictionary. Defaults to False.

    Returns:
        tuple or dict: deleted tuple 
    """
    table = f"{site}_locations"
    return __deleteTupleById(conn, site, payload, table, convert)

def deleteLogisticsInfoTuple(conn, site, payload, convert=False):
    """deletes tuple/s with ids from logistics_info table for site

    Args:
        conn (_T_connector@connect): Postgresql Connector
        site (str):
        payload (tuple): (id1, id2, id3, ...)
        convert (bool, optional): Determines if to return tuple as dictionary. Defaults to False.

    Returns:
        tuple or dict: deleted tuple 
    """
    table = f"{site}_logistics_info"
    return __deleteTupleById(conn, site, payload, table, convert)

def deleteRecipesTuple(conn, site, payload, convert=False):
    """deletes tuple/s with ids from recipes table for site

    Args:
        conn (_T_connector@connect): Postgresql Connector
        site (str):
        payload (tuple): (id1, id2, id3, ...)
        convert (bool, optional): Determines if to return tuple as dictionary. Defaults to False.

    Returns:
        tuple or dict: deleted tuple 
    """
    table = f"{site}_recipes"
    return __deleteTupleById(conn, site, payload, table, convert)

def deleteRecipeItemsTuple(conn, site, payload, convert=False):
    """deletes tuple/s with ids from recipe_items table for site

    Args:
        conn (_T_connector@connect): Postgresql Connector
        site (str):
        payload (tuple): (id1, id2, id3, ...)
        convert (bool, optional): Determines if to return tuple as dictionary. Defaults to False.

    Returns:
        tuple or dict: deleted tuple 
    """
    table = f"{site}_recipe_items"
    return __deleteTupleById(conn, site, payload, table, convert)

def deleteShoppingListsTuple(conn, site, payload, convert=False):
    """deletes tuple/s with ids from shopping_lists table for site

    Args:
        conn (_T_connector@connect): Postgresql Connector
        site (str):
        payload (tuple): (id1, id2, id3, ...)
        convert (bool, optional): Determines if to return tuple as dictionary. Defaults to False.

    Returns:
        tuple or dict: deleted tuple 
    """
    table = f"{site}_shopping_lists"
    return __deleteTupleById(conn, site, payload, table, convert)

def deleteShoppingListItemsTuple(conn, site, payload, convert=False):
    """deletes tuple/s with ids from shopping_list_items table for site

    Args:
        conn (_T_connector@connect): Postgresql Connector
        site (str):
        payload (tuple): (id1, id2, id3, ...)
        convert (bool, optional): Determines if to return tuple as dictionary. Defaults to False.

    Returns:
        tuple or dict: deleted tuple 
    """
    table = f"{site}_shopping_list_items"
    return __deleteTupleById(conn, site, payload, table, convert)

def deleteTransactionsTuple(conn, site, payload, convert=False):
    """deletes tuple/s with ids from transactions table for site

    Args:
        conn (_T_connector@connect): Postgresql Connector
        site (str):
        payload (tuple): (id1, id2, id3, ...)
        convert (bool, optional): Determines if to return tuple as dictionary. Defaults to False.

    Returns:
        tuple or dict: deleted tuple 
    """
    table = f"{site}_transactions"
    return __deleteTupleById(conn, site, payload, table, convert)

def deleteVendorsTuple(conn, site, payload, convert=False):
    """deletes tuple/s with ids from vendors table for site

    Args:
        conn (_T_connector@connect): Postgresql Connector
        site (str):
        payload (tuple): (id1, id2, id3, ...)
        convert (bool, optional): Determines if to return tuple as dictionary. Defaults to False.

    Returns:
        tuple or dict: deleted tuple 
    """
    table = f"{site}_vendors"
    return __deleteTupleById(conn, site, payload, table, convert)

def deleteReceiptsTuple(conn, site, payload, convert=False):
    """deletes tuple/s with ids from receipts table for site

    Args:
        conn (_T_connector@connect): Postgresql Connector
        site (str):
        payload (tuple): (id1, id2, id3, ...)
        convert (bool, optional): Determines if to return tuple as dictionary. Defaults to False.

    Returns:
        tuple or dict: deleted tuple 
    """
    table = f"{site}_receipts"
    return __deleteTupleById(conn, site, payload, table, convert)

def deleteReceiptItemsTuple(conn, site, payload, convert=False):
    """deletes tuple/s with ids from receipt_items table for site

    Args:
        conn (_T_connector@connect): Postgresql Connector
        site (str):
        payload (tuple): (id1, id2, id3, ...)
        convert (bool, optional): Determines if to return tuple as dictionary. Defaults to False.

    Returns:
        tuple or dict: deleted tuple 
    """
    table = f"{site}_receipt_items"
    return __deleteTupleById(conn, site, payload, table, convert)

def deleteSitesTuple(conn, site, payload, convert=False):
    """deletes tuple/s with ids from sites table

    Args:
        conn (_T_connector@connect): Postgresql Connector
        site (str):
        payload (tuple): (id1, id2, id3, ...)
        convert (bool, optional): Determines if to return tuple as dictionary. Defaults to False.

    Returns:
        tuple or dict: deleted tuple 
    """
    table = f"sites"
    return __deleteTupleById(conn, site, payload, table, convert)

# -------------------------
# Update Database Functions
# -------------------------
def __updateTuple(conn, site, table, payload, convert=False):
    """_summary_

    Args:
        conn (_T_connector@connect): Postgresql Connector
        site (str):
        table (str):
        payload (dict): {'id': row_id, 'update': {... column_to_update: value_to_update_to...}}
        convert (bool, optional): determines if to return tuple as dictionary. Defaults to False.

    Raises:
        DatabaseError:

    Returns:
        tuple or dict: updated tuple
    """
    updated = ()

    set_clause, values = updateStringFactory(payload['update'])
    values.append(payload['id'])
    sql = f"UPDATE {table} SET {set_clause} WHERE id=%s RETURNING *;"
    try:
        with conn.cursor() as cur:
            cur.execute(sql, values)
            rows = cur.fetchone()
            if rows and convert:
                updated = tupleDictionaryFactory(cur.description, rows)
            elif rows and not convert:
                updated = rows
    except Exception as error:
        raise DatabaseError(error, payload, sql)
    return updated

# -------------------------
# Select Database Functions
# -------------------------
def __selectTuple(conn, site, table, payload, convert=False):
    selected = ()
    sql = f"SELECT * FROM {table} WHERE id=%s;"
    try:
        with conn.cursor() as cur:
            cur.execute(sql, payload)
            rows = cur.fetchone()
            if rows and convert:
                selected = tupleDictionaryFactory(cur.description, rows)
            elif rows and not convert:
                selected = rows
    except Exception as error:
        raise DatabaseError(error, payload, sql)
    return selected

def __selectTuples(conn, site, table, convert=False):
    selected = ()
    sql = f"SELECT * FROM {table};"
    try:
        with conn.cursor() as cur:
            cur.execute(sql)
            rows = cur.fetchall()
            if rows and convert:
                selected = [tupleDictionaryFactory(cur.description, row) for row in rows]
            elif rows and not convert:
                selected = rows
    except Exception as error:
        raise DatabaseError(error, (), sql)
    return selected

def _paginateTableTuples(conn, site, table, payload, convert=False):
    recordset = []
    sql = f"SELECT * FROM {table} LIMIT {payload[0]} OFFSET {payload[1]};"
    try:
        if convert:
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                cur.execute(sql, payload)
                recordset = cur.fetchall()
                recordset = [dict(record) for record in recordset]
                cur.execute(f"SELECT COUNT(*) FROM {table}")
                count = cur.fetchone()
        else:
            with conn.cursor() as cur:
                cur.execute(sql, payload)
                recordset = cur.fetchall()
                cur.execute(f"SELECT COUNT(*) FROM {table}")
                count = cur.fetchone()
    except Exception as error:
        raise DatabaseError(error, payload, sql)

    return recordset, count

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

def selectSiteTuple(conn, payload, convert=False):
    """Select a single Site from sites using site_name

    Args:
        conn (_T_connector@connect): Postgresql Connector
        payload (tuple): (site_name,)
        convert (bool, optional): determines if to return tuple as dictionary. Defaults to False.

    Raises:
        DatabaseError:

    Returns:
        tuple or dict: selected tuples
    """
    site = ()
    select_site_sql = f"SELECT * FROM sites WHERE site_name = %s;"
    try:
        with conn.cursor() as cur:
            cur.execute(select_site_sql, payload)
            rows = cur.fetchone()
            if rows and convert:
                site = tupleDictionaryFactory(cur.description, rows)
            elif rows and not convert:
                site = rows
    except Exception as error:
        raise DatabaseError(error, payload, select_site_sql)
    return site

def selectSitesTuple(conn, payload, convert=False):
    site = ()
    select_sites_sql = f"SELECT * FROM sites WHERE id IN ({','.join(['%s'] * len(payload))}) RETURNING *;"
    try:
        with conn.cursor() as cur:
            cur.execute(select_sites_sql, payload)
            rows = cur.fetchall()
            if rows and convert:
                site = [tupleDictionaryFactory(cur.description, site) for site in rows]
            elif rows and not convert:
                site = rows
    except Exception as error:
        return error
    return site

def selectRolesTuple(conn, payload, convert=False):
    """Select all Roles from roles table using site_id

    Args:
        conn (_T_connector@connect): Postgresql Connector
        payload (tuple): (site_id,)
        convert (bool, optional): determines if to return tuple as dictionary. Defaults to False.

    Raises:
        DatabaseError: 

    Returns:
        tuple or dict: selected tuples
    """
    roles = ()
    select_roles_sql = f"SELECT * FROM roles WHERE site_id = %s;"
    try:
        with conn.cursor() as cur:
            cur.execute(select_roles_sql, payload)
            rows = cur.fetchall()
            if rows and convert:
                roles = [tupleDictionaryFactory(cur.description, role) for role in rows]
            elif rows and not convert:
                roles = rows
    except Exception as error:
        raise DatabaseError(error, payload, select_roles_sql)
    return roles



# -------------------------
# Create Database Functions
# -------------------------
def __createTable(conn, site, table):
    """creates table in site database

    Args:
        conn (_T_connector@connect): Postgresql Connector
        site (str): 
        table (str): 

    Raises:
        DatabaseError:
    """
    with open(f"sql/CREATE/{table}.sql", 'r') as file:
        sql = file.read().replace("%%site_name%%", site)
    try:
        with conn.cursor() as cur:
            cur.execute(sql)
    except Exception as error: 
        raise DatabaseError(error, sql, table)

# -----------------------
# Drop Database Functions
# -----------------------
def __dropTable(conn, site, table):
    """drops table from site database

    Args:
        conn (_T_connector@connect): Postgresql Connector
        site (str):
        table (str): 

    Raises:
        DatabaseError: 
    """
    with open(f"sql/DROP/{table}.sql", 'r') as file:
        sql = file.read().replace("%%site_name%%", site)
    try:
        with conn.cursor() as cur:
            cur.execute(sql)
    except Exception as error: 
        raise DatabaseError(error, sql, table)

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
    item_location[4] = selectCostLayersTuple(conn, site_name, (item_location[0], ))

    return item_location

def getUser(conn, payload, convert=False):
    """_summary_

    Args:
        conn (_type_): _description_
        payload (tuple): (username, password)
        convert (bool, optional): _description_. Defaults to False.

    Raises:
        DatabaseError: _description_

    Returns:
        _type_: _description_
    """
    user = ()
    try:
        with conn.cursor() as cur:
            sql = f"SELECT * FROM logins WHERE username=%s;"
            cur.execute(sql, (payload[0],))
            rows = cur.fetchone()
            if rows and rows[2] == payload[1] and convert:
                user = tupleDictionaryFactory(cur.description, rows)
            elif rows and rows[2] == payload[1] and not convert:
                user = rows
    except Exception as error:
        raise DatabaseError(error, payload, sql)
    return user

def updateRemoveLoginSite(conn, payload, convert=False):
    sql = f"UPDATE logins SET sites = array_remove(sites, %s) WHERE id = %s RETURNING *;"
    login = ()
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

def updateRemoveLoginRole(conn, payload, convert=False):
    sql = f"UPDATE logins SET site_roles = array_remove(site_roles, %s) WHERE id = %s RETURNING *;"
    login = ()
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

def updateRemoveLoginSitesRoles(conn, payload, convert=False):
    """update logins table with payload

    Args:
        conn (_T_connector@connect): Postgresql Connector
        payload (tuple): (site_id, role_id, login_id)
        convert (bool, optional): determins if to return tuple as dictionary. Defaults to False.

    Raises:
        DatabaseError: 

    Returns:
        tuple or dict: updated tuple
    """
    sql = f"UPDATE logins SET sites = array_remove(sites, %s), site_roles = array_remove(site_roles, %s) WHERE id = %s RETURNING *;"
    login = ()
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

def updateUsersSites(conn, site_id):
    try:
        select_sql = f"SELECT logins.id FROM logins WHERE sites @> ARRAY[%s];"
        with conn.cursor() as cur:
            cur.execute(select_sql, (site_id, ))
            user = tuple([row[0] for row in cur.fetchall()])

        update_sql = f"UPDATE logins SET sites = array_remove(sites, %s) WHERE id = %s;"
        with conn.cursor() as cur:
            for user_id in user:
                cur.execute(update_sql, (site_id, user_id))
    except Exception as error:
        raise error

def updateUsersRoles(conn, role_id):
    try:
        select_sql = f"SELECT logins.id FROM logins WHERE site_roles @> ARRAY[%s];"
        with conn.cursor() as cur:
            cur.execute(select_sql, (role_id, ))
            users = tuple([row[0] for row in cur.fetchall()])

        update_sql = f"UPDATE logins SET site_roles = array_remove(site_roles, %s) WHERE id = %s;"
        with conn.cursor() as cur:
            for user_id in users:
                cur.execute(update_sql, (role_id, user_id))
    except Exception as error:
        raise error

def updateAddLoginSitesRoles(conn, payload, convert=False):
    """update logins table with payload

    Args:
        conn (_T_connector@connect): Postgresql Connector
        payload (tuple): (site_id, role_id, login_id)
        convert (bool, optional): determins if to return tuple as dictionary. Defaults to False.

    Raises:
        DatabaseError: 

    Returns:
        tuple or dict: updated tuple
    """
    sql = f"UPDATE logins SET sites = sites || %s, site_roles = site_roles || %s WHERE id=%s RETURNING *;"
    login = ()
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

def getItemsWithQOH(conn, site, payload, convert=True):

    # used in items/index.html (getItems)
    recordset = []
    count = 0
    with open(f"sql/SELECT/getItemsWithQOH.sql", "r+") as file:
        sql = file.read().replace("%%site_name%%", site)
    try:
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
    except Exception as error:
        raise DatabaseError(error, payload, sql)
    return recordset, count

def getItemsForModal(conn, site, payload, convert=True):
    """ This database query returns all the items in the database specific for use with modals
    in the system. It returns all items that ARE NOT of the type link which is a linked item that
    we do not want anyone being able to interact with outside of editing info.

    Args:
        conn (_T_connector@connect): PostgreSQL connector
        site (str):
        payload (tuple): (search_string, limit, offset)
        convert (bool, optional): Determines if the items are returned as tuples or dictionaries. Defaults to True.

    Raises:
        DatabaseError:

    Returns:
        tuple: 
    """
    recordset = []
    count = 0
    with open(f"sql/SELECT/getItemsForModals.sql", "r+") as file:
        sql = file.read().replace("%%site_name%%", site)
    try:
        if convert:
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                cur.execute(sql, payload)
                recordset = cur.fetchall()
                recordset = [dict(record) for record in recordset]
                cur.execute(f"SELECT COUNT(*) FROM {site}_items WHERE search_string LIKE '%%' || %s || '%%' AND {site}_items.row_type <> 'link';", (payload[0], ))
                count = cur.fetchone()
        else:   
            with conn.cursor() as cur:
                cur.execute(sql, payload)
                recordset = cur.fetchall()
                cur.execute(f"SELECT COUNT(*) FROM {site}_items WHERE search_string LIKE '%%' || %s || '%%' AND {site}_items.row_type <> 'link';", (payload[0], ))
                count = cur.fetchone()
    except Exception as error:
        raise DatabaseError(error, payload, sql)
    return recordset, count

def getItemAllByID(conn, site, payload, convert=False):
    item = ()
    with open(f"sql/SELECT/getItemAllByID.sql", "r+") as file:
        getItemAllByID_sql = file.read().replace("%%site_name%%", site)
    try:
        with conn.cursor() as cur:
            cur.execute(getItemAllByID_sql, payload)
            rows = cur.fetchone()
            if rows and convert:
                item = tupleDictionaryFactory(cur.description, rows)
            if rows and not convert:
                item = rows
    except (Exception, psycopg2.DatabaseError) as error:
        raise DatabaseError(error, payload, getItemAllByID_sql)
    return item

def getLinkedItemByBarcode(conn, site, payload, convert=True):
    item = ()
    sql = f"SELECT * FROM {site}_itemlinks WHERE barcode=%s;"
    if convert:
        item = {}
    try:
        with conn.cursor() as cur:
            cur.execute(sql, payload)
            rows = cur.fetchone()
            if rows and convert:
                item = tupleDictionaryFactory(cur.description, rows)
            if rows and not convert:
                item = rows
    except (Exception, psycopg2.DatabaseError) as error:
        raise DatabaseError(error, payload, sql)
    return item

def getItemAllByBarcode(conn, site, payload, convert=True):

    item = ()
    if convert:
        item = {}
    linked_item = getLinkedItemByBarcode(conn, site, (payload[0],))

    if len(linked_item) > 1:
        item = getItemAllByID(conn, site, payload=(linked_item['link'], ), convert=convert)
        item['item_info']['uom_quantity'] = linked_item['conv_factor']
    else:
        with open(f"sql/SELECT/getItemAllByBarcode.sql", "r+") as file:
            getItemAllByBarcode_sql = file.read().replace("%%site_name%%", site)
        try:
            with conn.cursor() as cur:
                cur.execute(getItemAllByBarcode_sql, payload)
                rows = cur.fetchone()
                if rows and convert:
                    item = tupleDictionaryFactory(cur.description, rows)
                if rows and not convert:
                    item = rows
        except (Exception, psycopg2.DatabaseError) as error:
            raise DatabaseError(error, payload, getItemAllByBarcode_sql)
    return item

def getZonesWithCount(conn, site, payload, convert=False):
    """_summary_

    Args:
        conn (_type_): _description_
        site (_type_): _description_
        payload (_type_): (limit, offset)
        convert (bool, optional): _description_. Defaults to False.

    Raises:
        DatabaseError: _description_

    Returns:
        _type_: _description_
    """
    zones = ()
    count = 0
    with open(f"sql/SELECT/getZonesWithCount.sql", "r+") as file:
        getZonesWithCount_sql = file.read().replace("%%site_name%%", site)
    with open(f"sql/SELECT/countZones.sql", "r+") as file:
        countZones_sql = file.read().replace("%%site_name%%", site)
    try:
        with conn.cursor() as cur:
            cur.execute(getZonesWithCount_sql, payload)
            rows = cur.fetchall()
            if rows and convert:
                zones = [tupleDictionaryFactory(cur.description, row) for row in rows]
            if rows and not convert:
                zones = rows
            if rows:
                cur.execute(countZones_sql)
                count = cur.fetchone()    
    except (Exception, psycopg2.DatabaseError) as error:
        raise DatabaseError(error, payload, getZonesWithCount_sql)
    return zones, count

def queryTuple(conn, sql, payload, convert=False):
    queryset = ()
    try:
        with conn.cursor() as cur:
            cur.execute(sql, payload)
            rows = cur.fetchone()
            if rows and convert:
                queryset = tupleDictionaryFactory(cur.description, rows)
            if rows and not convert:
                queryset = rows
    except (Exception, psycopg2.DatabaseError) as error:
        raise DatabaseError(error, payload, sql)
    return queryset

def queryTuples(conn, sql, payload, convert=False):
    querysets = []
    try:
        with conn.cursor() as cur:
            cur.execute(sql, payload)
            rows = cur.fetchall()
            if rows and convert:
                querysets = [tupleDictionaryFactory(cur.description, row) for row in rows]
            if rows and not convert:
                querysets = rows
    except (Exception, psycopg2.DatabaseError) as error:
        raise DatabaseError(error, payload, sql)
    return querysets

def getItemLocations(conn, site, payload, convert=False):
    locations = []
    count = 0
    with open(f"sql/SELECT/getItemLocations.sql", "r+") as file:
        sql = file.read().replace("%%site_name%%", site)
    try:
        with conn.cursor() as cur:
            cur.execute(sql, payload)
            rows = cur.fetchall()
            if rows and convert:
                locations = [tupleDictionaryFactory(cur.description, row) for row in rows]
            if rows and not convert:
                locations = rows

            cur.execute(f"SELECT COUNT(*) FROM {site}_item_locations WHERE part_id=%s;", (payload[0],))
            count = cur.fetchone()[0]
    except (Exception, psycopg2.DatabaseError) as error:
        raise DatabaseError(error, payload, sql)
    return locations, count

def getReceipts(conn, site, payload, convert=False):
    receipts = []
    count = 0
    with open(f"sql/SELECT/getReceipts.sql", "r+") as file:
        sql = file.read().replace("%%site_name%%", site)
    try:
        with conn.cursor() as cur:
            cur.execute(sql, payload)
            rows = cur.fetchall()
            if rows and convert:
                receipts = [tupleDictionaryFactory(cur.description, row) for row in rows]
            if rows and not convert:
                receipts = rows

            cur.execute(f"SELECT COUNT(*) FROM {site}_receipts;")
            count = cur.fetchone()[0]
    except (Exception, psycopg2.DatabaseError) as error:
        raise DatabaseError(error, payload, sql)
    return receipts, count

def getReceiptByID(conn, site, payload, convert=False):
    receipt = []
    with open(f"sql/SELECT/getReceiptByID.sql", "r+") as file:
        sql = file.read().replace("%%site_name%%", site)
    try:
        with conn.cursor() as cur:
            cur.execute(sql, payload)
            row = cur.fetchone()
            if row and convert:
                receipt = tupleDictionaryFactory(cur.description, row)
            if row and not convert:
                receipt = row
    except (Exception, psycopg2.DatabaseError) as error:
        raise DatabaseError(error, payload, sql)
    return receipt

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
        raise DatabaseError(error, payload=(), sql=sql)
    
    return next_receipt_id

def getShoppingLists(conn, site, payload, convert=True):
    """_summary_

    Args:
        conn (_type_): _description_
        site (_type_): _description_
        payload (_type_): (limit, offset)
        convert (bool, optional): _description_. Defaults to True.

    Raises:
        DatabaseError: _description_

    Returns:
        _type_: _description_
    """
    recordset = []
    count = 0
    with open(f"sql/SELECT/getShoppingLists.sql", "r+") as file:
        sql = file.read().replace("%%site_name%%", site)
    try:
        with conn.cursor() as cur:
            cur.execute(sql, payload)
            rows = cur.fetchall()
            if rows and convert:
                recordset = [tupleDictionaryFactory(cur.description, row) for row in rows]
            if rows and not convert:
                recordset = rows

            cur.execute(f"SELECT COUNT(*) FROM {site}_shopping_lists;")
            count = cur.fetchone()[0]
    except (Exception, psycopg2.DatabaseError) as error:
        raise DatabaseError(error, payload, sql)
    return recordset, count

def getShoppingList(conn, site, payload, convert=True):
    """_summary_

    Args:
        conn (_type_): _description_
        site (_type_): _description_
        payload (_type_): (shopping_list_id, )
        convert (bool, optional): _description_. Defaults to True.

    Raises:
        DatabaseError: _description_

    Returns:
        _type_: _description_
    """
    recordset = []
    if convert:
        recordset = {}

    with open(f"sql/SELECT/getShoppingListByID.sql", "r+") as file:
        sql = file.read().replace("%%site_name%%", site)
    try:
        with conn.cursor() as cur:
            cur.execute(sql, payload)
            rows = cur.fetchone()
            if rows and convert:
                recordset = tupleDictionaryFactory(cur.description, rows)
            if rows and not convert:
                recordset = rows
            
    except (Exception, psycopg2.DatabaseError) as error:
        raise DatabaseError(error, payload, sql)
    return recordset

def getGroups(conn, site, payload, convert=True):
    """_summary_

    Args:
        conn (_type_): _description_
        site (_type_): _description_
        payload (_type_): (limit, offset)
        convert (bool, optional): _description_. Defaults to True.

    Raises:
        DatabaseError: _description_

    Returns:
        _type_: _description_
    """
    recordset = []
    count = 0
    with open(f"sql/SELECT/getGroups.sql", "r+") as file:
        sql = file.read().replace("%%site_name%%", site)
    try:
        with conn.cursor() as cur:
            cur.execute(sql, payload)
            rows = cur.fetchall()
            if rows and convert:
                recordset = [tupleDictionaryFactory(cur.description, row) for row in rows]
            if rows and not convert:
                recordset = rows

            cur.execute(f"SELECT COUNT(*) FROM {site}_groups;")
            count = cur.fetchone()[0]
    except (Exception, psycopg2.DatabaseError) as error:
        raise DatabaseError(error, payload, sql)
    return recordset, count

def getItemsSafetyStock(conn, site, convert=True):
    """_summary_

    Args:
        conn (_type_): _description_
        site (_type_): _description_
        payload (_type_): (limit, offset)
        convert (bool, optional): _description_. Defaults to True.

    Raises:
        DatabaseError: _description_

    Returns:
        _type_: _description_
    """
    recordsets = []
    with open(f"sql/SELECT/getItemsSafetyStock.sql", "r+") as file:
        sql = file.read().replace("%%site_name%%", site)
    try:
        with conn.cursor() as cur:
            cur.execute(sql)
            rows = cur.fetchall()
            if rows and convert:
                recordsets = [tupleDictionaryFactory(cur.description, row) for row in rows]
            if rows and not convert:
                recordsets = rows
    except (Exception, psycopg2.DatabaseError) as error:
        raise DatabaseError(error, None, sql)
    return recordsets