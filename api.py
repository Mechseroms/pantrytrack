from flask import Blueprint, request, render_template, redirect, session, url_for, send_file, jsonify, Response
import psycopg2, math, json, datetime, main, copy
from config import config, sites_config

database_api= Blueprint('database_api', __name__)

@database_api.route("/changeSite")
def changeSite():
    site = request.args.get('site', 'main')
    session['selected_site'] = site
    return jsonify({'status': 'SUCCESS'})

def paginate_with_params(cur, limit, offset, params):
    sql = f"SELECT * FROM main_items LEFT JOIN main_logistics_info ON main_items.logistics_info_id = main_logistics_info.id"
    count = f"SELECT COUNT(*) FROM main_items LEFT JOIN main_logistics_info ON main_items.logistics_info_id = main_logistics_info.id"
    # WHERE search_string LIKE '%{search_string}%'
    strings = []
    count_strings = []
    if params['search_string'] != "":
        s = params['search_string']
        strings.append(f" search_string LIKE '%{s}%'")
        count_strings.append(f" search_string LIKE '%{s}%'")
    
    if params['view'] == 1:
        s = params['view']
        strings.append(f" main_logistics_info.quantity_on_hand <> 0.00")
        count_strings.append(f" main_logistics_info.quantity_on_hand <> 0.00")


    #   LIMIT {limit} OFFSET {offset};"

    if len(strings) > 0:
        sql = f"{sql} WHERE{" AND".join(strings)}"

    if len(count_strings) > 0:
        count = f"{count} WHERE{" AND".join(count_strings)}"

    sql = f"{sql} ORDER BY main_logistics_info.quantity_on_hand LIMIT {limit} OFFSET {offset};"
    count = f"{count};"
    print(count)
    print(sql)
    cur.execute(sql)
    pantry_inventory = cur.fetchall()
    cur.execute(count)
    count = cur.fetchone()[0]
    return pantry_inventory, count

def paginate_default(cur, limit, offset):
    sql = f"SELECT * FROM main_items LEFT JOIN main_logistics_info ON main_items.logistics_info_id = main_logistics_info.id LIMIT %s OFFSET %s;"
    cur.execute(sql, (limit, offset))
    pantry_inventory = cur.fetchall()
    cur.execute("SELECT COUNT(*) FROM main_items;")
    count = cur.fetchone()[0]
    return pantry_inventory, count

def paginate_with_params_groups(cur, limit, offset, params):
    sql = f"SELECT * FROM main_groups"
    count = f"SELECT COUNT(*) FROM main_groups"
    # WHERE search_string LIKE '%{search_string}%'
    strings = []
    count_strings = []
    if params['search_string'] != "":
        s = params['search_string']
        strings.append(f" search_string LIKE '%{s}%'")
        count_strings.append(f" search_string LIKE '%{s}%'")
    

    #   LIMIT {limit} OFFSET {offset};"

    if len(strings) > 0:
        sql = f"{sql} WHERE{" AND".join(strings)}"

    if len(count_strings) > 0:
        count = f"{count} WHERE{" AND".join(count_strings)}"

    sql = f"{sql} ORDER BY main_logistics_info.quantity_on_hand LIMIT {limit} OFFSET {offset};"
    count = f"{count};"
    print(count)
    print(sql)
    cur.execute(sql)
    pantry_inventory = cur.fetchall()
    cur.execute(count)
    count = cur.fetchone()[0]
    return pantry_inventory, count

