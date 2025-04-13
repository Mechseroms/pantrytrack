from flask import Blueprint, request, render_template, redirect, session, url_for, send_file, jsonify, Response
import psycopg2, math, json, datetime, main, copy, requests, process, database, pprint, MyDataclasses
from config import config, sites_config
from main import unfoldCostLayers
from user_api import login_required
import postsqldb

shopping_list_api = Blueprint('shopping_list_API', __name__)

@shopping_list_api.route("/shopping-lists")
@login_required
def shopping_lists():
    sites = [site[1] for site in main.get_sites(session['user']['sites'])]
    return render_template("shopping-lists/index.html", current_site=session['selected_site'], sites=sites)

@shopping_list_api.route("/shopping-list/<mode>/<id>")
@login_required
def shopping_list(mode, id):
    sites = [site[1] for site in main.get_sites(session['user']['sites'])]
    if mode == "view":
        return render_template("shopping-lists/view.html", id=id, current_site=session['selected_site'], sites=sites)
    if mode == "edit":
        return render_template("shopping-lists/edit.html", id=id, current_site=session['selected_site'], sites=sites)
    return redirect("/")

@shopping_list_api.route('/shopping-lists/addList', methods=["POST"])
def addList():
    if request.method == "POST":
        list_name = request.get_json()['list_name']
        list_description = request.get_json()['list_description']
        list_type = request.get_json()['list_type']
        database_config = config()
        site_name = session['selected_site']
        user_id = session['user_id']
        with psycopg2.connect(**database_config) as conn:
            shopping_list = MyDataclasses.ShoppingListPayload(
                name=list_name,
                description=list_description,
                author=user_id,
                type=list_type
            )
            database.insertShoppingListsTuple(conn, site_name, shopping_list.payload())
        return jsonify({'error': False, 'message': 'List added!!'})
    return jsonify({'error': True, 'message': 'These was an error with adding the list!'})

@shopping_list_api.route('/shopping-lists/getLists', methods=["GET"])
def getShoppingLists():
    lists = []
    if request.method == "GET":
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 1))
        offset = (page-1)*limit
        database_config = config()
        site_name = session['selected_site']
        with psycopg2.connect(**database_config) as conn:
            lists, count = database.getShoppingLists(conn, site_name, (limit, offset), convert=True)

            for list in lists:
                
                if list['type'] == 'calculated':
                    items = []
                    not_items = database.getItemsSafetyStock(conn, site_name, convert=True)
                    for item in not_items:
                        new_item = {
                            'id': item['id'], 
                            'uuid': item['barcode'],
                            'sl_id': 0,
                            'item_type': 'sku',
                            'item_name': item['item_name'],
                            'uom': item['uom'],
                            'qty': float(float(item['safety_stock']) - float(item['total_sum'])),
                            'item_id': item['id'],
                            'links': item['links']
                            }
                        items.append(new_item)
                    list['sl_items'] = items

        return jsonify({'shopping_lists': lists, 'end':math.ceil(count/limit), 'error': False, 'message': 'Lists queried successfully!'})

@shopping_list_api.route('/shopping-lists/getList', methods=["GET"])
def getShoppingList():
    if request.method == "GET":
        sl_id = int(request.args.get('id', 1))
        database_config = config()
        site_name = session['selected_site']
        with psycopg2.connect(**database_config) as conn:
            lists = database.getShoppingList(conn, site_name, (sl_id, ), convert=True)
        return jsonify({'shopping_list': lists, 'error': False, 'message': 'Lists queried successfully!'})

@shopping_list_api.route('/shopping-lists/getListItem', methods=["GET"])
def getShoppingListItem():
    list_item = {}
    if request.method == "GET":
        sli_id = int(request.args.get('sli_id', 1))
        database_config = config()
        site_name = session['selected_site']
        with psycopg2.connect(**database_config) as conn:
            list_item = postsqldb.ShoppingListsTable.getItem(conn, site_name, (sli_id, ))
        return jsonify({'list_item': list_item, 'error': False, 'message': 'Lists Items queried successfully!'})
    return jsonify({'list_item': list_item, 'error': True, 'message': 'List Items queried unsuccessfully!'})

