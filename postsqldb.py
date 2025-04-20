import datetime
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
            file.write(f"{datetime.datetime.now()} --- ERROR --- DatabaseError(message='{self.message}',\n")
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

class ConversionsTable:
    @dataclass
    class Payload:
        item_id: int
        uom_id: int
        conv_factor: float

        def payload(self):
            return (
                self.item_id,
                self.uom_id,
                self.conv_factor
            )

    @classmethod
    def create_table(self, conn, site):
        with open(f"sql/CREATE/conversions.sql", 'r') as file:
            sql = file.read().replace("%%site_name%%", site)
        try:
            with conn.cursor() as cur:
                cur.execute(sql)
        except Exception as error: 
            raise DatabaseError(error, sql, "PrefixTable")

    @classmethod
    def delete_table(self, conn, site):
        with open(f"sql/DROP/conversions.sql", 'r') as file:
            sql = file.read().replace("%%site_name%%", site)
        try:
            with conn.cursor() as cur:
                cur.execute(sql)
        except Exception as error: 
            raise DatabaseError(error, 'ConversionsTable', sql)

    @classmethod
    def insert_tuple(self, conn, site: str, payload: list, convert=True):
        """insert into recipes table for site

        Args:
            conn (_T_connector@connect): Postgresql Connector
            site (stre):
            payload (tuple): (item_id, uom_id, conversion_factor) 
            convert (bool, optional): Determines if to return tuple as a dictionary. Defaults to False.

        Raises:
            DatabaseError:

        Returns:
            tuple or dict: inserted tuple
        """
        record = ()
        with open(f"sql/INSERT/insertConversionsTuple.sql", "r+") as file:
            sql = file.read().replace("%%site_name%%", site)
        try:
            with conn.cursor() as cur:
                cur.execute(sql, payload)
                rows = cur.fetchone()
                if rows and convert:
                    record = tupleDictionaryFactory(cur.description, rows)
                elif rows and not convert:
                    record = rows
        except Exception as error:
            raise DatabaseError(error, payload, sql)
        return record
    

    @classmethod
    def delete_item_tuple(self, conn, site_name, payload, convert=True):
        """This is a basic funtion to delete a tuple from a table in site with an id. All
        tables in this database has id's associated with them.

        Args:
            conn (_T_connector@connect): Postgresql Connector
            site_name (str):
            payload (tuple): (tuple_id,...)
            convert (bool, optional): Determines if to return tuple as dictionary. Defaults to False.

        Raises:
            DatabaseError:

        Returns:
            tuple or dict: deleted tuple
        """
        deleted = ()
        sql = f"WITH deleted_rows AS (DELETE FROM {site_name}_conversions WHERE id IN ({','.join(['%s'] * len(payload))}) RETURNING *) SELECT * FROM deleted_rows;"
        try:
            with conn.cursor() as cur:
                cur.execute(sql, payload)
                rows = cur.fetchone()
                if rows and convert:
                    deleted = tupleDictionaryFactory(cur.description, rows)
                elif rows and not convert:
                    deleted = rows
        except Exception as error:
            raise DatabaseError(error, payload, sql)
        return deleted

    @classmethod
    def update_item_tuple(self, conn, site, payload, convert=False):
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
        sql = f"UPDATE {site}_conversions SET {set_clause} WHERE id=%s RETURNING *;"
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