@database_api.route("/getGroups")
def paginate_groups():
    page = int(request.args.get('page', 1))
    limit = int(request.args.get('limit', 10))
    site_name = session['selected_site']    
    offset = (page - 1) * limit

    groups = []
    count = 0
    
    database_config = config()
    with psycopg2.connect(**database_config) as conn:
        try:
            with conn.cursor() as cur:
                sql = f"SELECT * FROM {site_name}_groups LIMIT %s OFFSET %s;"
                count = f"SELECT COUNT(*) FROM {site_name}_groups"

                cur.execute(sql, (limit, offset))
                groups = cur.fetchall()
                cur.execute(count)
                count = cur.fetchone()[0]

            
                sql_item = f"SELECT {site_name}_items.barcode, {site_name}_items.item_name, {site_name}_logistics_info.quantity_on_hand FROM {site_name}_items LEFT JOIN {site_name}_logistics_info ON {site_name}_items.logistics_info_id = {site_name}_logistics_info.id WHERE {site_name}_items.id = %s; "
                new_groups = []
                for group in groups:
                    qty = 0
                    group = list(group)
                    items = []
                    print(group[3])
                    for item_id in group[3]:
                        cur.execute(sql_item, (item_id,))
                        item_row = cur.fetchone()
                        qty += float(item_row[2])
                        items.append(item_row)
                    group[3] = items
                    group.append(qty)
                    new_groups.append(group)
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)

    return jsonify({'groups': new_groups, "end": math.ceil(count/limit)})

@database_api.route("/getItems")
def pagninate_items():
    page = int(request.args.get('page', 1))
    limit = int(request.args.get('limit', 10))
    search_string = str(request.args.get('search_text', ""))
    sort_order = int(request.args.get('sort_order', 1))
    view = int(request.args.get('view', 0))
    site_name = session['selected_site']

    offset = (page - 1) * limit

    pantry_inventory = []
    count = 0

    database_config = config()
    with psycopg2.connect(**database_config) as conn:
        try:
            with conn.cursor() as cur:
                sql = f"SELECT * FROM {site_name}_items LEFT JOIN {site_name}_logistics_info ON {site_name}_items.logistics_info_id = {site_name}_logistics_info.id LIMIT {limit} OFFSET {offset};"
                count = f"SELECT COUNT(*) FROM {site_name}_items LEFT JOIN {site_name}_logistics_info ON {site_name}_items.logistics_info_id = {site_name}_logistics_info.id;"
                cur.execute(sql)
                pantry_inventory = cur.fetchall()
                cur.execute(count)
                count = cur.fetchone()[0]
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)

    return jsonify({'items': pantry_inventory, "end": math.ceil(count/limit)})

@database_api.route("/getTransactions")
def pagninate_transactions():
    item_id = request.args.get('id', 1)
    page = int(request.args.get('page', 1))
    limit = int(request.args.get('limit', 10))
    site_name = session['selected_site']

    offset = (page - 1) * limit
    count = 0
    transactions = []

    database_config = config()
    with psycopg2.connect(**database_config) as conn:
        try:
            with conn.cursor() as cur:

                cur.execute(f"SELECT logistics_info_id FROM {site_name}_items WHERE id={item_id};")
                logistics_info_id = cur.fetchone()[0]
                sql = f"SELECT * FROM {site_name}_transactions WHERE logistics_info_id={logistics_info_id} LIMIT {limit} OFFSET {offset};"
                count = f"SELECT COUNT(*) FROM {site_name}_transactions WHERE logistics_info_id={logistics_info_id};"
                cur.execute(sql)
                transactions = cur.fetchall()
                cur.execute(count)
                count = cur.fetchone()[0]
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)

    return jsonify({'transactions': transactions, "end": math.ceil(count/limit)})

@database_api.route("/getLocations")
def get_locations():
    zone_name = request.args.get('zone', 1)
    database_config = config()
    site_name = session['selected_site']
    locations = []
    with psycopg2.connect(**database_config) as conn:
        try:
            with conn.cursor() as cur:
                sql = f"SELECT id FROM {site_name}_zones WHERE name=%s;"
                cur.execute(sql, (zone_name,))
                zone_id = cur.fetchone()[0]

                sqltwo = f"SELECT name FROM {site_name}_locations WHERE zone_id=%s;"
                cur.execute(sqltwo, (zone_id, ))
                locations = [location[0] for location in cur.fetchall()]            
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)
    
    print(locations)
    return jsonify(locations=locations)