@shopping_list_api.route('/shopping-lists/getItems', methods=["GET"])
def getItems():
    recordset = []
    count = {'count': 0}
    if request.method == "GET":
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 10))
        search_string = request.args.get('search_string', 10)
        site_name = session['selected_site']
        offset = (page - 1) * limit
        database_config = config()
        with psycopg2.connect(**database_config) as conn:
            payload = (search_string, limit, offset)
            recordset, count = database.getItemsWithQOH(conn, site_name, payload, convert=True)
        return jsonify({"items":recordset, "end":math.ceil(count['count']/limit), "error":False, "message":"items fetched succesfully!"})
    return jsonify({"items":recordset, "end":math.ceil(count['count']/limit), "error":True, "message":"There was an error with this GET statement"})

@shopping_list_api.route('/shopping-lists/postListItem', methods=["POST"])
def postListItem():
    if request.method == "POST":
        data = request.get_json()['data']
        site_name = session['selected_site']
        database_config = config()
        with psycopg2.connect(**database_config) as conn:
            sl_item = MyDataclasses.ShoppingListItemPayload(
                uuid = data['uuid'],
                sl_id = data['sl_id'],
                item_type=data['item_type'],
                item_name=data['item_name'],
                uom=data['uom'],
                qty=data['qty'],
                item_id=data['item_id'],
                links=data['links']
            )
            database.insertShoppingListItemsTuple(conn, site_name, sl_item.payload())
        return jsonify({"error":False, "message":"items fetched succesfully!"})
    return jsonify({"error":True, "message":"There was an error with this GET statement"})

@shopping_list_api.route('/shopping-lists/deleteListItem', methods=["POST"])
def deleteListItem():
    if request.method == "POST":
        sli_id = request.get_json()['sli_id']
        site_name = session['selected_site']
        database_config = config()
        with psycopg2.connect(**database_config) as conn:
            database.deleteShoppingListItemsTuple(conn, site_name, (sli_id, ))
        return jsonify({"error":False, "message":"item deleted succesfully!"})
    return jsonify({"error":True, "message":"There was an error with this POST statement"})

@shopping_list_api.route('/shopping-lists/saveListItem', methods=["POST"])
def saveListItem():
    if request.method == "POST":
        sli_id = request.get_json()['sli_id']
        update = request.get_json()['update']
        site_name = session['selected_site']
        database_config = config()
        with psycopg2.connect(**database_config) as conn:
            database.__updateTuple(conn, site_name, f"{site_name}_shopping_list_items", {'id': sli_id, 'update': update})
        return jsonify({"error":False, "message":"items fetched succesfully!"})
    return jsonify({"error":True, "message":"There was an error with this GET statement"})

@shopping_list_api.route('/shopping-lists/getSKUItemsFull', methods=["GET"])
def getSKUItemsFull():
    items = []
    count = {'count': 0}
    if request.method == "GET":
        site_name = session['selected_site']
        database_config = config()
        with psycopg2.connect(**database_config) as conn:
            not_items = database.getItemsSafetyStock(conn, site_name, convert=True)
            for item in not_items:
                new_item = {
                    'id': item['id'], 
                    'uuid': item['barcode'],
                    'sl_id': 0,
                    'item_type': 'sku',
                    'item_name': item['item_name'],
                    'uom': item['uom'],
                    'qty': float(float(item['safety_stock']) - float(item['total_sum'])),
                    'item_id': item['id'],
                    'links': item['links']
                    }
                items.append(new_item)
        return jsonify({"list_items":items, "error":False, "message":"items fetched succesfully!"})
    return jsonify({"list_items":items, "error":True, "message":"There was an error with this GET statement"})