class ShoppingListsTable:
    @dataclass
    class Payload:
        name: str
        description: str
        author: int
        type: str = "plain"
        creation_date: datetime.datetime = field(init=False)

        def __post_init__(self):
            self.creation_date = datetime.datetime.now()

        def payload(self):
            return (
                self.name,
                self.description,
                self.author,
                self.creation_date,
                self.type
            )
    
    @dataclass
    class ItemPayload:
        uuid: str
        sl_id: int
        item_type: str
        item_name: str
        uom: str
        qty: float
        item_id: int = None
        links: dict = field(default_factory=dict)

        def payload(self):
            return (
                self.uuid,
                self.sl_id,
                self.item_type,
                self.item_name,
                self.uom,
                self.qty,
                self.item_id,
                json.dumps(self.links)
            )
        
    @classmethod
    def getItem(self, conn, site, payload, convert=True):
        """_summary_

        Args:
            conn (_type_): _description_
            site (_type_): _description_
            payload (_type_): (id, )
            convert (bool, optional): _description_. Defaults to True.

        Raises:
            DatabaseError: _description_

        Returns:
            _type_: _description_
        """
        record = ()
        with open('sql/SELECT/selectShoppingListItem.sql', 'r') as file:
            sql = file.read().replace("%%site_name%%", site)
        try:
            with conn.cursor() as cur:
                cur.execute(sql, payload)
                rows = cur.fetchone()
                if rows and convert:
                    record = tupleDictionaryFactory(cur.description, rows)
                elif rows and not convert:
                    record = rows
        except Exception as error:
            raise DatabaseError(error, payload, sql)
        return record
    
class UnitsTable:
    @dataclass
    class Payload:
        __slots__ = ('plural', 'single', 'fullname', 'description')

        plural: str
        single: str
        fullname: str
        description: str

        def payload(self):
            return (
               self.plural,
               self.single,
               self.fullname,
               self.description
            )
        
    @classmethod
    def create_table(self, conn):
        with open(f"sql/CREATE/units.sql", 'r') as file:
            sql = file.read()
        try:
            with conn.cursor() as cur:
                cur.execute(sql)
        except Exception as error: 
            raise DatabaseError(error, sql, "UnitsTable")

    @classmethod
    def delete_table(self, conn):
        with open(f"sql/DROP/units.sql", 'r') as file:
            sql = file.read()
        try:
            with conn.cursor() as cur:
                cur.execute(sql)
        except Exception as error: 
            raise DatabaseError(error, 'PrefixTable', sql)

    @classmethod
    def insert_tuple(self, conn, payload: list, convert=True):
        """_summary_

        Args:
            conn (_type_): _description_
            payload (list): (plural, single, fullname, description)
            convert (bool, optional): _description_. Defaults to True.

        Raises:
            DatabaseError: _description_

        Returns:
            _type_: _description_
        """
        record = ()
        with open(f"sql/INSERT/insertUnitsTuple.sql", "r+") as file:
            sql = file.read()
        try:
            with conn.cursor() as cur:
                cur.execute(sql, payload)
                rows = cur.fetchone()
                if rows and convert:
                    record = tupleDictionaryFactory(cur.description, rows)
                elif rows and not convert:
                    record = rows
        except Exception as error:
            raise DatabaseError(error, payload, sql)
        return record
    
    @classmethod
    def getAll(self, conn, convert=True):
        """_summary_

        Args:
            conn (_type_): _description_
            convert (bool, optional): _description_. Defaults to True.

        Raises:
            DatabaseError: _description_

        Returns:
            _type_: _description_
        """
        records = ()
        sql = f"SELECT * FROM units;"
        try:
            with conn.cursor() as cur:
                cur.execute(sql)
                rows = cur.fetchall()
                if rows and convert:
                    records = [tupleDictionaryFactory(cur.description, row) for row in rows] 
                elif rows and not convert:
                    records = rows
        except Exception as error:
            raise DatabaseError(error, "", sql)
        return records

