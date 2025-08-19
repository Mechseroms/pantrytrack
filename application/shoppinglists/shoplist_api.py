# 3rd Party imports
from flask import (
    Blueprint, request, render_template, redirect, session, jsonify
    )
import math

# APPLICATION IMPORTS
from application import postsqldb, database_payloads
from application.access_module import access_api
from application.shoppinglists import shoplist_database, shoplist_processess

shopping_list_api = Blueprint('shopping_list_API', __name__, template_folder="templates", static_folder="static")


# ROOT TEMPLATE ROUTES
@shopping_list_api.route("/")
@access_api.login_required
def shopping_lists():
    sites = [site[1] for site in postsqldb.get_sites(session['user']['sites'])]
    return render_template("lists.html", current_site=session['selected_site'], sites=sites)

@shopping_list_api.route("/<mode>/<list_uuid>")
@access_api.login_required
def shopping_list(mode, list_uuid):
    sites = [site[1] for site in postsqldb.get_sites(session['user']['sites'])]
    if mode == "view":
        return render_template("view.html", list_uuid=list_uuid, current_site=session['selected_site'], sites=sites)
    if mode == "edit":
        return render_template("edit.html", list_uuid=list_uuid, current_site=session['selected_site'], sites=sites)
    return redirect("/")

@shopping_list_api.route("/generate")
@access_api.login_required
def generateList():
    sites = [site[1] for site in postsqldb.get_sites(session['user']['sites'])]
    units = postsqldb.get_units_of_measure()
    return render_template("generate.html", current_site=session['selected_site'], sites=sites, units=units)

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
            sub_type=list_type
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
            
            if list['sub_type'] == 'calculated':
                items = []
                not_items = shoplist_database.getItemsSafetyStock(site_name)
                for item in not_items:
                    new_item = {
                        'list_item_uuid': 0,
                        'list_uuid': list['list_uuid'],
                        'item_type': 'sku',
                        'item_name': item['item_name'],
                        'uom': item['item_info']['uom'],
                        'qty': float(float(item['item_info']['safety_stock']) - float(item['total_sum'])),
                        'links': item['links'],
                        'uom_fullname': ['uom_fullname']
                        }
                    items.append(new_item)
                list['sl_items'] = items

        return jsonify({'shopping_lists': lists, 'end':math.ceil(count/limit), 'error': False, 'message': 'Lists queried successfully!'})

# Added to Database
@shopping_list_api.route('/api/getList', methods=["GET"])
@access_api.login_required
def getShoppingList():
    if request.method == "GET":
        list_uuid = request.args.get('list_uuid', 1)
        site_name = session['selected_site']
        list = shoplist_database.getShoppingList(site_name, (list_uuid, ))
        return jsonify({'shopping_list': list, 'error': False, 'message': 'Lists queried successfully!'})

# Added to Database
@shopping_list_api.route('/api/getListItem', methods=["GET"])
@access_api.login_required
def getShoppingListItem():
    list_item = {}
    if request.method == "GET":
        list_item_uuid = request.args.get('list_item_uuid', '')
        site_name = session['selected_site']
        list_item = shoplist_database.getShoppingListItem(site_name, (list_item_uuid, ))
        return jsonify({'list_item': list_item, 'error': False, 'message': 'Lists Items queried successfully!'})
    return jsonify({'list_item': list_item, 'error': True, 'message': 'List Items queried unsuccessfully!'})

# Added to database
@shopping_list_api.route('/api/getItemstwo', methods=["GET"])
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

@shopping_list_api.route('/api/getRecipesModal', methods=["GET"])
@access_api.login_required
def getRecipesModal():
    recordsets = []
    count = 0
    if request.method == "GET":
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 10))
        search_string = request.args.get('search_string', 10)
        site_name = session['selected_site']
        offset = (page - 1) * limit        
        
        payload = (search_string, limit, offset)
        recordsets, count = shoplist_database.getRecipesModal(site_name, payload)
        return jsonify(status=201, recipes=recordsets, end=math.ceil(count/limit), message=f"Recipes fetched successfully!")
    return jsonify(status=405, recipes=recordsets, end=math.ceil(count/limit), message=f"{request.method} is not an accepted method on this endpoint!")

@shopping_list_api.route('/api/getListsModal', methods=["GET"])
@access_api.login_required
def getListsModal():
    recordsets = []
    count = 0
    if request.method == "GET":
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 10))
        search_string = request.args.get('search_string', 10)
        site_name = session['selected_site']
        offset = (page - 1) * limit        
        
        payload = (search_string, limit, offset)
        recordsets, count = shoplist_database.getListsModal(site_name, payload)
        return jsonify(status=201, lists=recordsets, end=math.ceil(count/limit), message=f"Recipes fetched successfully!")
    return jsonify(status=405, lists=recordsets, end=math.ceil(count/limit), message=f"{request.method} is not an accepted method on this endpoint!")


