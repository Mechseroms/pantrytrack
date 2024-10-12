from flask import Blueprint, request, render_template, redirect, session, url_for, send_file, jsonify, Response
import psycopg2, math
from config import config

database_api= Blueprint('database_api', __name__)


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


@database_api.route("/getItems")
def pagninate_items():
    print("hello")
    page = int(request.args.get('page', 1))
    limit = int(request.args.get('limit', 10))
    search_string = str(request.args.get('search_text', ""))
    sort_order = int(request.args.get('sort_order', 1))
    view = int(request.args.get('view', 0))

    offset = (page - 1) * limit

    pantry_inventory = []
    count = 0

    database_config = config()
    with psycopg2.connect(**database_config) as conn:
        try:
            with conn.cursor() as cur:
                pantry_inventory, count = paginate_with_params(
                    cur, limit, offset, 
                    {'search_string': search_string, 
                     'view': view}
                     )
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)

        if sort_order == 0:
            pantry_inventory = sorted(pantry_inventory, key=lambda x: x[1])

        if sort_order == 1:
            pantry_inventory = sorted(pantry_inventory, key=lambda x: x[2])
        
        if sort_order == 2:
            pantry_inventory = sorted(pantry_inventory, key=lambda x: x[18])

    return jsonify({'items': pantry_inventory, "end": math.ceil(count/limit)})

@database_api.route("/getItem")
def get_item():
    id = int(request.args.get('id', 1))
    database_config = config()
    site_name = "main"
    item = []
    with psycopg2.connect(**database_config) as conn:
        try:
            with conn.cursor() as cur:
                with open(f"sites/{site_name}/sql/unique/select_item_all.sql", "r+") as file:
                    sql = file.read()
                cur.execute(sql, (id, ))
                item = list(cur.fetchone())
                item[5] = {'walmart': 'https://www.walmart.com/ip/Ptasie-Mleczko-Chocolate-Covered-Vanilla-Marshmallow-birds-milk-chocolate-13-4-Oz-Includes-Our-Exclusive-HolanDeli-Chocolate-Mints/965551629?classType=REGULAR&from=/search', 'target': 'https://www.target.com/p/hershey-39-s-cookies-39-n-39-cr-232-me-fangs-halloween-candy-snack-size-9-45oz/-/A-79687769#lnk=sametab'}
                item[22] = ['test_list', 'main_list']
                item[23] = ['test_recipe',]
                item[24] = ['test_group', 'main_group', 'test2_group']
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)

    return render_template(f"item_page/index.html", item=item)

@database_api.route("/addGroup")
def addGroup():
    name = str(request.args.get('name', ""))
    description = str(request.args.get('description', ""))
    group_type = str(request.args.get('type', ""))

    state = "FAILED"

    if name or description or group_type == "":
        print("this is empty")

    return jsonify({'state': state})