class SKUPrefixTable:
    @dataclass
    class Payload:
        __slots__ = ('uuid', 'name', 'description')

        uuid: str
        name: str
        description: str

        def payload(self):
            return (
               self.uuid,
               self.name,
               self.description
            )
        
    @classmethod
    def create_table(self, conn, site):
        with open(f"sql/CREATE/sku_prefix.sql", 'r') as file:
            sql = file.read().replace("%%site_name%%", site)
        try:
            with conn.cursor() as cur:
                cur.execute(sql)
        except Exception as error: 
            raise DatabaseError(error, sql, "PrefixTable")

    @classmethod
    def delete_table(self, conn, site):
        with open(f"sql/DROP/sku_prefix.sql", 'r') as file:
            sql = file.read().replace("%%site_name%%", site)
        try:
            with conn.cursor() as cur:
                cur.execute(sql)
        except Exception as error: 
            raise DatabaseError(error, 'PrefixTable', sql)

    @classmethod
    def paginatePrefixes(self, conn, site: str, payload: tuple, convert=True):
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
        with open(f"sql/SELECT/getSkuPrefixes.sql", "r+") as file:
            sql = file.read().replace("%%site_name%%", site)
        try:
            with conn.cursor() as cur:
                cur.execute(sql, payload)
                rows = cur.fetchall()
                if rows and convert:
                    recordset = [tupleDictionaryFactory(cur.description, row) for row in rows]
                if rows and not convert:
                    recordset = rows

                cur.execute(f"SELECT COUNT(*) FROM {site}_sku_prefix;")
                count = cur.fetchone()[0]
        except (Exception, psycopg2.DatabaseError) as error:
            raise DatabaseError(error, payload, sql)
        return recordset, count
    
    @classmethod
    def insert_tuple(self, conn, site, payload, convert=True):
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
        prefix = ()
        with open(f"sql/INSERT/insertSKUPrefixTuple.sql", "r+") as file:
            sql = file.read().replace("%%site_name%%", site)
        try:
            with conn.cursor() as cur:
                cur.execute(sql, payload)
                rows = cur.fetchone()
                if rows and convert:
                    prefix = tupleDictionaryFactory(cur.description, rows)
                elif rows and not convert:
                    prefix = rows
        except Exception as error:
            raise DatabaseError(error, payload, sql)
        return prefix
    
    @classmethod
    def update_tuple(self, conn, site, payload, convert=True):
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
        sql = f"UPDATE {site}_sku_prefix SET {set_clause} WHERE id=%s RETURNING *;"
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

