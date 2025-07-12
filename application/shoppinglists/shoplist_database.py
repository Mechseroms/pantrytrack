
import psycopg2

import config
from application import postsqldb

def getShoppingListItem(site, payload, convert=True, conn=None):
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
        self_conn = False
        with open('application/shoppinglists/sql/selectShoppingListItem.sql', 'r') as file:
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
                    record = postsqldb.tupleDictionaryFactory(cur.description, rows)
                elif rows and not convert:
                    record = rows
            
            if self_conn:
                conn.close()

            return record
        except Exception as error:
            raise postsqldb.DatabaseError(error, payload, sql)


def getItemsWithQOH(site, payload, convert=True, conn=None):
    recordset = []
    count = 0
    self_conn = False

    with open(f"application/shoppinglists/sql/getItemsWithQOH.sql", "r+") as file:
        sql = file.read().replace("%%site_name%%", site).replace("%%sort_order%%", payload[3])

    payload = list(payload)
    payload.pop(3)
    try:

        if not conn:
            database_config = config.config()
            conn = psycopg2.connect(**database_config)
            conn.autocommit = True
            self_conn = True

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

        if self_conn:
            conn.close()

        return recordset, count

    except Exception as error:
        raise postsqldb.DatabaseError(error, payload, sql)

def deleteShoppingListItemsTuple(site_name, payload, convert=True, conn=None):
    deleted = ()
    self_conn = False
    sql = f"WITH deleted_rows AS (DELETE FROM {site_name}_shopping_list_items WHERE id IN ({','.join(['%s'] * len(payload))}) RETURNING *) SELECT * FROM deleted_rows;"
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

def insertShoppingListItemsTuple(site, payload, convert=True, conn=None):
    shopping_list_item = ()
    self_conn = False
    with open(f"application/shoppinglists/sql/insertShoppingListItemsTuple.sql", "r+") as file:
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
                shopping_list_item = postsqldb.tupleDictionaryFactory(cur.description, rows)
            elif rows and not convert:
                shopping_list_item = rows
        
        if self_conn:
            conn.commit()
            conn.close()

        return shopping_list_item
        
    except Exception as error:
        raise postsqldb.DatabaseError(error, payload, sql)
