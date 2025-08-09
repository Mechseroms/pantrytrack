# 3RD PARTY IMPORTS
import psycopg2

# APPLICATION IMPORTS
import config
from application import postsqldb

def requestNextReceiptID(site_name, conn=None):
    """gets the next id for receipts_id, currently returns a 8 digit number

    Args:
        site (str): site to get the next id for

    Returns:
        json: receipt_id, message, error keys
    """
    next_receipt_id = None
    self_conn = False
    sql = f"SELECT receipt_id FROM {site_name}_receipts ORDER BY id DESC LIMIT 1;"
    try:
        if not conn:
            database_config = config.config()
            conn = psycopg2.connect(**database_config)
            conn.autocommit = True
            self_conn = True

        with conn.cursor() as cur:
            cur.execute(sql)
            next_receipt_id = cur.fetchone()
            if next_receipt_id == None:
                next_receipt_id = "00000001"
            else:
                next_receipt_id = next_receipt_id[0]
                next_receipt_id = int(next_receipt_id.split("-")[1]) + 1
                y = str(next_receipt_id)
                len_str = len(y)
                x = "".join(["0" for _ in range(8 - len_str)])
                next_receipt_id = x + y
        
        if self_conn:
            conn.commit()
            conn.close()

        return next_receipt_id
    except (Exception, psycopg2.DatabaseError) as error:
        raise postsqldb.DatabaseError(error, payload=(), sql=sql)
    
def getItemsWithQOH(site, payload, convert=True, conn=None):
    recordset = []
    count = 0
    self_conn = False
    with open(f"application/receipts/sql/getItemsWithQOH.sql", "r+") as file:
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

def getLinkedItemByBarcode(site, payload, convert=True, conn=None):
        item = ()
        self_conn = False
        sql = f"SELECT * FROM {site}_itemlinks WHERE barcode=%s;"
        if convert:
            item = {}
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
                    item = postsqldb.tupleDictionaryFactory(cur.description, rows)
                if rows and not convert:
                    item = rows
            
            if self_conn:
                conn.close()
            
            return item
        except (Exception, psycopg2.DatabaseError) as error:
            raise postsqldb.DatabaseError(error, payload, sql)

def getItemAllByBarcode(site, payload, convert=True, conn=None):
        item = ()
        self_conn = False

        if not conn:
            database_config = config.config()
            conn = psycopg2.connect(**database_config)
            conn.autocommit = True
            self_conn = True

        if convert:
            item = {}

        linked_item = getLinkedItemByBarcode(site, (payload[0],), conn=conn)

        if len(linked_item) > 1:
            item = getItemAllByID(site, payload=(linked_item['link'], ), convert=convert, conn=conn)
            item['item_info']['uom_quantity'] = linked_item['conv_factor']
            
            if self_conn:
                conn.close()

            return item
        else:
            with open(f"application/receipts/sql/getItemAllByBarcode.sql", "r+") as file:
                getItemAllByBarcode_sql = file.read().replace("%%site_name%%", site)
            try:
                with conn.cursor() as cur:
                    cur.execute(getItemAllByBarcode_sql, payload)
                    rows = cur.fetchone()
                    if rows and convert:
                        item = postsqldb.tupleDictionaryFactory(cur.description, rows)
                    if rows and not convert:
                        item = rows

                if self_conn:
                    conn.close()

                return item
            except (Exception, psycopg2.DatabaseError) as error:
                raise postsqldb.DatabaseError(error, payload, getItemAllByBarcode_sql)

def getItemAllByUUID(site, payload, convert=True, conn=None):
        item = ()
        self_conn = False

        if not conn:
            database_config = config.config()
            conn = psycopg2.connect(**database_config)
            conn.autocommit = True
            self_conn = True

        if convert:
            item = {}

        
        with open(f"application/receipts/sql/getItemAllByUUID.sql", "r+") as file:
            getItemAllByUUID_sql = file.read().replace("%%site_name%%", site)
        try:
            with conn.cursor() as cur:
                cur.execute(getItemAllByUUID_sql, payload)
                rows = cur.fetchone()
                if rows and convert:
                    item = postsqldb.tupleDictionaryFactory(cur.description, rows)
                if rows and not convert:
                    item = rows

            if self_conn:
                conn.close()

            return item
        except (Exception, psycopg2.DatabaseError) as error:
            raise postsqldb.DatabaseError(error, payload, getItemAllByUUID_sql)