class RecipesTable:
    @dataclass
    class Payload:
        #__slots__ = ('name', 'author', 'description', 'created_date', 'instructions', 'picture_path')

        name: str
        author: int
        description: str
        created_date: datetime = field(init=False)
        instructions: list = field(default_factory=list)
        picture_path: str = ""

        def __post_init__(self):
            self.created_date = datetime.datetime.now()

        def payload(self):
            return (
                self.name,
                self.author,
                self.description,
                self.created_date,
                lst2pgarr(self.instructions),
                self.picture_path
            )
    
    @dataclass
    class ItemPayload:
        uuid: str
        rp_id: int
        item_type: str
        item_name:str
        uom: int
        qty: float = 0.0
        item_id: int = None
        links: dict = field(default_factory=dict)

        def payload(self):
            return (
                self.uuid,
                self.rp_id,
                self.item_type,
                self.item_name,
                self.uom,
                self.qty,
                self.item_id,
                json.dumps(self.links)
            )

    @classmethod
    def create_table(self, conn, site):
        with open(f"sql/CREATE/recipes.sql", 'r') as file:
            sql = file.read().replace("%%site_name%%", site)
        try:
            with conn.cursor() as cur:
                cur.execute(sql)
        except Exception as error: 
            raise DatabaseError(error, sql, "PrefixTable")

    @classmethod
    def delete_table(self, conn, site):
        with open(f"sql/DROP/recipes.sql", 'r') as file:
            sql = file.read().replace("%%site_name%%", site)
        try:
            with conn.cursor() as cur:
                cur.execute(sql)
        except Exception as error: 
            raise DatabaseError(error, 'PrefixTable', sql)

    @classmethod
    def insert_tuple(self, conn, site: str, payload: list, convert=True):
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
    
    @classmethod
    def insert_item_tuple(self, conn, site, payload, convert=True):
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
    
    @classmethod
    def delete_item_tuple(self, conn, site_name, payload, convert=True):
        """This is a basic funtion to delete a tuple from a table in site with an id. All
        tables in this database has id's associated with them.

        Args:
            conn (_T_connector@connect): Postgresql Connector
            site_name (str):
            payload (tuple): (tuple_id,...)
            convert (bool, optional): Determines if to return tuple as dictionary. Defaults to False.

        Raises:
            DatabaseError:

        Returns:
            tuple or dict: deleted tuple
        """
        deleted = ()
        sql = f"WITH deleted_rows AS (DELETE FROM {site_name}_recipe_items WHERE id IN ({','.join(['%s'] * len(payload))}) RETURNING *) SELECT * FROM deleted_rows;"
        try:
            with conn.cursor() as cur:
                cur.execute(sql, payload)
                rows = cur.fetchone()
                if rows and convert:
                    deleted = tupleDictionaryFactory(cur.description, rows)
                elif rows and not convert:
                    deleted = rows
        except Exception as error:
            raise DatabaseError(error, payload, sql)
        return deleted

    @classmethod
    def update_item_tuple(self, conn, site, payload, convert=False):
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
        sql = f"UPDATE {site}_recipe_items SET {set_clause} WHERE id=%s RETURNING *;"
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

    @classmethod
    def getRecipes(self, conn, site: str, payload: tuple, convert=True):
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
        with open(f"sql/SELECT/getRecipes.sql", "r+") as file:
            sql = file.read().replace("%%site_name%%", site)
        try:
            with conn.cursor() as cur:
                cur.execute(sql, payload)
                rows = cur.fetchall()
                if rows and convert:
                    recordset = [tupleDictionaryFactory(cur.description, row) for row in rows]
                if rows and not convert:
                    recordset = rows

                cur.execute(f"SELECT COUNT(*) FROM {site}_recipes;")
                count = cur.fetchone()[0]
        except (Exception, psycopg2.DatabaseError) as error:
            raise DatabaseError(error, payload, sql)
        return recordset, count

    @classmethod
    def getRecipe(self, conn, site: str, payload: tuple, convert=True):
        """_summary_

        Args:
            conn (_type_): _description_
            site (_type_): _description_
            payload (_type_): (id, )
            convert (bool, optional): _description_. Defaults to True.

        Raises:
            DatabaseError: _description_

        Returns:
            _type_: _description_
        """
        record = ()
        with open(f"sql/SELECT/getRecipeByID.sql", "r+") as file:
            sql = file.read().replace("%%site_name%%", site)
        try:
            with conn.cursor() as cur:
                cur.execute(sql, payload)
                rows = cur.fetchone()
                if rows and convert:
                    record = tupleDictionaryFactory(cur.description, rows)
                if rows and not convert:
                    record = rows
        except (Exception, psycopg2.DatabaseError) as error:
            raise DatabaseError(error, payload, sql)
        return record

    @classmethod
    def updateRecipe(self, conn, site, payload, convert=True):
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
        sql = f"UPDATE {site}_recipes SET {set_clause} WHERE id=%s RETURNING *;"
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

class ItemInfoTable:
    @dataclass
    class Payload:
        barcode: str
        packaging: str = ""
        uom_quantity: float = 1.0
        uom: int = 1
        cost: float = 0.0
        safety_stock: float = 0.0
        lead_time_days: float = 0.0
        ai_pick: bool = False
        prefixes: list = field(default_factory=list)

        def __post_init__(self):
            if not isinstance(self.barcode, str):
                raise TypeError(f"barcode must be of type str; not {type(self.barcode)}")
            
        def payload(self):
            return (
                self.barcode,
                self.packaging,
                self.uom_quantity,
                self.uom,
                self.cost,
                self.safety_stock,
                self.lead_time_days,
                self.ai_pick,
                lst2pgarr(self.prefixes)
            )
    @classmethod
    def select_tuple(self, conn, site:str, payload:tuple, convert=True):
        """_summary_

        Args:
            conn (_type_): _description_
            site (_type_): _description_
            payload (_type_): (item_info_id,)
            convert (bool, optional): _description_. Defaults to True.

        Raises:
            DatabaseError: _description_

        Returns:
            _type_: _description_
        """
        selected = ()
        sql = f"SELECT * FROM {site}_item_info WHERE id=%s;"
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
    
    @classmethod
    def update_tuple(self, conn, site:str, payload: dict, convert=True):
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
        sql = f"UPDATE {site}_item_info SET {set_clause} WHERE id=%s RETURNING *;"
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
    
