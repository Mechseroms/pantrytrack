import postsqldb
import psycopg2
import config

def selectLoginsUser(login_id):
    database_config = config.config()
    try:
        with psycopg2.connect(**database_config) as conn:
            with open("sql/SELECT/admin/selectLoginsUser.sql", "r") as file:
                sql = file.read()
            with conn.cursor() as cur:
                cur.execute(sql, (login_id,))
                user = cur.fetchone()
                if user:
                    user = postsqldb.tupleDictionaryFactory(cur.description, user)
                return user
    except Exception as error:
        raise postsqldb.DatabaseError(error, login_id, sql)