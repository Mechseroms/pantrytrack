from flask import Blueprint, request, render_template, redirect, session, url_for, send_file, jsonify, Response
import psycopg2, math, json, datetime, main, copy, openfoodfacts
from config import config, sites_config
from main import unfoldCostLayers

external_api= Blueprint('external_api', __name__)

open_food_api = openfoodfacts.API(user_agent="MyAwesomeApp/1.0")

open_food_enabled = False

        
def parseOpenFoodsData(data: dict):
    print(data)
    x = [
        ("brands_tags", list, []), # process into items.tags
        ("categories_tags", list, []), # process into items.tags
        ("countries_tags", list, []), # process into items.tags
        ("labels_hierarchy", list, []), # process into items.tags
        ("ingredients_text_en", str, ""), # process into a list of food_info.ingrediants
        ("nutriments", dict, {}), # process into food_info.nutrients
        ("product_name", str, ""), # #process into items.item_name
        ("serving_size", str, ""), # add to nutriments
        ("code", str, "") # process into items.barcode
        ]
    
    dummy = {}
    keys = data.keys()
    for key in x:
        if key[0] in keys and isinstance(data[key[0]], key[1]):
            dummy[key[0]] = data[key[0]]
        else:
            dummy[key[0]] = key[2]

    tags = dummy["brands_tags"] + dummy["categories_tags"] + dummy["countries_tags"] + dummy["labels_hierarchy"]
    ingredients = str(dummy["ingredients_text_en"]).split(", ")
    nutriments = dummy["nutriments"]
    nutriments["serving_size"] = dummy["serving_size"]

    payload = copy.deepcopy(main.payload_food_item)
    payload["tags"] = tags
    payload["product_name"] = dummy["product_name"]
    payload["food_info"]["ingrediants"] = ingredients
    payload["food_info"]["nutrients"] = nutriments

    print(payload)


@external_api.route("/api/getLink/<site>/<barcode>")
def get_linked_item(site, barcode):
    database_config = config()
    with psycopg2.connect(**database_config) as conn:
        try:
            with conn.cursor() as cur:
                cur.execute(f"SELECT * FROM {site}_itemlinks WHERE barcode=%s;", (barcode, ))
                item = cur.fetchone()
                if item:
                    return jsonify({"item": item}), 200
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)
            conn.rollback()
            return jsonify({'state': str(error)}), 500
    return jsonify({"item": []}), 500

@external_api.route("/api/getItem/<site>/<barcode>")
def get_item(site, barcode):
    database_config = config()
    with psycopg2.connect(**database_config) as conn:
        try:
            with conn.cursor() as cur:
                with open(f"sites/{site}/sql/unique/select_item_all_barcode.sql", "r+") as file:
                    sql = file.read()
                cur.execute(sql, (barcode, ))
                item = cur.fetchone()
                if item:
                    return jsonify({"item": item}), 200
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)
            conn.rollback()
            return jsonify({'state': str(error)}), 500
    return jsonify({"item": []}), 500

@external_api.route("/api/getOpenFacts/<site>/<barcode>")
def get_open_facts(site, barcode):
    if open_food_enabled:
        data = open_food_api.product.get(barcode)
        if data != None:
            return jsonify({"item": data}), 500
    return jsonify({"item": []}), 500