class ItemTable:

    @classmethod
    def paginateLinkedLists(self, conn, site:str, payload:tuple, convert=True):
        records = []
        count = 0

        sql = f"SELECT * FROM {site}_items WHERE row_type = 'list' LIMIT %s OFFSET %s;"
        sql_count = f"SELECT COUNT(*) FROM {site}_items WHERE row_type = 'list' LIMIT %s OFFSET %s;"
        try:
            with conn.cursor() as cur:
                cur.execute(sql, payload)
                rows = cur.fetchall()
                if rows and convert:
                    records = [tupleDictionaryFactory(cur.description, row) for row in rows]
                if rows and not convert:
                    records = rows

                cur.execute(sql_count, payload)
                count = cur.fetchone()[0]

        except (Exception, psycopg2.DatabaseError) as error:
            raise DatabaseError(error, payload, sql)
        return records, count

    @classmethod
    def getItemAllByID(self, conn, site, payload, convert=True):
        """_summary_

        Args:
            conn (_type_): _description_
            site (_type_): _description_
            payload (_type_): (item_id, )
            convert (bool, optional): _description_. Defaults to False.

        Raises:
            DatabaseError: _description_

        Returns:
            _type_: _description_
        """
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
    
    @classmethod
    def getLinkedItemByBarcode(self, conn, site, payload, convert=True):
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

    @classmethod
    def getItemAllByBarcode(self, conn, site, payload, convert=True):
        item = ()
        if convert:
            item = {}
        linked_item = self.getLinkedItemByBarcode(conn, site, (payload[0],))

        if len(linked_item) > 1:
            item = self.getItemAllByID(conn, site, payload=(linked_item['link'], ), convert=convert)
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
    
    @classmethod
    def update_tuple(self, conn, site, payload, convert=True):
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
        sql = f"UPDATE {site}_items SET {set_clause} WHERE id=%s RETURNING *;"
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

class ReceiptTable:

    @classmethod
    def update_receipt(self, conn, site:str, payload:dict, convert=True):
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
        sql = f"UPDATE {site}_receipts SET {set_clause} WHERE id=%s RETURNING *;"
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
    
    @classmethod
    def update_receipt_item(self, conn, site:str, payload:dict, convert=True):
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
        sql = f"UPDATE {site}_receipt_items SET {set_clause} WHERE id=%s RETURNING *;"
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

    @classmethod
    def select_tuple(self, conn, site:str, payload:tuple, convert=True):
        """_summary_

        Args:
            conn (_type_): _description_
            site (_type_): _description_
            payload (_type_): (receipt_id,)
            convert (bool, optional): _description_. Defaults to True.

        Raises:
            DatabaseError: _description_

        Returns:
            _type_: _description_
        """
        selected = ()
        sql = f"SELECT * FROM {site}_receipts WHERE id=%s;"
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
    
    @classmethod
    def select_item_tuple(self, conn, site:str, payload:tuple, convert=True):
        """_summary_

        Args:
            conn (_type_): _description_
            site (_type_): _description_
            payload (_type_): (receipt_id,)
            convert (bool, optional): _description_. Defaults to True.

        Raises:
            DatabaseError: _description_

        Returns:
            _type_: _description_
        """
        selected = ()
        sql = f"SELECT * FROM {site}_receipt_items WHERE id=%s;"
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
    
