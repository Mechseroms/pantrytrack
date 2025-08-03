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
          'flags': user['flags']
    }

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