def getItemAllByID(site, payload, convert=True, conn=None):
    item = ()
    self_conn = False

    with open(f"application/receipts/sql/getItemAllByID.sql", "r+") as file:
        getItemAllByID_sql = file.read().replace("%%site_name%%", site)
    try:
        if not conn:
            database_config = config.config()
            conn = psycopg2.connect(**database_config)
            conn.autocommit = True
            self_conn = True

        with conn.cursor() as cur:
            cur.execute(getItemAllByID_sql, payload)
            rows = cur.fetchone()
            if rows and convert:
                item = postsqldb.tupleDictionaryFactory(cur.description, rows)
            if rows and not convert:
                item = rows
        
        if self_conn:
            conn.close()
        
        return item
    except (Exception, psycopg2.DatabaseError) as error:
        raise postsqldb.DatabaseError(error, payload, getItemAllByID_sql)

def getReceiptByID(site, payload, convert=True, conn=None):
    receipt = []
    self_conn = False
    with open(f"application/receipts/sql/getReceiptByID.sql", "r+") as file:
        sql = file.read().replace("%%site_name%%", site)
    try:
        if not conn:
            database_config = config.config()
            conn = psycopg2.connect(**database_config)
            conn.autocommit = True
            self_conn = True

        with conn.cursor() as cur:
            cur.execute(sql, payload)
            row = cur.fetchone()
            if row and convert:
                receipt = postsqldb.tupleDictionaryFactory(cur.description, row)
            if row and not convert:
                receipt = row

        if self_conn:
            conn.close()

        return receipt
    except (Exception, psycopg2.DatabaseError) as error:
        raise postsqldb.DatabaseError(error, payload, sql)

def paginateReceiptsTuples(site, payload, convert=True, conn=None):
    """payload=(limit, offset)"""
    receipts = []
    count = 0
    self_conn = False
    with open(f"application/receipts/sql/getReceipts.sql", "r+") as file:
        sql = file.read().replace("%%site_name%%", site)
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
                receipts = [postsqldb.tupleDictionaryFactory(cur.description, row) for row in rows]
            if rows and not convert:
                receipts = rows

            cur.execute(f"SELECT COUNT(*) FROM {site}_receipts;")
            count = cur.fetchone()[0]
        
        if self_conn:
            conn.commit()
            conn.close()

        return receipts, count

    except (Exception, psycopg2.DatabaseError) as error:
        raise postsqldb.DatabaseError(error, payload, sql)

def paginateVendorsTuples(site, payload, convert=True, conn=None):
        """payload (tuple): (limit, offset)"""
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
                conn.close()

            return recordset, count
        except Exception as error:
            raise postsqldb.DatabaseError(error, (), sql)

def paginateLinkedLists(site, payload, convert=True, conn=None):
        records = []
        count = 0
        self_conn = False
        sql = f"SELECT * FROM {site}_items WHERE row_type = 'list' LIMIT %s OFFSET %s;"
        sql_count = f"SELECT COUNT(*) FROM {site}_items WHERE row_type = 'list' LIMIT %s OFFSET %s;"
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
                    records = [postsqldb.tupleDictionaryFactory(cur.description, row) for row in rows]
                if rows and not convert:
                    records = rows

                cur.execute(sql_count, payload)
                count = cur.fetchone()[0]

            if self_conn:
                conn.close()

            return records, count
        except (Exception, psycopg2.DatabaseError) as error:
            raise postsqldb.DatabaseError(error, payload, sql)