class ZonesTable:
    @dataclass
    class Payload:
        name: str
        site_id: int
        description: str = ""

        def __post_init__(self):
            if not isinstance(self.name, str):
                raise TypeError(f"Zone name should be of type str; not {type(self.name)}")
            
        def payload(self):
            return (
                self.name,
                self.description,
                self.site_id
            )

    @classmethod
    def insert_tuple(self, conn, site, payload, convert=True):
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
    
    @classmethod
    def update_tuple(self, conn, site, payload, convert=True):
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
        sql = f"UPDATE {site}_zones SET {set_clause} WHERE id=%s RETURNING *;"
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

    @classmethod
    def paginateZones(self, conn, site:str, payload:tuple, convert=True):
        """_summary_

        Args:
            conn (_type_): _description_
            site (str): _description_
            payload (tuple): (limit, offset)
            convert (bool, optional): _description_. Defaults to True.

        Raises:
            DatabaseError: _description_

        Returns:
            _type_: _description_
        """
        recordset = ()
        count = 0
        sql = f"SELECT * FROM {site}_zones LIMIT %s OFFSET %s;"
        try:
            with conn.cursor() as cur:
                cur.execute(sql, payload)
                rows = cur.fetchall()
                if rows and convert:
                    recordset = [tupleDictionaryFactory(cur.description, row) for row in rows]
                elif rows and not convert:
                    recordset = rows

                cur.execute(f"SELECT COUNT(*) FROM {site}_zones;")
                count = cur.fetchone()[0]
        except Exception as error:
            raise DatabaseError(error, (), sql)
        return recordset, count
    
    @classmethod
    def paginateZonesBySku(self, conn, site: str, payload: tuple, convert=True):
        zones = ()
        count = 0
        with open(f"sql/SELECT/zones/paginateZonesBySku.sql", "r+") as file:
            sql = file.read().replace("%%site_name%%", site)
        with open(f"sql/SELECT/zones/paginateZonesBySkuCount.sql", "r+") as file:
            sql_count = file.read().replace("%%site_name%%", site)
        try:
            with conn.cursor() as cur:
                cur.execute(sql, payload)
                rows = cur.fetchall()
                if rows and convert:
                    zones = [tupleDictionaryFactory(cur.description, row) for row in rows]
                elif rows and not convert:
                    zones = rows

                cur.execute(sql_count, payload)
                count = cur.fetchone()[0]
                
        except Exception as error:
            raise DatabaseError(error, payload, sql)
        return zones, count
    
class LocationsTable:
    @dataclass
    class Payload:
        uuid: str
        name: str
        zone_id: int

        def __post_init__(self):
            if not isinstance(self.uuid, str):
                raise TypeError(f"uuid must be of type str; not {type(self.uuid)}")
            if not isinstance(self.name, str):
                raise TypeError(f"Location name must be of type str; not {type(self.name)}")
            if not isinstance(self.zone_id, int):
                raise TypeError(f"zone_id must be of type str; not {type(self.zone_id)}")
        
        def payload(self):
            return (
                self.uuid,
                self.name,
                self.zone_id
            )
    
    @classmethod
    def paginateLocations(self, conn, site:str, payload:tuple, convert=True):
        """_summary_

        Args:
            conn (_type_): _description_
            site (str): _description_
            payload (tuple): (limit, offset)
            convert (bool, optional): _description_. Defaults to True.

        Raises:
            DatabaseError: _description_

        Returns:
            _type_: _description_
        """
        recordset = ()
        count = 0
        sql = f"SELECT * FROM {site}_locations LIMIT %s OFFSET %s;"
        try:
            with conn.cursor() as cur:
                cur.execute(sql, payload)
                rows = cur.fetchall()
                if rows and convert:
                    recordset = [tupleDictionaryFactory(cur.description, row) for row in rows]
                elif rows and not convert:
                    recordset = rows

                cur.execute(f"SELECT COUNT(*) FROM {site}_locations;")
                count = cur.fetchone()[0]
        except Exception as error:
            raise DatabaseError(error, (), sql)
        return recordset, count
    
    @classmethod
    def paginateLocationsWithZone(self, conn, site:str, payload:tuple, convert=True):
        """_summary_

        Args:
            conn (_type_): _description_
            site (str): _description_
            payload (tuple): (limit, offset)
            convert (bool, optional): _description_. Defaults to True.

        Raises:
            DatabaseError: _description_

        Returns:
            _type_: _description_
        """
        recordset = ()
        count = 0
        with open(f"sql/SELECT/getLocationsWithZone.sql", "r+") as file:
            sql = file.read().replace("%%site_name%%", site)
        try:
            with conn.cursor() as cur:
                cur.execute(sql, payload)
                rows = cur.fetchall()
                if rows and convert:
                    recordset = [tupleDictionaryFactory(cur.description, row) for row in rows]
                elif rows and not convert:
                    recordset = rows
                cur.execute(f"SELECT COUNT(*) FROM {site}_locations;")
                count = cur.fetchone()[0]
        except Exception as error:
            raise DatabaseError(error, (), sql)
        return recordset, count
    
    @classmethod
    def paginateLocationsBySkuZone(self, conn, site: str, payload: tuple, convert=True):
        """_summary_

        Args:
            conn (_type_): _description_
            site (str): _description_
            payload (tuple): (item_id, zone_id, limit, offset)
            convert (bool, optional): _description_. Defaults to True.

        Raises:
            DatabaseError: _description_

        Returns:
            _type_: _description_
        """
        locations = ()
        count = 0
        with open(f"sql/SELECT/locations/paginateLocationsBySkuZone.sql", "r+") as file:
            sql = file.read().replace("%%site_name%%", site)
        with open(f"sql/SELECT/locations/paginateLocationsBySkuZoneCount.sql", "r+") as file:
            sql_count = file.read().replace("%%site_name%%", site)
        try:
            with conn.cursor() as cur:
                cur.execute(sql, payload)
                rows = cur.fetchall()
                if rows and convert:
                    locations = [tupleDictionaryFactory(cur.description, row) for row in rows]
                elif rows and not convert:
                    locations = rows

                cur.execute(sql_count, payload)
                count = cur.fetchone()[0]
                
        except Exception as error:
            raise DatabaseError(error, payload, sql)
        return locations, count
    
    @classmethod
    def insert_tuple(self, conn, site, payload, convert=True):
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
        with open(f"sql/INSERT/insertLocationsTuple.sql", "r+") as file:
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
    
