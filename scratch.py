
from config import config 
import psycopg2, requests
import main, datetime, json



database_config = config()
with psycopg2.connect(**database_config) as conn:

# update user with site_id and admin role.
    sqlfile = open('sites/main/sql/unique/shopping_lists_safetystock_uncalculated.sql', "r+")
    sql = sqlfile.readlines()
    sql = "\n".join(sql)
    sqlfile.close()
    try:
        with conn.cursor() as cur:
            cur.execute(sql, (1, ))
            x = cur.fetchall()
            for _ in x:
                print(_)

    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
        conn.rollback()
