# 3rd Party imports
from flask import (
    Blueprint, request, render_template, redirect, session, jsonify
    )
import math

# APPLICATION IMPORTS
from application import postsqldb, database_payloads
from application.access_module import access_api
from application.shoppinglists import shoplist_database

shopping_list_api = Blueprint('shopping_list_API', __name__, template_folder="templates", static_folder="static")


# ROOT TEMPLATE ROUTES
@shopping_list_api.route("/")
@access_api.login_required
def shopping_lists():
    sites = [site[1] for site in postsqldb.get_sites(session['user']['sites'])]
    return render_template("lists.html", current_site=session['selected_site'], sites=sites)

@shopping_list_api.route("/<mode>/<id>")
@access_api.login_required
def shopping_list(mode, id):
    sites = [site[1] for site in postsqldb.get_sites(session['user']['sites'])]
    if mode == "view":
        return render_template("view.html", id=id, current_site=session['selected_site'], sites=sites)
    if mode == "edit":
        return render_template("edit.html", id=id, current_site=session['selected_site'], sites=sites)
    return redirect("/")

# API CALLS
# Added to Database
@shopping_list_api.route('/api/addList', methods=["POST"])
@access_api.login_required
def addList():
    if request.method == "POST":
        list_name = request.get_json()['list_name']
        list_description = request.get_json()['list_description']
        list_type = request.get_json()['list_type']
        site_name = session['selected_site']
        user_id = session['user_id']
        shopping_list = database_payloads.ShoppingListPayload(
            name=list_name,
            description=list_description,
            author=user_id,
            type=list_type
        )
        shoplist_database.insertShoppingListsTuple(site_name, shopping_list.payload())
        return jsonify({'error': False, 'message': 'List added!!'})
    return jsonify({'error': True, 'message': 'These was an error with adding the list!'})

# Added to Database
@shopping_list_api.route('/api/getLists', methods=["GET"])
@access_api.login_required
def getShoppingLists():
    lists = []
    if request.method == "GET":
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 1))
        offset = (page-1)*limit
        
        site_name = session['selected_site']
        lists, count = shoplist_database.getShoppingLists(site_name, (limit, offset))

        for list in lists:
            
            if list['type'] == 'calculated':
                items = []
                not_items = shoplist_database.getItemsSafetyStock(site_name)
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

# Added to Database
@shopping_list_api.route('/api/getList', methods=["GET"])
@access_api.login_required
def getShoppingList():
    if request.method == "GET":
        sl_id = int(request.args.get('id', 1))
        site_name = session['selected_site']
        list = shoplist_database.getShoppingList(site_name, (sl_id, ))
        return jsonify({'shopping_list': list, 'error': False, 'message': 'Lists queried successfully!'})

# Added to Database
@shopping_list_api.route('/api/getListItem', methods=["GET"])
@access_api.login_required
def getShoppingListItem():
    list_item = {}
    if request.method == "GET":
        sli_id = int(request.args.get('sli_id', 1))
        site_name = session['selected_site']
        list_item = shoplist_database.getShoppingListItem(site_name, (sli_id, ))
        return jsonify({'list_item': list_item, 'error': False, 'message': 'Lists Items queried successfully!'})
    return jsonify({'list_item': list_item, 'error': True, 'message': 'List Items queried unsuccessfully!'})

# Added to database
@shopping_list_api.route('/api/getItems', methods=["GET"])
@access_api.login_required
def getItems():
    recordset = []
    count = {'count': 0}
    if request.method == "GET":
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 10))
        search_string = request.args.get('search_string', 10)
        site_name = session['selected_site']
        offset = (page - 1) * limit        
        sort_order = "ID ASC"
        payload = (search_string, limit, offset, sort_order)
        recordset, count = shoplist_database.getItemsWithQOH(site_name, payload, convert=True)
        return jsonify({"items":recordset, "end":math.ceil(count['count']/limit), "error":False, "message":"items fetched succesfully!"})
    return jsonify({"items":recordset, "end":math.ceil(count['count']/limit), "error":True, "message":"There was an error with this GET statement"})

# Added to database
@shopping_list_api.route('/api/postListItem', methods=["POST"])
@access_api.login_required
def postListItem():
    if request.method == "POST":
        data = request.get_json()['data']
        site_name = session['selected_site']
        sl_item = database_payloads.ShoppingListItemPayload(
            uuid = data['uuid'],
            sl_id = data['sl_id'],
            item_type=data['item_type'],
            item_name=data['item_name'],
            uom=data['uom'],
            qty=data['qty'],
            item_id=data['item_id'],
            links=data['links']
        )
        shoplist_database.insertShoppingListItemsTuple(site_name, sl_item.payload())
        return jsonify({"error":False, "message":"items fetched succesfully!"})
    return jsonify({"error":True, "message":"There was an error with this GET statement"})

# Added to Database
@shopping_list_api.route('/api/deleteListItem', methods=["POST"])
@access_api.login_required
def deleteListItem():
    if request.method == "POST":
        sli_id = request.get_json()['sli_id']
        site_name = session['selected_site']
        shoplist_database.deleteShoppingListItemsTuple(site_name, (sli_id, ))
        return jsonify({"error":False, "message":"item deleted succesfully!"})
    return jsonify({"error":True, "message":"There was an error with this POST statement"})

# Added to Database
@shopping_list_api.route('/api/saveListItem', methods=["POST"])
@access_api.login_required
def saveListItem():
    if request.method == "POST":
        sli_id = request.get_json()['sli_id']
        update = request.get_json()['update']
        site_name = session['selected_site']
        shoplist_database.updateShoppingListItemsTuple(site_name, {'id': sli_id, 'update': update})
        return jsonify({"error":False, "message":"items fetched succesfully!"})
    return jsonify({"error":True, "message":"There was an error with this GET statement"})

# Added to Database
@shopping_list_api.route('/api/getSKUItemsFull', methods=["GET"])
@access_api.login_required
def getSKUItemsFull():
    items = []
    count = {'count': 0}
    if request.method == "GET":
        site_name = session['selected_site']
        
        not_items = shoplist_database.getItemsSafetyStock(site_name)
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
