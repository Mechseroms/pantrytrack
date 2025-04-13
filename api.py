from flask import Blueprint, request, render_template, redirect, session, url_for, send_file, jsonify, Response
import psycopg2, math, json, datetime, main, copy, requests, process, database
from config import config, sites_config
from main import unfoldCostLayers

database_api= Blueprint('database_api', __name__)

@database_api.route("/changeSite", methods=["POST"])
def changeSite():
    if request.method == "POST":
        site = request.json['site']
    session['selected_site'] = site
    return jsonify({'error': False, 'message': 'Site Changed!'})


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
                        item_row = list(cur.fetchone())
                        cur.execute(f"SELECT quantity_on_hand FROM {site_name}_item_locations WHERE part_id=%s;", (item_id, ))
                        item_locations = cur.fetchall()[0]
                        qty += float(sum(item_locations))
                        item_row[2] = sum(item_locations)
                        items.append(item_row)
                    group[3] = items
                    group.append(qty)
                    new_groups.append(group)
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)

    return jsonify({'groups': new_groups, "end": math.ceil(count/limit)})


@database_api.route("/getVendors")
def get_vendors():
    database_config = config()
    site_name = session['selected_site']
    vendors = []
    with psycopg2.connect(**database_config) as conn:
        try:
            with conn.cursor() as cur:
                sql = f"SELECT * FROM {site_name}_vendors;"
                cur.execute(sql)
                vendors = cur.fetchall()
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)
    
    return jsonify(vendors=vendors)


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

                    sqlfile = open(f"sites/{site_name}/sql/unique/shopping_lists_safetystock_count.sql", "r+")
                    sql = "\n".join(sqlfile.readlines())
                    sqlfile.close()
                    print(sql)
                    if shopping_list[10] == 'calculated':
                        print(shopping_list[0])
                        cur.execute(sql, (shopping_list[0], ))
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
                    sqlfile = open(f"sites/{site_name}/sql/unique/shopping_lists_safetystock.sql", "r+")
                    sql = "\n".join(sqlfile.readlines())
                    sqlfile.close()
                else:
                    sqlfile = open(f"sites/{site_name}/sql/unique/shopping_lists_safetystock_uncalculated.sql", "r+")
                    sql = "\n".join(sqlfile.readlines())
                    sqlfile.close()
                    
                cur.execute(sql, (id, ))
                shopping_list[3] = list(cur.fetchall())
                print(shopping_list[4])

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