def selectItemLocationsTuple(site_name, payload, convert=True, conn=None):
    """payload (tuple): [item_id, location_id]"""
    item_locations = ()
    self_conn = False
    select_item_location_sql = f"SELECT * FROM {site_name}_item_locations WHERE part_id = %s AND location_id = %s;"
    try:
        if not conn:
            database_config = config.config()
            conn = psycopg2.connect(**database_config)
            conn.autocommit = True
            self_conn = True

        with conn.cursor() as cur:
            cur.execute(select_item_location_sql, payload)
            rows = cur.fetchone()
            if rows and convert:
                item_locations = postsqldb.tupleDictionaryFactory(cur.description, rows)
            elif rows and not convert:
                item_locations = rows

        if self_conn:
            conn.close()

        return item_locations
    except Exception as error:
        return error

def selectLocationsTuple(site, payload, convert=True, conn=None):
    selected = ()
    self_conn = False
    sql = f"SELECT * FROM {site}_locations WHERE id=%s;"
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
                selected = postsqldb.tupleDictionaryFactory(cur.description, rows)
            elif rows and not convert:
                selected = rows

        if self_conn:
            conn.close()

        return selected

    except Exception as error:
        raise postsqldb.DatabaseError(error, payload, sql)

def selectReceiptsTuple(site, payload, convert=True, conn=None):
    selected = ()
    self_conn = False
    sql = f"SELECT * FROM {site}_receipts WHERE id=%s;"

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
                selected = postsqldb.tupleDictionaryFactory(cur.description, rows)
            if rows and not convert:
                selected = rows
        
        if self_conn:
            conn.close()
        
        return selected
    except (Exception, psycopg2.DatabaseError) as error:
        raise postsqldb.DatabaseError(error, payload, sql)

def selectReceiptItemsTuple(site, payload, convert=True, conn=None):
    selected = ()
    self_conn = False
    sql = f"SELECT * FROM {site}_receipt_items WHERE id=%s;"

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
                selected = postsqldb.tupleDictionaryFactory(cur.description, rows)
            if rows and not convert:
                selected = rows
        
        if self_conn:
            conn.close()
        
        return selected
    except (Exception, psycopg2.DatabaseError) as error:
        raise postsqldb.DatabaseError(error, payload, sql)

def deleteReceiptItemsTuple(site, payload, convert=True, conn=None):
    deleted = ()
    self_conn = False
    sql = f"WITH deleted_rows AS (DELETE FROM {site}_receipt_items WHERE id IN ({','.join(['%s'] * len(payload))}) RETURNING *) SELECT * FROM deleted_rows;"
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

def insertTransactionsTuple(site, payload, convert=True, conn=None):
    """
    payload (tuple): (timestamp[timestamp], logistics_info_id[int], barcode[str], name[str], 
    transaction_type[str], quantity[float], description[str], user_id[int], data[jsonb])
    """
    transaction = ()
    self_conn = False
    with open(f"application/receipts/sql/insertTransactionsTuple.sql", "r+") as file:
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
                transaction = postsqldb.tupleDictionaryFactory(cur.description, rows)
            elif rows and not convert:
                transaction = rows

        if self_conn:
            conn.commit()
            conn.close()
        
        return transaction

    except Exception as error:
        raise postsqldb.DatabaseError(error, payload, sql)

def insertItemLinksTuple(site, payload, convert=True, conn=None):
    """payload (tuple): (barcode[str], link[int], data[jsonb], conv_factor[float]) """
    link = ()
    self_conn = False
    with open(f"application/receipts/sql/insertItemLinksTuple.sql", "r+") as file:
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
                link = postsqldb.tupleDictionaryFactory(cur.description, rows)
            elif rows and not convert:
                link = rows
        
        if self_conn:
            conn.commit()
            conn.close()

        return link
    except Exception as error:
        raise postsqldb.DatabaseError(error, payload, sql)
    