class VendorsTable:
    @dataclass
    class Payload:
        vendor_name: str
        created_by: int
        vendor_address: str = ""
        creation_date: datetime.datetime = field(init=False)
        phone_number: str = ""

        def __post_init__(self):
            if not isinstance(self.vendor_name, str):
                raise TypeError(f"vendor_name should be of type str; not {type(self.vendor_name)}")
            self.creation_date = datetime.datetime.now()


        def payload(self):
            return (
                self.vendor_name,
                self.vendor_address,
                self.creation_date,
                self.created_by,
                self.phone_number
            )
    
    @classmethod
    def paginateVendors(self, conn, site:str, payload:tuple, convert=True):
        """_summary_

        Args:
            conn (_type_): _description_
            site (str): _description_
            payload (tuple): (limit, offset)
            convert (bool, optional): _description_. Defaults to True.

        Raises:
            DatabaseError: _description_

        Returns:
            _type_: _description_
        """
        recordset = ()
        count = 0
        sql = f"SELECT * FROM {site}_vendors LIMIT %s OFFSET %s;"
        try:
            with conn.cursor() as cur:
                cur.execute(sql, payload)
                rows = cur.fetchall()
                if rows and convert:
                    recordset = [tupleDictionaryFactory(cur.description, row) for row in rows]
                elif rows and not convert:
                    recordset = rows

                cur.execute(f"SELECT COUNT(*) FROM {site}_vendors;")
                count = cur.fetchone()[0]
        except Exception as error:
            raise DatabaseError(error, (), sql)
        return recordset, count
    
    @classmethod
    def insert_tuple(self, conn, site, payload, convert=True):
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
        with open(f"sql/INSERT/insertVendorsTuple.sql", "r+") as file:
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
    
    @classmethod
    def update_tuple(self, conn, site, payload, convert=True):
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
        sql = f"UPDATE {site}_vendors SET {set_clause} WHERE id=%s RETURNING *;"
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
    
