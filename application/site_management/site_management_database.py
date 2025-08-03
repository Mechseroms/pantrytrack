# 3RD PARTY IMPORTS
import psycopg2

# APPLICATION IMPORTS
import config
from application import postsqldb

def paginateZonesTuples(site, payload, convert=True, conn=None):
    """ payload (tuple): (limit, offset) """
    recordset = ()
    count = 0
    self_conn = False
    sql = f"SELECT * FROM {site}_zones LIMIT %s OFFSET %s;"
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

            cur.execute(f"SELECT COUNT(*) FROM {site}_zones;")
            count = cur.fetchone()[0]

        if self_conn:
            conn.commit()
            conn.close()

        return recordset, count
    
    except Exception as error:
        raise postsqldb.DatabaseError(error, (), sql)

def paginateLocationsTuples(site, payload, convert=True, conn=None):
    """ payload (tuple): (limit, offset) """
    recordset = ()
    count = 0
    self_conn = False
    sql = f"SELECT * FROM {site}_locations LIMIT %s OFFSET %s;"
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

            cur.execute(f"SELECT COUNT(*) FROM {site}_locations;")
            count = cur.fetchone()[0]
        
        if self_conn:
            conn.commit()
            conn.close()
        
        return recordset, count
    except Exception as error:
        raise postsqldb.DatabaseError(error, (), sql)

def paginateVendorsTuples(site, payload, convert=True, conn=None):
        """ payload (tuple): (limit, offset) """
        recordset = ()
        count = 0
        self_conn = False
        sql = f"SELECT * FROM {site}_vendors LIMIT %s OFFSET %s;"
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

                cur.execute(f"SELECT COUNT(*) FROM {site}_vendors;")
                count = cur.fetchone()[0]
            
            if self_conn:
                conn.commit()
                conn.close()
            
            return recordset, count
        except Exception as error:
            raise postsqldb.DatabaseError(error, (), sql)

def paginateBrandsTuples(site, payload, convert=True, conn=None):
    """ payload (tuple): (limit, offset) """
    recordset = ()
    count = 0
    self_conn = False
    sql = f"SELECT * FROM {site}_brands LIMIT %s OFFSET %s;"
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

            cur.execute(f"SELECT COUNT(*) FROM {site}_brands;")
            count = cur.fetchone()[0]
        
        if self_conn:
            conn.commit()
            conn.close()
        
        return recordset, count
    except Exception as error:
        raise postsqldb.DatabaseError(error, (), sql)

def paginatePrefixesTuples(site, payload, convert=True, conn=None):
    """ payload (_type_): (limit, offset) """
    recordset = []
    self_conn = False
    count = 0
    sql = f"SELECT * FROM {site}_sku_prefix LIMIT %s OFFSET %s;"
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

            cur.execute(f"SELECT COUNT(*) FROM {site}_sku_prefix;")
            count = cur.fetchone()[0]
        
        if self_conn:
            conn.commit()
            conn.close()
        
        return recordset, count
    except (Exception, psycopg2.DatabaseError) as error:
        raise postsqldb.DatabaseError(error, payload, sql)

def selectSitesTupleByName(payload, convert=True, conn=None):
    """ payload (_type_): (site_name,) """
    record = ()
    self_conn = False
    sql = f"SELECT id FROM sites WHERE site_name = %s;"
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
            conn.commit()
            conn.close()
        
        return record
    except (Exception, psycopg2.DatabaseError) as error:
        raise postsqldb.DatabaseError(error, payload, sql)

def selectZonesTuples(site, convert=True, conn=None):
    """ payload (tuple): (limit, offset) """
    recordset = ()
    self_conn = False
    sql = f"SELECT * FROM {site}_zones;"
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
                recordset = [postsqldb.tupleDictionaryFactory(cur.description, row) for row in rows]
            elif rows and not convert:
                recordset = rows

        if self_conn:
            conn.commit()
            conn.close()

        return recordset
    
    except Exception as error:
        raise postsqldb.DatabaseError(error, (), sql)