@external_api.route("/api/addTransaction", methods=['POST'])
def add_transaction():

    if request.method == "POST":
        print(request.get_json())
        site_name = request.get_json()["site_name"]
        logistics_info_id = request.get_json()['logistics_info_id']
        barcode = request.get_json()['barcode']
        name = request.get_json()['name']
        location = request.get_json()['location']
        qty = float(request.get_json()['qty'])
        trans_type = request.get_json()['trans_type']
        trans_cost = request.get_json()['trans_cost']

        database_config = config()

        actual_qty = qty
        if trans_type == "Adjust Out":
            actual_qty = -qty

        with psycopg2.connect(**database_config) as conn:
            try:
                with conn.cursor() as cur:
                    cur.execute(f"SELECT id FROM {site_name}_items WHERE barcode=%s;", (barcode,))
                    item_id = cur.fetchone()
                payload = [
                        datetime.datetime.now(),
                        logistics_info_id,
                        barcode,
                        name,
                        trans_type,
                        qty,
                        "",
                        1,
                        json.dumps({'location': location, 'cost': trans_cost})
                        ]
                
                print(payload)
                main.addTransaction(
                    conn=conn,
                    site_name=site_name, 
                    payload=payload,
                    location=location,
                    logistics_info_id=logistics_info_id,
                    item_id=item_id,
                    qty=actual_qty, 
                    cost=trans_cost
                    )

            except (Exception, psycopg2.DatabaseError) as error:
                print(error)
                conn.rollback()
                return jsonify({'state': str(error)})
            print("SUCCESS")
            return jsonify({'state': str("SUCCESS")})
        print("SUCCESS")
        return jsonify({'state': str("FAILED")})


@external_api.route("/api/requestReceiptId/<site>")
def request_receipt_id(site):
    """gets the next id for receipts_id, currently returns a 8 digit number

    Args:
        site (str): site to get the next id for

    Returns:
        json: receipt_id, message, error keys
    """
    database_config = config()
    with psycopg2.connect(**database_config) as conn:
        try:
            with conn.cursor() as cur:
                cur.execute(f"SELECT receipt_id FROM {site}_receipts ORDER BY id DESC LIMIT 1;")
                next_receipt_id = cur.fetchone()
                print(next_receipt_id)
                if next_receipt_id == None:
                    next_receipt_id = "00000001"
                else:
                    next_receipt_id = next_receipt_id[0]
                    next_receipt_id = int(next_receipt_id.split("-")[1]) + 1
                    y = str(next_receipt_id)
                    len_str = len(y)
                    x = "".join(["0" for _ in range(8 - len_str)])
                    next_receipt_id = x + y
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)
            conn.rollback()
            return jsonify({"message": "Failed", "error": str(error)})
    return jsonify({"receipt_id": next_receipt_id, "message": "Success", "error": "None"}), 200

@external_api.route("/api/addReceipt", methods=["POST"])
def add_receipt():
    """Receives a payload and adds the receipt to the system for <site>

    payload = {
        receipt_id: str
        receipt_status: str
        date_submitted: timestamp
        submitted_by: INT
        vendor_id: INT
        files: dict
        items: list = (tuples)
            (type, 0, barcode, name, qty, data, status),
        site_name: str
    }

    Returns:
        Success: dict with "error", "message" keys
    """
    if request.method == "POST":
        site_name = request.get_json()["site_name"] 
        receipt_id = request.get_json()["receipt_id"]
        receipt_status = request.get_json()["receipt_status"]
        date_submitted = request.get_json()['date_submitted']
        submitted_by = request.get_json()["submitted_by"]
        vendor_id = request.get_json()["vendor_id"]
        files = request.get_json()["files"]
        items = request.get_json()["items"]
        payload = (receipt_id, receipt_status, date_submitted, submitted_by, vendor_id, json.dumps(files))
        database_config = config()
        
        with psycopg2.connect(**database_config) as conn:
            try:
                with conn.cursor() as cur:
                    insert_receipt = f"INSERT INTO {site_name}_receipts (receipt_id, receipt_status, date_submitted, submitted_by, vendor_id, files) VALUES (%s, %s, %s, %s, %s, %s) RETURNING id;"
                    cur.execute(insert_receipt, payload)
                    row_id = cur.fetchone()[0]
                    print(row_id)
                    insert_item = f"INSERT INTO {site_name}_receipt_items (type, receipt_id, barcode, name, qty, data, status) VALUES (%s, %s, %s, %s, %s, %s, %s);"
                    for item in items:
                        item = list(item)
                        item[1] = row_id
                        item[5] = json.dumps(item[5])
                        cur.execute(insert_item, item) 
            except (Exception, psycopg2.DatabaseError) as error:
                print(error)
                conn.rollback()
                return jsonify({"message": "Failed", "error": str(error)})
        return jsonify({"message": "Success", "error": "None"})
    return jsonify({"message": "Failed", "error": "Must be a post method!"})