@database_api.route("/getZones")
def get_zones():
    database_config = config()
    site_name = session['selected_site']
    zones = []
    with psycopg2.connect(**database_config) as conn:
        try:
            with conn.cursor() as cur:
                sql = f"SELECT name FROM {site_name}_zones;"
                cur.execute(sql)
                zones = [zone[0] for zone in cur.fetchall()]
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)
    print(zones)
    return jsonify(zones=zones)

@database_api.route("/getItem")
def get_item():
    id = int(request.args.get('id', 1))
    database_config = config()
    site_name = session['selected_site']
    sites = sites_config()


    item = []
    with psycopg2.connect(**database_config) as conn:
        try:
            with conn.cursor() as cur:
                with open(f"sites/{site_name}/sql/unique/select_item_all.sql", "r+") as file:
                    sql = file.read()
                cur.execute(sql, (id, ))
                item = list(cur.fetchone())
                SQL_groups = f"SELECT * FROM {site_name}_groups WHERE included_items @> ARRAY[%s];"
                cur.execute(SQL_groups, (item[0], ))
                item[25] = list(cur.fetchall())
                SQL_shopping_lists = f"SELECT * FROM {site_name}_shopping_lists WHERE pantry_items @> ARRAY[%s];"
                cur.execute(SQL_shopping_lists, (item[0], ))
                item[23] = list(cur.fetchall())
                print(item)
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)

    return jsonify(item=item)

@database_api.route("/addItem")
def addItem():
    barcode = str(request.args.get('barcode', ""))
    name = str(request.args.get('item_name', ""))
    description = str(request.args.get('item_description', ""))
    item_type = str(request.args.get('item_type', ""))
    subtype = str(request.args.get('sub_type', ""))
    site_name = session['selected_site']
    state = "FAILED"

    payload = copy.deepcopy(main.payload_food_item)

    defaults = config(filename=f"sites/{site_name}/site.ini", section="defaults")
    uuid = f"{defaults["default_zone"]}@{defaults["default_primary_location"]}"
    name = name.replace("'", "@&apostraphe&")
    payload["logistics_info"]["primary_location"] = uuid
    payload["logistics_info"]["auto_issue_location"] = uuid

    tags = main.lst2pgarr([])
    links = json.dumps({})

    database_config = config()
    with psycopg2.connect(**database_config) as conn:
        logistics_info_id = main.create_logistics_info(conn, site_name, barcode, payload["logistics_info"])
        if not logistics_info_id:
            return jsonify({'state': str(logistics_info_id)})
        item_info_id = main.create_item_info(conn, site_name, barcode, payload["item_info"])
        if not item_info_id:
            return jsonify({'state': str(item_info_id)})
        food_info_id = main.create_food_info(conn, site_name, payload["food_info"])
        if not food_info_id:
            return jsonify({'state': str(food_info_id)})

        sqltwo = f"INSERT INTO {site_name}_items(barcode, item_name, tags, links, item_info_id, logistics_info_id, food_info_id, row_type, item_type, search_string) VALUES('{barcode}', '{name}', '{tags}', '{links}', {item_info_id}, {logistics_info_id}, {food_info_id}, 'single', 'FOOD', '{barcode}%{name}') RETURNING *;"
        row = None
        try:
            with conn.cursor() as cur:
                cur.execute(sqltwo)
                rows = cur.fetchone()
                if rows:
                    row = rows[:]
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)
            conn.rollback()
            return jsonify({'state': str(error)})


        conn.commit()


    main.add_transaction(site_name, barcode, qty=0, user_id=1, description="Added Item to System!")

    

    return jsonify({'state': "SUCCESS"})