class BrandsTable:
    @dataclass
    class Payload:
        name: str

        def __post_init__(self):
            if not isinstance(self.name, str):
                return TypeError(f"brand name should be of type str; not {type(self.name)}")
            
        def payload(self):
            return (
                self.name,
            )
        
    @classmethod
    def paginateBrands(self, conn, site:str, payload:tuple, convert=True):
        """_summary_

        Args:
            conn (_type_): _description_
            site (str): _description_
            payload (tuple): (limit, offset)
            convert (bool, optional): _description_. Defaults to True.

        Raises:
            DatabaseError: _description_

        Returns:
            _type_: _description_
        """
        recordset = ()
        count = 0
        sql = f"SELECT * FROM {site}_brands LIMIT %s OFFSET %s;"
        try:
            with conn.cursor() as cur:
                cur.execute(sql, payload)
                rows = cur.fetchall()
                if rows and convert:
                    recordset = [tupleDictionaryFactory(cur.description, row) for row in rows]
                elif rows and not convert:
                    recordset = rows

                cur.execute(f"SELECT COUNT(*) FROM {site}_brands;")
                count = cur.fetchone()[0]
        except Exception as error:
            raise DatabaseError(error, (), sql)
        return recordset, count
    
    @classmethod
    def insert_tuple(self, conn, site, payload, convert=True):
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
    
    @classmethod
    def update_tuple(self, conn, site, payload, convert=True):
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
        sql = f"UPDATE {site}_brands SET {set_clause} WHERE id=%s RETURNING *;"
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
    
class ItemLocationsTable:
    @dataclass
    class Payload:
        part_id: int
        location_id: int
        quantity_on_hand: float = 0.0
        cost_layers: list = field(default_factory=list)

        def __post_init__(self):
            if not isinstance(self.part_id, int):
                raise TypeError(f"part_id must be of type int; not {type(self.part_id)}")
            if not isinstance(self.location_id, int):
                raise TypeError(f"part_id must be of type int; not {type(self.part_id)}")

        def payload(self):
            return (
                self.part_id,
                self.location_id,
                self.quantity_on_hand,
                lst2pgarr(self.cost_layers)
            )
    
    @classmethod
    def insert_tuple(self, conn, site, payload, convert=True):
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
        item_location = ()
        with open(f"sql/INSERT/insertItemLocationsTuple.sql", "r+") as file:
            sql = file.read().replace("%%site_name%%", site)
        try:
            with conn.cursor() as cur:
                cur.execute(sql, payload)
                rows = cur.fetchone()
                if rows and convert:
                    item_location = tupleDictionaryFactory(cur.description, rows)
                elif rows and not convert:
                    item_location = rows
        except Exception as error:
            raise DatabaseError(error, payload, sql)
        return item_location
    
    @classmethod
    def select_by_id(self, conn, site: str, payload: tuple, convert=True):
        item_locations = ()
        with open(f"sql/SELECT/selectItemLocations", "r+") as file:
            sql = file.read().replace("%%site_name%%", site)
        try:
            with conn.cursor() as cur:
                cur.execute(sql, payload)
                rows = cur.fetchall()
                if rows and convert:
                    item_locations = [tupleDictionaryFactory(cur.description, row) for row in rows]
                elif rows and not convert:
                    item_locations = rows
        except Exception as error:
            raise DatabaseError(error, payload, sql)
        return item_locations
    
class ItemLinksTable:
    @dataclass
    class Payload:
        barcode: str
        link: int
        data: dict = field(default_factory=dict)
        conv_factor: float = 1

        def __post_init__(self):
            if not isinstance(self.barcode, str):
                raise TypeError(f"barcode must be of type str; not {type(self.barocde)}")
            if not isinstance(self.link, int):
                raise TypeError(f"link must be of type str; not {type(self.link)}")

        def payload(self):
            return (
                self.barcode,
                self.link,
                json.dumps(self.data),
                self.conv_factor
            )
    
    @classmethod
    def insert_tuple(self, conn, site:str, payload:tuple, convert=True):
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

class CycleCountsTable:
    @dataclass
    class Payload:
        pass

class SitesTable:
    @classmethod
    def selectTuples(self, conn, convert=True):
        recordsets = []
        sql = f"SELECT * FROM sites"
        try:
            with conn.cursor() as cur:
                cur.execute(sql)
                rows = cur.fetchall()
                if rows and convert:
                    recordsets = [tupleDictionaryFactory(cur.description, row) for row in rows]
                elif rows and not convert:
                    recordsets = rows
        except Exception as error:
            raise DatabaseError(error, (), sql)
        return recordsets