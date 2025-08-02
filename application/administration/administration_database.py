from application import postsqldb
import psycopg2
import config

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

def selectLoginsTuple(payload, convert=True, conn=None):
    user = ()
    self_conn = False
    with open("application/administration/sql/selectLoginsUser.sql", "r") as file:
        sql = file.read()
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
                user = postsqldb.tupleDictionaryFactory(cur.description, rows)
            elif rows and not convert:
                user = rows

        if self_conn:
            conn.close()

        return user
    except Exception as error:
        raise postsqldb.DatabaseError(error, payload, sql)

def selectSitesTuple(payload, convert=True, conn=None):
    record = []
    self_conn = False
    sql = f"SELECT * FROM sites WHERE id=%s;"
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
        raise postsqldb.DatabaseError(error, (), sql)

def selectSiteTupleByName(payload, convert=True, conn=None):
    """ payload (tuple): (site_name,) """
    site = ()
    self_conn = False
    select_site_sql = f"SELECT * FROM sites WHERE site_name = %s;"
    try:
        if not conn:
            database_config = config.config()
            conn = psycopg2.connect(**database_config)
            conn.autocommit = True
            self_conn = True
        
        with conn.cursor() as cur:
            cur.execute(select_site_sql, payload)
            rows = cur.fetchone()
            if rows and convert:
                site = postsqldb.tupleDictionaryFactory(cur.description, rows)
            elif rows and not convert:
                site = rows
        
        if self_conn:
            conn.commit()
            conn.close()

        return site

    except Exception as error:
        raise postsqldb.DatabaseError(error, payload, select_site_sql)

def selectSitesTuples(convert=True, conn=None):
    sites = []
    self_conn = False
    sql = f"SELECT * FROM sites;"
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
                sites = [postsqldb.tupleDictionaryFactory(cur.description, row) for row in rows]
            elif rows and not convert:
                sites = rows

        if self_conn:
            conn.close()

        return sites
    except Exception as error:
        raise postsqldb.DatabaseError(error, (), sql)
        
def selectRolesTuple(payload, convert=True, conn=None):
    role = []
    self_conn = False
    sql = f"SELECT roles.*, row_to_json(sites.*) as site FROM roles LEFT JOIN sites ON sites.id = roles.site_id WHERE roles.id=%s;"
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
                role = postsqldb.tupleDictionaryFactory(cur.description, rows)
            elif rows and not convert:
                role = rows
        if self_conn:
            conn.close()

        return role
    except Exception as error:
        raise postsqldb.DatabaseError(error, (), sql)

def selectRolesTupleBySite(payload, convert=True, conn=None):
    """ payload (tuple): (site_id,) """
    roles = ()
    self_conn = False
    select_roles_sql = f"SELECT * FROM roles WHERE site_id = %s;"
    try:
        if not conn:
            database_config = config.config()
            conn = psycopg2.connect(**database_config)
            conn.autocommit = True
            self_conn = True

        with conn.cursor() as cur:
            cur.execute(select_roles_sql, payload)
            rows = cur.fetchall()
            if rows and convert:
                roles = [postsqldb.tupleDictionaryFactory(cur.description, role) for role in rows]
            elif rows and not convert:
                roles = rows
        
        if self_conn:
            conn.close()

        return roles
    except Exception as error:
        raise postsqldb.DatabaseError(error, payload, select_roles_sql)

def paginateSitesTuples(payload, convert=True, conn=None):
    """ payload (tuple): (limit, offset) """
    recordsets = []
    count = 0
    self_conn = False
    sql = f"SELECT * FROM sites LIMIT %s OFFSET %s;"
    sql_count = f"SELECT COUNT(*) FROM sites;"
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
            elif rows and not convert:
                recordsets = rows
            cur.execute(sql_count)
            count = cur.fetchone()[0]

        if self_conn:
            conn.close()

        return recordsets, count
    except Exception as error:
        raise postsqldb.DatabaseError(error, (), sql)

