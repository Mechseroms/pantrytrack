from flask import Blueprint, request, render_template, redirect, session, url_for, send_file, jsonify, Response
import psycopg2, math
from config import config

database_api= Blueprint('database_api', __name__)

@database_api.route("/getItems")
def pagninate_items():
    print("hello")
    page = int(request.args.get('page', 1))
    limit = int(request.args.get('limit', 10))
    search_string = str(request.args.get('search_text', ""))

    offset = (page - 1) * limit

    pantry_inventory = []
    count = 0

    database_config = config()
    with psycopg2.connect(**database_config) as conn:
        try:
            with conn.cursor() as cur:
                if search_string != "":
                    sql = f"SELECT * FROM main_items LEFT JOIN main_logistics_info ON main_items.logistics_info_id = main_logistics_info.id WHERE search_string LIKE '%{search_string}%' LIMIT {limit} OFFSET {offset};"
                    cur.execute(sql)
                    pantry_inventory = cur.fetchall()
                    cur.execute(f"SELECT COUNT(*) FROM main_items WHERE search_string LIKE '%{search_string}%';")
                    count = cur.fetchone()[0]
                else:
                    sql = f"SELECT * FROM main_items LEFT JOIN main_logistics_info ON main_items.logistics_info_id = main_logistics_info.id LIMIT %s OFFSET %s;"
                    cur.execute(sql, (limit, offset))
                    pantry_inventory = cur.fetchall()
                    cur.execute("SELECT COUNT(*) FROM main_items;")
                    count = cur.fetchone()[0]

                print(sql)
                print(count, math.ceil(count/limit))
                
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)

        pantry_inventory = sorted(pantry_inventory, key=lambda x: x[2])

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