@shopping_list_api.route("/api/getItems", methods=["GET"])
@access_api.login_required
def getItemsModal():
    items = []
    count = 0
    if request.method == "GET":
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 10))
        search_string = request.args.get('search_string', 10)
        site_name = session['selected_site']
        offset = (page - 1) * limit        
        payload = (search_string, limit, offset)
        items, count = shoplist_database.getItemsModal(site_name, payload)
        return jsonify(status=201, items=items, end=math.ceil(count/limit), message=f"Items fetched successfully!")
    return jsonify(status=405, items=items, end=math.ceil(count/limit), message=f"{request.method} is not an accepted method on this endpoint!")


# Added to database
@shopping_list_api.route('/api/postListItem', methods=["POST"])
@access_api.login_required
def postListItem():
    if request.method == "POST":
        data = request.get_json()['data']
        site_name = session['selected_site']
        sl_item = database_payloads.ShoppingListItemPayload(
            list_uuid = data['list_uuid'],
            item_type=data['item_type'],
            item_name=data['item_name'],
            uom=data['uom'],
            qty=data['qty'],
            item_uuid=data['item_uuid'],
            links=data['links']
        )
        shoplist_database.insertShoppingListItemsTuple(site_name, sl_item.payload())
        return jsonify({"error":False, "message":"items fetched succesfully!"})
    return jsonify({"error":True, "message":"There was an error with this GET statement"})

@shopping_list_api.route('/api/postRecipeLine', methods=["POST"])
@access_api.login_required
def postRecipeLine():
    if request.method == "POST":
        data = request.get_json()
        
        site_name = session['selected_site']
        user_id = session['user_id']
        """sl_item = database_payloads.ShoppingListItemPayload(
            uuid = data['uuid'],
            sl_id = data['sl_id'],
            item_type=data['item_type'],
            item_name=data['item_name'],
            uom=data['uom'],
            qty=data['qty'],
            item_id=data['item_id'],
            links=data['links']
        )
        shoplist_database.insertShoppingListItemsTuple(site_name, sl_item.payload())"""
        shoplist_processess.addRecipeItemsToList(site_name, data, user_id)

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

@shopping_list_api.route('/api/deleteList', methods=["POST"])
@access_api.login_required
def deleteList():
    if request.method == "POST":
        shopping_list_uuid = request.get_json()['shopping_list_uuid']
        site_name = session['selected_site']
        user_id = session['user_id']
        shoplist_processess.deleteShoppingList(site_name, {'shopping_list_uuid': shopping_list_uuid}, user_id)
        return jsonify({"error":False, "message":"List Deleted succesfully!"})
    return jsonify({"error":True, "message":"There was an error with this POST statement"})


# Added to Database
@shopping_list_api.route('/api/saveListItem', methods=["POST"])
@access_api.login_required
def saveListItem():
    if request.method == "POST":
        list_item_uuid = request.get_json()['list_item_uuid']
        update = request.get_json()['update']
        site_name = session['selected_site']
        shoplist_database.updateShoppingListItemsTuple(site_name, {'uuid': list_item_uuid, 'update': update})
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
        print(not_items)
        for item in not_items:
            new_item = {
                'id': item['id'], 
                'uuid': item['barcode'],
                'sl_id': 0,
                'item_type': 'sku',
                'item_name': item['item_name'],
                'uom': item['item_info']['uom'],
                'qty': float(float(item['item_info']['safety_stock']) - float(item['total_sum'])),
                'item_id': item['id'],
                'links': item['links'],
                'uom_fullname': item['uom_fullname'],
                'list_item_state': False
                }
            items.append(new_item)
        return jsonify({"list_items":items, "error":False, "message":"items fetched succesfully!"})
    return jsonify({"list_items":items, "error":True, "message":"There was an error with this GET statement"})

# Added to Database
@shopping_list_api.route('/api/setListItemState', methods=["POST"])
@access_api.login_required
def setListItemState():
    items = []
    count = {'count': 0}
    if request.method == "POST":
        site_name = session['selected_site']
        print(request.get_json())
        
        shoplist_database.updateShoppingListItemsTuple(site_name, {'uuid': request.get_json()['list_item_uuid'], 'update': {'list_item_state': request.get_json()['list_item_state']}})

        return jsonify({"list_items":items, "error":False, "message":"items fetched succesfully!"})
    return jsonify({"list_items":items, "error":True, "message":"There was an error with this GET statement"})


@shopping_list_api.route('/api/postGeneratedList', methods=["POST"])
@access_api.login_required
def postGeneratedList():
    if request.method == "POST":
        payload: dict = request.get_json()
        site_name: str = session['selected_site']
        user_id: int = session['user_id']
        shoplist_processess.postNewGeneratedList(site_name, payload, user_id)
        return jsonify(status=201,  message=f"List Generated successfully!")
    return jsonify(status=405, message=f"{request.method} is not an accepted method on this endpoint!")