def paginateRolesTuples(payload, convert=True, conn=None):
    """ payload (tuple): (limit, offset) """
    recordset = []
    self_conn = False
    sql = f"SELECT roles.*, row_to_json(sites.*) as site FROM roles LEFT JOIN sites ON sites.id = roles.site_id LIMIT %s OFFSET %s;"
    sql_count = f"SELECT COUNT(*) FROM roles;"

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
            cur.execute(sql_count)
            count = cur.fetchone()[0]

        if self_conn:
            conn.close()

        return recordset, count
    except Exception as error:
        raise postsqldb.DatabaseError(error, payload, sql)

def paginateLoginsTuples(payload, convert=True, conn=None):
    """ payload (tuple): (limit, offset) """
    recordset = []
    self_conn = False
    sql = f"SELECT * FROM logins LIMIT %s OFFSET %s;"
    sql_count = f"SELECT COUNT(*) FROM logins;"

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

            cur.execute(sql_count)
            count = cur.fetchone()[0]

        if self_conn:
            conn.close()

        return recordset, count
    except Exception as error:
        raise postsqldb.DatabaseError(error, payload, sql)

def insertSitesTuple(payload, convert=True, conn=None):
    """ payload (tuple): (site_name[str], site_description[str], creation_date[timestamp], site_owner_id[int],
          flags[dict], default_zone[str], default_auto_issue_location[str], default_primary_location[str]) """
    site_tuple = ()
    self_conn = False
    with open(f"application/administration/sql/insertSitesTuple.sql", "r+") as file:
        sql = file.read()
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
                site_tuple = postsqldb.tupleDictionaryFactory(cur.description, rows)
            elif rows and not convert:
                site_tuple = rows

        if self_conn:
            conn.commit()
            conn.close()
        
        return site_tuple
    except Exception as error:
        raise postsqldb.DatabaseError(error, payload, sql)

def insertRolesTuple(payload, convert=True, conn=None):
    """ payload (tuple): (role_name[str], role_description[str], site_id[int], flags[jsonb]) """
    role_tuple = ()
    self_conn = False
    with open(f"application/administration/sql/insertRolesTuple.sql", "r+") as file:
        sql = file.read()
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
                role_tuple = postsqldb.tupleDictionaryFactory(cur.description, rows)
            elif rows and not convert:
                role_tuple = rows
        
        if self_conn:
            conn.commit()
            conn.close()

        return role_tuple
    except Exception as error:
        raise postsqldb.DatabaseError(error, payload, sql)

def insertZonesTuple(site, payload, convert=True, conn=None):
    """ payload (tuple): (name[str],) """
    zone = ()
    self_conn = False
    with open(f"application/administration/sql/insertZonesTuple.sql", "r+") as file:
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
    """ payload (tuple): (uuid[str], name[str], zone_id[int], items[jsonb]) """
    location = ()
    self_conn = False
    with open(f"application/administration/sql/insertLocationsTuple.sql", "r+") as file:
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

def insertVendorsTuple(site, payload, convert=True, conn=None):
    """ payload (tuple): (vendor_name[str], vendor_address[str], creation_date[timestamp], created_by[int], phone_number[str]) """
    vendor = ()
    self_conn = False
    with open(f"application/administration/sql/insertVendorsTuple.sql", "r+") as file:
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
                vendor = postsqldb.tupleDictionaryFactory(cur.description, rows)
            elif rows and not convert:
                vendor = rows
        
        if self_conn:
            conn.commit()
            conn.close()
        
        return vendor
    except Exception as error:
        raise postsqldb.DatabaseError(error, payload, sql)

def insertBrandsTuple(site, payload, convert=True, conn=None):
    """ payload (tuple): (brand_name[str], ) """
    brand = ()
    self_conn = False
    with open(f"application/administration/sql/insertBrandsTuple.sql", "r+") as file:
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

def updateAddLoginSitesRoles(payload, convert=True, conn=None):
    """ payload (tuple): (site_id, role_id, login_id) """
    sql = f"UPDATE logins SET sites = sites || %s, site_roles = site_roles || %s WHERE id=%s RETURNING *;"
    login = ()
    self_conn = False
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
                login = postsqldb.tupleDictionaryFactory(cur.description, rows)
            elif rows and not convert:
                login = rows
        
        if self_conn:
            conn.commit()
            conn.close()

        return login
    except Exception as error:
        raise postsqldb.DatabaseError(error, payload, sql)

