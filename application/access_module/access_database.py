import psycopg2

import config
from application import postsqldb

def washUserDictionary(user):
     return {
          'id': user['id'],
          'username': user['username'],
          'sites': user['sites'],
          'site_roles': user['site_roles'],
          'system_admin': user['system_admin'],
          'flags': user['flags'],
          'profile_pic_url': user['profile_pic_url'],
          'login_type': user['login_type']
    }

def selectLoginsTupleByID(payload, convert=True, conn=None):
    """ payload = (id,)"""
    self_conn = False
    user = ()
    sql = f"SELECT * FROM logins WHERE id=%s;"
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
            conn.commit()
            conn.close()
        
        return user
    except Exception as error:
        raise postsqldb.DatabaseError(error, payload, sql)

def selectUserByEmail(payload, convert=True, conn=None):
    """ payload = (email,)"""
    self_conn = False
    user = ()
    sql = f"SELECT * FROM logins WHERE email=%s;"
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
            conn.commit()
            conn.close()
        
        return user
    except Exception as error:
        raise postsqldb.DatabaseError(error, payload, sql)
    

def updateLoginsTuple(payload, convert=True, conn=None):
    """ payload = {'id': user_id, 'update': {...}}"""
    self_conn = False
    user = ()
    set_clause, values = postsqldb.updateStringFactory(payload['update'])
    values.append(payload['id'])
    sql = f"UPDATE logins SET {set_clause} WHERE id=%s RETURNING *;"
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
                user = postsqldb.tupleDictionaryFactory(cur.description, rows)
            elif rows and not convert:
                user = rows
        
        if self_conn:
            conn.commit()
            conn.close()

        return user
    except Exception as error:
        raise postsqldb.DatabaseError(error, payload, sql)