@database_api.route("/updateItem", methods=['POST'])
def updateItem():
    def transformValues(values):
        v = []
        for value in values:
            if isinstance(value, dict):
                v.append(json.dumps(value))
            elif isinstance(value, list):
                v.append(main.lst2pgarr(value))
            else:
                v.append(value)
        return v
    
    def manufactureSQL(keys, item_id, table):
        if len(keys) > 1:
            x = f"({', '.join(keys)})"
            y = f"({', '.join(['%s' for _ in keys])})"
        else:
            x = f"{', '.join(keys)}"
            y = f"{', '.join(['%s' for _ in keys])}"

        sql = f"UPDATE {table} SET {x} = {y} WHERE id={item_id};"
        return sql
    
    if request.method == "POST":
        site_name = session['selected_site']
        
        item_id = request.get_json()['id']
        logistics_info_id = request.get_json()['logistics_info_id']
        food_info_id = request.get_json()['food_info_id']
        item_info_id = request.get_json()['item_info_id']
        updated = request.get_json()['updated']
        item_info = request.get_json()['item_info']
        food_info = request.get_json()['food_info']
        logistics_info = request.get_json()['logistics_info']
        
        database_config = config()
        
        with psycopg2.connect(**database_config) as conn:
            try:
                with conn.cursor() as cur:
                    if updated != {}:                
                        values = transformValues(updated.values())
                        sql = manufactureSQL(updated.keys(), item_id, f"{site_name}_items")
                        cur.execute(sql, values)
                    if item_info != {}:
                        values = transformValues(item_info.values())
                        sql = manufactureSQL(item_info.keys(), item_info_id, f"{site_name}_item_info")
                        cur.execute(sql, values)
                    if food_info != {}:
                        values = transformValues(food_info.values())
                        sql = manufactureSQL(food_info.keys(), food_info_id, f"{site_name}_food_info")
                        cur.execute(sql, values)
                    if logistics_info != {}:
                        values = transformValues(logistics_info.values())
                        sql = manufactureSQL(logistics_info.keys(), logistics_info_id, f"{site_name}_logistics_info")
                        cur.execute(sql, values)

                    cur.execute(f"SELECT barcode FROM {site_name}_items WHERE id={item_id};")
                    barcode = cur.fetchone()[0]
                    print(barcode)
                    main.add_transaction(site_name, barcode, 0, 1, "SYSTEM", "Item data was update!", data=request.get_json())
            except (Exception, psycopg2.DatabaseError) as error:
                print(error)
                conn.rollback()
        
        return jsonify({"state": "SUCCESS"})

    return jsonify({"status": "FAILED"})

@database_api.route("/addGroup")
def addGroup():
    name = str(request.args.get('name', ""))
    description = str(request.args.get('description', ""))
    group_type = str(request.args.get('type', ""))
    site_name = session['selected_site']
    state = "FAILED"

    database_config = config()
    with psycopg2.connect(**database_config) as conn:
            try:
                with conn.cursor() as cur:
                    sql = f"INSERT INTO {site_name}_groups (name, description, included_items, group_type) VALUES (%s, %s, %s, %s);"
                    cur.execute(sql, (name, description, json.dumps({}), group_type))
                    state = "SUCCESS"
                    conn.commit()
            except (Exception, psycopg2.DatabaseError) as error:
                print(error)
                conn.rollback()


    return jsonify({'state': state})

@database_api.route("/getGroup")
def get_group():
    id = int(request.args.get('id', 1))
    database_config = config()
    site_name = session['selected_site']

    group = []
    with psycopg2.connect(**database_config) as conn:
        try:
            with conn.cursor() as cur:
                sql = f"SELECT * FROM {site_name}_groups WHERE id=%s;"
                cur.execute(sql, (id, ))
                group = list(cur.fetchone())

                sql_item = f"SELECT {site_name}_items.id, {site_name}_items.barcode, {site_name}_items.item_name, {site_name}_logistics_info.quantity_on_hand FROM {site_name}_items LEFT JOIN {site_name}_logistics_info ON {site_name}_items.logistics_info_id = {site_name}_logistics_info.id WHERE {site_name}_items.id = %s;"                
                qty = 0
                group = list(group)
                items = []
                print(group[3])
                for item_id in group[3]:
                    cur.execute(sql_item, (item_id,))
                    item_row = cur.fetchone()
                    qty += float(item_row[3])
                    items.append(item_row)
                group[3] = items
                group.append(qty)
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)

    return jsonify(group=group)

