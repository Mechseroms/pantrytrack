from scripts import postsqldb
import config
import psycopg2

def getModalSKUs(site, payload, convert=True):
    database_config = config.config()
    with psycopg2.connect(**database_config) as conn:
        with conn.cursor() as cur:
            with open("scripts/recipes/sql/itemsModal.sql") as file:
                 sql = file.read().replace("%%site_name%%", site)
            cur.execute(sql, payload)
            rows = cur.fetchall()

            if rows and convert:
                rows = [postsqldb.tupleDictionaryFactory(cur.description, row) for row in rows]
            
            with open("scripts/recipes/sql/itemsModalCount.sql") as file:
                sql = file.read().replace("%%site_name%%", site)

            cur.execute(sql)
            count = cur.fetchone()[0]

            if rows and count:
                return rows, count
    return [], 0