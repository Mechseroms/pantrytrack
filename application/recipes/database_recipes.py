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

def getRecipe(site, payload:tuple, convert=True):
    database_config = config.config()
    with open(f"application/recipes/sql/getRecipeByID.sql", "r+") as file:
        sql = file.read().replace("%%site_name%%", site)
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
    except (Exception, psycopg2.DatabaseError) as error:
        raise postsqldb.DatabaseError(error, payload, sql)

def getPicturePath(site:str, payload:tuple):
    database_config = config.config()
    with psycopg2.connect(**database_config) as conn:
        with conn.cursor() as cur:
            cur.execute(f"SELECT picture_path FROM {site}_recipes WHERE id=%s;", payload)
            rows = cur.fetchone()[0]
            return rows

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