def updateSitesTuple(payload, convert=True, conn=None):
    """ payload (dict): {'id': row_id, 'update': {... column_to_update: value_to_update_to...}} """
    updated = ()
    self_conn = False
    set_clause, values = postsqldb.updateStringFactory(payload['update'])
    values.append(payload['id'])
    sql = f"UPDATE sites SET {set_clause} WHERE id=%s RETURNING *;"
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

def updateUsersSites(payload, convert=True, conn=None):
    """ payload: {'site_id',} """
    self_conn = False
    try:
        if not conn:
            database_config = config.config()
            conn = psycopg2.connect(**database_config)
            conn.autocommit = True
            self_conn = True

        select_sql = f"SELECT logins.id FROM logins WHERE sites @> ARRAY[%s];"
        with conn.cursor() as cur:
            cur.execute(select_sql, (payload['site_id'], ))
            user = tuple([row[0] for row in cur.fetchall()])

        update_sql = f"UPDATE logins SET sites = array_remove(sites, %s) WHERE id = %s;"
        with conn.cursor() as cur:
            for user_id in user:
                cur.execute(update_sql, (payload['site_id'], user_id))
        
        if self_conn:
            conn.commit()
            conn.close()

    except Exception as error:
        raise error

def updateUsersRoles(payload, convert=True, conn=None):
    """ payload: {'role_id',} """
    self_conn = False
    try:
        if not conn:
            database_config = config.config()
            conn = psycopg2.connect(**database_config)
            conn.autocommit = True
            self_conn = True

        select_sql = f"SELECT logins.id FROM logins WHERE site_roles @> ARRAY[%s];"
        with conn.cursor() as cur:
            cur.execute(select_sql, (payload['role_id'], ))
            users = tuple([row[0] for row in cur.fetchall()])

        update_sql = f"UPDATE logins SET site_roles = array_remove(site_roles, %s) WHERE id = %s;"
        with conn.cursor() as cur:
            for user_id in users:
                cur.execute(update_sql, (payload['role_id'], user_id))
        
        if self_conn:
            conn.commit()
            conn.close()

    except Exception as error:
        raise error

def createTable(site, table, conn=None):
    self_conn = False
    with open(f"application/administration/sql/CREATE/{table}.sql", 'r') as file:
        sql = file.read().replace("%%site_name%%", site)
    try:
        if not conn:
            database_config = config.config()
            conn = psycopg2.connect(**database_config)
            conn.autocommit = True
            self_conn = True

        with conn.cursor() as cur:
            cur.execute(sql)
        
        if self_conn:
            conn.commit()
            conn.close()

    except Exception as error: 
        raise postsqldb.DatabaseError(error, sql, table)

def dropTable(site, table, conn=None):
    self_conn = False
    with open(f"application/administration/sql/DROP/{table}.sql", 'r') as file:
        sql = file.read().replace("%%site_name%%", site)
    try:
        if not conn:
            database_config = config.config()
            conn = psycopg2.connect(**database_config)
            conn.autocommit = True
            self_conn = True

        with conn.cursor() as cur:
            cur.execute(sql)

        if self_conn:
            conn.commit()
            conn.close()

    except Exception as error: 
        raise postsqldb.DatabaseError(error, sql, table)

def deleteSitesTuple(payload, convert=True, conn=None):
    """payload (tuple): (tuple_id, )"""
    deleted = ()
    self_conn = False
    sql = f"WITH deleted_rows AS (DELETE FROM sites WHERE id IN ({','.join(['%s'] * len(payload))}) RETURNING *) SELECT * FROM deleted_rows;"
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

def deleteRolesTuple(payload, convert=True, conn=None):
    """payload (tuple): (tuple_id, )"""
    deleted = ()
    self_conn = False
    sql = f"WITH deleted_rows AS (DELETE FROM roles WHERE id IN ({','.join(['%s'] * len(payload))}) RETURNING *) SELECT * FROM deleted_rows;"
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
    