@database_api.route("/updateGroup", methods=["POST"])
def update_group():
    if request.method == "POST":
        site_name = session['selected_site']
        group_id = request.get_json()['id']
        items = request.get_json()['items']
        name = request.get_json()['name']
        description = request.get_json()['description']
        group_type = request.get_json()['group_type']
        data = (name, description, items, group_type, group_id)
        database_config = config()
        with psycopg2.connect(**database_config) as conn:
            try:
                with conn.cursor() as cur:
                    # Start by updating the group -> included items with the up to date list
                    sql = f"UPDATE {site_name}_groups SET name = %s, description = %s, included_items = %s, group_type = %s WHERE id=%s;"
                    cur.execute(sql, data)

                    update_item_sql = f"UPDATE {site_name}_item_info SET groups = %s WHERE id = %s;"
                    select_item_sql = f"SELECT {site_name}_item_info.id, {site_name}_item_info.groups FROM {site_name}_items LEFT JOIN {site_name}_item_info ON {site_name}_items.item_info_id = {site_name}_item_info.id WHERE {site_name}_items.id = %s;"
                    # Now we will fetch each item row one by one and check if the group id is already inside of its groups array
                    for item_id in items:
                        cur.execute(select_item_sql, (item_id, ))
                        item = cur.fetchone()
                        print(item)
                        item_groups: set = set(item[1])
                        # Condition check, adds it if it doesnt exist.
                        if group_id not in item_groups:
                            item_groups.add(group_id)
                            cur.execute(update_item_sql, (list(item_groups), item[0]))

                    # Now we fetch all items that have the group id in its groups array
                    fetch_items_with_group = f"SELECT {site_name}_items.id, groups, {site_name}_item_info.id FROM {site_name}_item_info LEFT JOIN {site_name}_items ON {site_name}_items.item_info_id = {site_name}_item_info.id WHERE groups @> ARRAY[%s];"
                    cur.execute(fetch_items_with_group, (group_id, ))
                    group_items = cur.fetchall()
                    print(items)
                    # We will then check each item id against the groups new included_items list to see if the item should be in there
                    for item_id, group, info_id in group_items:
                        # If it is not we remove the group form the items list and update the item
                        if item_id not in items:
                            groups: list = list(group)
                            groups.remove(group_id)
                            cur.execute(update_item_sql, (list(groups), info_id))

                    conn.commit()
            except (Exception, psycopg2.DatabaseError) as error:
                print(error)
                conn.rollback()
        
        return jsonify({"state": "SUCCESS"})
    return jsonify({"state": "FAILED"})

@database_api.route("/addList")
def addList():
    name = str(request.args.get('name', ""))
    description = str(request.args.get('description', ""))
    list_type = str(request.args.get('type', ""))
    site_name = session['selected_site']

    print(name, description, list_type)
    state = "FAILED"

    #if name or description or group_type == "":
      #  print("this is empty")
       # return jsonify({'state': state})
    timestamp = datetime.datetime.now()
    data = (name, description, [], json.dumps({}), [], [], 0, timestamp, list_type)
    database_config = config()
    with psycopg2.connect(**database_config) as conn:
            try:
                with conn.cursor() as cur:
                    sql = f"INSERT INTO {site_name}_shopping_lists (name, description, pantry_items, custom_items, recipes, groups, author, creation_date, type) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s);"
                    cur.execute(sql, data)
                    state = "SUCCESS"
                    conn.commit()
            except (Exception, psycopg2.DatabaseError) as error:
                print(error)
                conn.rollback()


    return jsonify({'state': state})