def insertCostLayersTuple(site, payload, convert=True, conn=None):
    """payload (tuple): (aquisition_date[timestamp], quantity[float], cost[float], currency_type[str], expires[timestamp/None], vendor[int])"""
    cost_layer = ()
    self_conn = False

    with open(f"application/receipts/sql/insertCostLayersTuple.sql", "r+") as file:
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
                cost_layer = postsqldb.tupleDictionaryFactory(cur.description, rows)
            elif rows and not convert:
                cost_layer = rows

        if self_conn:
            conn.commit()
            conn.close()
        
        return cost_layer

    except Exception as error:
        raise postsqldb.DatabaseError(error, payload, sql)

def insertReceiptItemsTuple(site, payload, convert=True, conn=None):
    receipt_item = ()
    self_conn = False
    with open(f"application/receipts/sql/insertReceiptItemsTuple.sql", "r+") as file:
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
                receipt_item = postsqldb.tupleDictionaryFactory(cur.description, rows)
            elif rows and not convert:
                receipt_item = rows
        
        if self_conn:
            conn.commit()
            conn.close()
        
        return receipt_item
    except Exception as error:
        raise postsqldb.DatabaseError(error, payload, sql)

def insertReceiptsTuple(site, payload, convert=True, conn=None):
    receipt = ()
    self_conn = False
    with open(f"application/receipts/sql/insertReceiptsTuple.sql", "r+") as file:
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
                receipt = postsqldb.tupleDictionaryFactory(cur.description, rows)
            elif rows and not convert:
                receipt = rows
        
        if self_conn:
            conn.commit()
            conn.close()
        
        return receipt
    except Exception as error:
        raise postsqldb.DatabaseError(error, payload, sql)

def insertBarcodesTuple(site: str, payload: list, convert=True, conn=None):
    """ payload (tuple): (barcode, item_uuid, in_exchange, out_exchange, descriptor) """
    record = ()
    self_conn = False
    
    sql = f"INSERT INTO {site}_barcodes (barcode, item_uuid, in_exchange, out_exchange, descriptor) VALUES (%s, %s, %s, %s, %s) RETURNING *;"

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
            conn.commit()
            conn.close()

        return record
    
    except Exception as error:
        raise postsqldb.DatabaseError(error, payload, sql)   

def updateItemsTuple(site, payload, convert=True, conn=None):
    """payload (dict): {'id': row_id, 'update': {... column_to_update: value_to_update_to...}}"""
    updated = ()
    self_conn = False
    set_clause, values = postsqldb.updateStringFactory(payload['update'])
    values.append(payload['id'])
    sql = f"UPDATE {site}_items SET {set_clause} WHERE id=%s RETURNING *;"
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

def updateItemLocation(site, payload, convert=True, conn=None):
    item_location = ()
    self_conn = False
    with open(f"application/receipts/sql/updateItemLocation.sql", "r+") as file:
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
                item_location = postsqldb.tupleDictionaryFactory(cur.description, rows)
            elif rows and not convert:
                item_location = rows
        
        if self_conn:
            conn.commit()
            conn.close()

        return item_location
    except Exception as error:
        return error

def updateReceiptsTuple(site, payload, convert=True, conn=None):
        """payload (dict): {'id': row_id, 'update': {... column_to_update: value_to_update_to...}}"""
        updated = ()
        self_conn = False
        set_clause, values = postsqldb.updateStringFactory(payload['update'])
        values.append(payload['id'])
        sql = f"UPDATE {site}_receipts SET {set_clause} WHERE id=%s RETURNING *;"
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
        
def updateReceiptItemsTuple(site, payload, convert=True, conn=None):
    """_summary_

    Args:
        conn (_T_connector@connect): Postgresql Connector
        site (str):
        payload (dict): {'id': row_id, 'update': {... column_to_update: value_to_update_to...}}
        convert (bool, optional): determines if to return tuple as dictionary. Defaults to True.

    Raises:
        DatabaseError:

    Returns:
        tuple or dict: updated tuple
    """
    updated = ()
    self_conn = False

    set_clause, values = postsqldb.updateStringFactory(payload['update'])
    values.append(payload['id'])
    sql = f"UPDATE {site}_receipt_items SET {set_clause} WHERE id=%s RETURNING *;"
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