def insertZonesTuple(site, payload, convert=True, conn=None):
    """ payload (tuple): (name[str],) """
    zone = ()
    self_conn = False
    with open(f"application/site_management/sql/insertZonesTuple.sql", "r+") as file:
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
                zone = postsqldb.tupleDictionaryFactory(cur.description, rows)
            elif rows and not convert:
                zone = rows
        
        if self_conn:
            conn.commit()
            conn.close()

        return zone
    except Exception as error:
        raise postsqldb.DatabaseError(error, payload, sql)

def insertLocationsTuple(site, payload, convert=True, conn=None):
    """ payload (tuple): (name[str],) """
    zone = ()
    self_conn = False
    with open(f"application/site_management/sql/insertLocationsTuple.sql", "r+") as file:
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
                zone = postsqldb.tupleDictionaryFactory(cur.description, rows)
            elif rows and not convert:
                zone = rows

        if self_conn:
            conn.commit()
            conn.close()
        
        return zone
    except Exception as error:
        raise postsqldb.DatabaseError(error, payload, sql)

def insertVendorsTuple(site, payload, convert=True, conn=None):
    """ payload (tuple): (name[str],) """
    zone = ()
    self_conn = False
    with open(f"application/site_management/sql/insertVendorsTuple.sql", "r+") as file:
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
                zone = postsqldb.tupleDictionaryFactory(cur.description, rows)
            elif rows and not convert:
                zone = rows
        
        if self_conn:
            conn.commit()
            conn.close()
                
        return zone
    except Exception as error:
        raise postsqldb.DatabaseError(error, payload, sql)

def insertBrandsTuple(site, payload, convert=True, conn=None):
    """ payload (tuple): (name[str],) """
    brand = ()
    self_conn = False
    with open(f"application/site_management/sql/insertBrandsTuple.sql", "r+") as file:
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
                brand = postsqldb.tupleDictionaryFactory(cur.description, rows)
            elif rows and not convert:
                brand = rows

        if self_conn:
            conn.commit()
            conn.close()

        return brand 
    except Exception as error:
        raise postsqldb.DatabaseError(error, payload, sql)

def insertSKUPrefixesTuple(site, payload, convert=True, conn=None):
    """ payload (tuple): (name[str],) """
    prefix = ()
    self_conn = False
    with open(f"application/site_management/sql/insertSKUPrefixTuple.sql", "r+") as file:
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

def updateSKUPrefixesTuple(site, payload, convert=True, conn=None):
    """ payload (dict): {'id': row_id, 'update': {... column_to_update: value_to_update_to...}} """
    updated = ()
    self_conn = False
    set_clause, values = postsqldb.updateStringFactory(payload['update'])
    values.append(payload['id'])
    sql = f"UPDATE {site}_sku_prefix SET {set_clause} WHERE id=%s RETURNING *;"
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
    
def updateZonesTuple(site, payload, convert=True, conn=None):
    """ payload (dict): {'id': row_id, 'update': {... column_to_update: value_to_update_to...}} """
    updated = ()
    self_conn = False
    set_clause, values = postsqldb.updateStringFactory(payload['update'])
    values.append(payload['id'])
    sql = f"UPDATE {site}_zones SET {set_clause} WHERE id=%s RETURNING *;"
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

def updateVendorsTuple(site, payload, convert=True, conn=None):
    """ payload (dict): {'id': row_id, 'update': {... column_to_update: value_to_update_to...}} """
    updated = ()
    self_conn = False
    set_clause, values = postsqldb.updateStringFactory(payload['update'])
    values.append(payload['id'])
    sql = f"UPDATE {site}_vendors SET {set_clause} WHERE id=%s RETURNING *;"
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

def updateBrandsTuple(site, payload, convert=True, conn=None):
    """ payload (dict): {'id': row_id, 'update': {... column_to_update: value_to_update_to...}} """
    updated = ()
    self_conn = False
    set_clause, values = postsqldb.updateStringFactory(payload['update'])
    values.append(payload['id'])
    sql = f"UPDATE {site}_brands SET {set_clause} WHERE id=%s RETURNING *;"
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