@database_api.route("/getLists")
def paginate_lists():
    page = int(request.args.get('page', 1))
    limit = int(request.args.get('limit', 10))
    site_name = session['selected_site']
    
    offset = (page - 1) * limit

    lists = []
    count = 0
    
    database_config = config()
    with psycopg2.connect(**database_config) as conn:
        try:
            with conn.cursor() as cur:
                sql = f"SELECT * FROM {site_name}_shopping_lists LIMIT %s OFFSET %s;"
                count = f"SELECT COUNT(*) FROM {site_name}_shopping_lists;"

                cur.execute(sql, (limit, offset))
                temp_lists = list(cur.fetchall())
                cur.execute(count)
                count = cur.fetchone()[0]

                for shopping_list in temp_lists:
                    shopping_list: list = list(shopping_list)
                    pantry_items = shopping_list[3]
                    custom_items = shopping_list[4]
                    list_length = len(custom_items)

                    if shopping_list[10] == 'calculated':
                        item_sql = f"SELECT COUNT(*) FROM {site_name}_items LEFT JOIN {site_name}_logistics_info ON {site_name}_items.logistics_info_id = {site_name}_logistics_info.id LEFT JOIN {site_name}n_item_info ON {site_name}_items.item_info_id = {site_name}_item_info.id LEFT JOIN {site_name}_food_info ON {site_name}_items.food_info_id = {site_name}_food_info.id WHERE {site_name}_logistics_info.quantity_on_hand < {site_name}_item_info.safety_stock AND shopping_lists @> ARRAY[%s];"
                        cur.execute(item_sql, (shopping_list[0], ))
                        list_length += cur.fetchone()[0]
                    else:
                        list_length += len(pantry_items)

                    shopping_list.append(list_length)
                    lists.append(shopping_list)
            
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)

    return jsonify({'lists': lists, 'end': math.ceil(count/limit)})

@database_api.route("/getListView")
def get_list_view():
    id = int(request.args.get('id', 1))
    site_name = session['selected_site']
    shopping_list = []
    database_config = config()
    with psycopg2.connect(**database_config) as conn:
        try:
            with conn.cursor() as cur:
                sql = f"SELECT * FROM {site_name}_shopping_lists WHERE id=%s;"
                cur.execute(sql, (id, ))
                shopping_list = list(cur.fetchone())

                if shopping_list[10] == "calculated":
                    itemSQL = f"SELECT {site_name}_items.id, {site_name}_items.barcode, {site_name}_items.item_name, {site_name}_items.links, {site_name}_logistics_info.quantity_on_hand, {site_name}_item_info.safety_stock, {site_name}_item_info.uom FROM {site_name}_items LEFT JOIN {site_name}_logistics_info ON {site_name}_items.logistics_info_id = {site_name}_logistics_info.id LEFT JOIN {site_name}_item_info ON {site_name}_items.item_info_id = {site_name}_item_info.id LEFT JOIN {site_name}_food_info ON {site_name}_items.food_info_id = {site_name}_food_info.id WHERE {site_name}_logistics_info.quantity_on_hand < {site_name}_item_info.safety_stock AND shopping_lists @> ARRAY[%s];"
                else:
                    itemSQL = f"SELECT {site_name}_items.id, {site_name}_items.barcode, {site_name}_items.item_name, {site_name}_items.links, {site_name}_logistics_info.quantity_on_hand, {site_name}_item_info.safety_stock, {site_name}_item_info.uom FROM {site_name}_items LEFT JOIN {site_name}_logistics_info ON {site_name}_items.logistics_info_id = {site_name}_logistics_info.id LEFT JOIN {site_name}_item_info ON {site_name}_items.item_info_id = {site_name}_item_info.id LEFT JOIN {site_name}_food_info ON {site_name}_items.food_info_id = {site_name}_food_info.id WHERE shopping_lists @> ARRAY[%s];"

                cur.execute(itemSQL, (id, ))
                shopping_list[3] = list(cur.fetchall())
                print(shopping_list)

        except (Exception, psycopg2.DatabaseError) as error:
            print(error)

    return jsonify(shopping_list=shopping_list)

@database_api.route("/getList")
def get_list():
    id = int(request.args.get('id', 1))
    database_config = config()
    site_name = session['selected_site']
    shopping_list = []
    with psycopg2.connect(**database_config) as conn:
        try:
            with conn.cursor() as cur:
                sql = f"SELECT * FROM {site_name}_shopping_lists WHERE id=%s;"
                cur.execute(sql, (id, ))
                shopping_list = list(cur.fetchone())
                itemSQL = f"SELECT {site_name}_items.id, {site_name}_items.barcode, {site_name}_items.item_name, {site_name}_items.links, {site_name}_item_info.uom FROM {site_name}_items LEFT JOIN {site_name}_item_info ON {site_name}_items.item_info_id = {site_name}_item_info.id WHERE {site_name}_item_info.shopping_lists @> ARRAY[%s];"
                cur.execute(itemSQL, (id, ))
                shopping_list[3] = list(cur.fetchall())
                print(shopping_list)
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)

    return jsonify(shopping_list=shopping_list)

@database_api.route("/updateList", methods=["POST"])
def update_list():
    if request.method == "POST":
        site_name = session['selected_site']
        list_id = request.get_json()['id']
        items = request.get_json()['items']
        print(items)
        custom_items = request.get_json()['custom']
        name = request.get_json()['name']
        description = request.get_json()['description']
        list_type = request.get_json()['list_type']
        quantities = request.get_json()['quantities']
        data = (name, description, items, json.dumps(custom_items), list_type, json.dumps(quantities), list_id)
        database_config = config()
        with psycopg2.connect(**database_config) as conn:
            try:
                with conn.cursor() as cur:
                    # Start by updating the group -> included items with the up to date list
                    sql = f"UPDATE {site_name}_shopping_lists SET name = %s, description = %s, pantry_items = %s, custom_items = %s, type = %s, quantities = %s WHERE id=%s;"
                    cur.execute(sql, data)

                    update_item_sql = f"UPDATE {site_name}_item_info SET shopping_lists = %s WHERE id = %s;"
                    select_item_sql = f"SELECT {site_name}_item_info.id, {site_name}_item_info.shopping_lists FROM {site_name}_items LEFT JOIN {site_name}_item_info ON {site_name}_items.item_info_id = {site_name}_item_info.id WHERE {site_name}_items.id = %s;"
                    # Now we will fetch each item row one by one and check if the group id is already inside of its groups array
                    for item_id in items:
                        cur.execute(select_item_sql, (item_id, ))
                        item = cur.fetchone()
                        print(item)
                        shopping_lists: set = set(item[1])
                        # Condition check, adds it if it doesnt exist.
                        if list_id not in shopping_lists:
                            shopping_lists.add(list_id)
                            cur.execute(update_item_sql, (list(shopping_lists), item[0]))

                    # Now we fetch all items that have the group id in its groups array
                    fetch_items_with_list = f"SELECT {site_name}_items.id, {site_name}_item_info.shopping_lists, {site_name}_item_info.id FROM {site_name}_item_info LEFT JOIN {site_name}_items ON {site_name}_items.item_info_id = {site_name}_item_info.id WHERE {site_name}_item_info.shopping_lists @> ARRAY[%s];"
                    cur.execute(fetch_items_with_list, (list_id, ))
                    list_items = cur.fetchall()
                    print(items)
                    # We will then check each item id against the groups new included_items list to see if the item should be in there
                    for item_id, shopping_list, info_id in list_items:
                        # If it is not we remove the group form the items list and update the item
                        if item_id not in items:
                            shopping_lists: list = list(shopping_list)
                            shopping_lists.remove(list_id)
                            cur.execute(update_item_sql, (list(shopping_lists), info_id))

                    conn.commit()
            except (Exception, psycopg2.DatabaseError) as error:
                print(error)
                conn.rollback()
        
        return jsonify({"state": "SUCCESS"})
    return jsonify({"state": "FAILED"})