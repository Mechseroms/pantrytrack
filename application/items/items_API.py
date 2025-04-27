from flask import Blueprint, request, render_template, redirect, session, url_for, send_file, jsonify, Response
import psycopg2, math, json, datetime, main, copy, requests, process, database, pprint, MyDataclasses
from config import config, sites_config
from main import unfoldCostLayers
from user_api import login_required
import application.postsqldb as db
from application.items import database_items

items_api = Blueprint('items_api', __name__)

@items_api.route("/item/<parent_id>/itemLink/<id>")
@login_required
def itemLink(parent_id, id):
    sites = [site[1] for site in main.get_sites(session['user']['sites'])]
    return render_template("items/itemlink.html", current_site=session['selected_site'], sites=sites, proto={'referrer': request.referrer}, id=id)

@items_api.route("/item/getTransactions", methods=["GET"])
@login_required
def getTransactions():
    """ GET a subquery of transactions by passing a logistics_info_id, limit, and page
    ---
    responses:
        200:
            description: transactions received successfully.
    """
    if request.method == "GET":
        recordset = []
        count = 0
        logistics_info_id = int(request.args.get('logistics_info_id', 1))
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 50))
        site_name = session['selected_site']
        offset = (page - 1) * limit
        recordset, count = database_items.getTransactions(site_name, (logistics_info_id, limit, offset))
        return jsonify({"transactions": recordset, "end": math.ceil(count/limit), "error": False, "message": ""})
    return jsonify({"transactions": recordset, "end": math.ceil(count/limit), "error": True, "message": f"method {request.method} is not allowed."})

@items_api.route("/item/getTransaction", methods=["GET"])
@login_required
def getTransaction():
    """ GET a transaction from the system by passing an ID
    ---
    parameters:
        - in: query
          name: id
          schema:
            type: integer
            minimum: 1
            default: 1
          required: true
          description: The transaction.id
    responses:
        200:
            description: Transaction Object received successfully.
    """
    transaction = ()
    if request.method == "GET":
        id = int(request.args.get('id', 1))
        site_name = session['selected_site']
        transaction = database_items.getTransaction(site_name, (id, ))
        return jsonify({"transaction": transaction, "error": False, "message": ""})
    return jsonify({"transaction": transaction,  "error": True, "message": f"method {request.method} is not allowed."})

@items_api.route("/item/getItem", methods=["GET"])
@login_required
def get_item():
    """ GET item from system by passing its ID
    ---
    parameters:
        - in: query
          name: id
          schema:
            type: integer
            minimum: 1
            default: 1
          description: item.id
    responses:
        200:
            description: Item.id received successfully!
    """
    if request.method == "GET":
        id = int(request.args.get('id', 1))
        site_name = session['selected_site']
        item = ()
        item = database_items.getItemAllByID(site_name, (id, ))
        return jsonify({'item': item, 'error': False, 'message': ''})
    return jsonify({'item': item, 'error': True, 'message': f'method {request.method} not allowed.'})

@items_api.route("/item/getItemsWithQOH", methods=['GET'])
@login_required
def pagninate_items():
    """ GET items from the system by passing a page, limit, search_string, sort, and order
    ---
    parameters:
        - in: query
          name: page
          schema:
            type: integer
            default: 1
          description: page number for offset
        - in: query
          name: limit
          schema:
            type: integer
            default: 50
          description: number of records to grab
        - in: query
          name: search_string
          schema:
            type: string
            default: ''
          description: string to look for in column search_string
        - in: query
          name: sort
          schema:
            type: string
            default: ''
          description: items table column to sort by
        - in: query
          name: order
          schema:
            type: string
            enum: ['ASC', 'DESC']
            default: 'ASC'
          description: Order to sort items table sort parameter by
    responses:
        200:
            description: Items received successfully.
    """
    items = []
    count = 0
    if request.method == "GET":
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 10))
        search_string = str(request.args.get('search_text', ""))
        sort = request.args.get('sort', "")
        order = request.args.get('order', "")
        site_name = session['selected_site']
        offset = (page - 1) * limit
        if sort == 'total_qoh':
            sort_order = f"{sort} {order}"
        else:
            sort_order = f"item.{sort} {order}"
        
        items, count = database_items.getItemsWithQOH(site_name, (search_string, limit, offset, sort_order))
        
        return jsonify({'items': items, "end": math.ceil(count/limit), 'error':False, 'message': 'Items Loaded Successfully!'})
    return jsonify({'items': items, "end": math.ceil(count/limit), 'error':True, 'message': 'There was a problem loading the items!'})

@items_api.route('/item/getModalItems', methods=["GET"])
@login_required
def getModalItems():
    """ GET items from the system by passing a page, limit, search_string. For select modals
    ---
    parameters:
        - in: query
          name: page
          schema:
            type: integer
            default: 1
          description: page number for offset
        - in: query
          name: limit
          schema:
            type: integer
            default: 25
          description: number of records to grab
        - in: query
          name: search_string
          schema:
            type: string
            default: ''
          description: string to look for in column search_string  
    responses:
        200:
            description: Items received successfully.
    """
    recordset, count = tuple(), 0
    if request.method == "GET":
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 10))
        search_string = request.args.get('search_string', '')
        site_name = session['selected_site']
        offset = (page - 1) * limit
        recordset, count = database_items.getModalSKUs(site_name, (search_string, limit, offset))
        print(recordset, count)
        return jsonify({"items":recordset, "end":math.ceil(count/limit), "error":False, "message":"items fetched succesfully!"})
    return jsonify({"items":recordset, "end":math.ceil(count/limit), "error":True, "message": f"method {request.method} is not allowed."})

@items_api.route('/item/getPrefixes', methods=["GET"])
@login_required
def getModalPrefixes():
    """ GET prefixes from the system by passing page and limit.
    ---
    parameters:
        - in: query
          name: page
          schema:
            type: integer
            minimum: 1
            default: 1
          description: page of the database records
        - in: query
          name: limit
          schema:
            type: integer
            minimum: 1
            default: 10
          description: number of database records to GET
    responses:
        200:
            description: Prefixes received from the system successfully!
    """
    recordset = []
    count = 0
    if request.method == "GET":
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 10))
        site_name = session['selected_site']
        offset = (page - 1) * limit
        recordset, count = database_items.getPrefixes(site_name, (limit, offset))
        print(recordset, count)
        return jsonify({"prefixes":recordset, "end":math.ceil(count/limit), "error":False, "message":"items fetched succesfully!"})
    return jsonify({"prefixes":recordset, "end":math.ceil(count/limit), "error":True, "message":f"method {request.method} is not allowed!"})


@items_api.route('/item/getZones', methods=['GET'])
def getZones():
    page = int(request.args.get('page', 1))
    limit = int(request.args.get('limit', 1))
    database_config = config()
    site_name = session['selected_site']
    zones = []
    offset = (page - 1) * limit
    payload = (limit, offset)
    count = 0
    with psycopg2.connect(**database_config) as conn:
        zones, count = database.getZonesWithCount(conn, site_name, payload, convert=True)
    print(count, len(zones))
    return jsonify(zones=zones, endpage=math.ceil(count[0]/limit))


@items_api.route('/item/getZonesBySku', methods=["GET"])
def getZonesbySku():
    if request.method == "GET":
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 1))
        item_id = int(request.args.get('item_id'))
        database_config = config()
        site_name = session['selected_site']
        zones = []
        offset = (page - 1) * limit
        payload = (item_id, limit, offset)
        count = 0
        with psycopg2.connect(**database_config) as conn:
            zones, count = db.ZonesTable.paginateZonesBySku(conn, site_name, payload)
            print(zones, count)
        return jsonify(zones=zones, endpage=math.ceil(count/limit))

@items_api.route('/item/getLocationsBySkuZone', methods=['get'])
def getLocationsBySkuZone():
    zone_id = int(request.args.get('zone_id', 1))
    part_id = int(request.args.get('part_id', 1))
    page = int(request.args.get('page', 1))
    limit = int(request.args.get('limit', 1))

    offset = (page-1)*limit
    database_config = config()
    site_name = session['selected_site']
    locations = []
    count=0
    with psycopg2.connect(**database_config) as conn:
        payload = (part_id, zone_id, limit, offset)
        locations, count = db.LocationsTable.paginateLocationsBySkuZone(conn, site_name, payload)
    return jsonify(locations=locations, endpage=math.ceil(count/limit))


@items_api.route('/item/getLocations', methods=['get'])
def getLocationsByZone():
    zone_id = int(request.args.get('zone_id', 1))
    part_id = int(request.args.get('part_id', 1))
    page = int(request.args.get('page', 1))
    limit = int(request.args.get('limit', 1))

    offset = (page-1)*limit
    database_config = config()
    site_name = session['selected_site']
    locations = []
    count=0
    with psycopg2.connect(**database_config) as conn:
        sql = f"SELECT * FROM {site_name}_locations WHERE zone_id=%s LIMIT %s OFFSET %s;"
        locations = database.queryTuples(conn, sql, (zone_id, limit, offset), convert=True)
        sql = f"SELECT COUNT(*) FROM {site_name}_locations WHERE zone_id=%s;"
        count = database.queryTuple(conn, sql, (zone_id, ))
    return jsonify(locations=locations, endpage=math.ceil(count[0]/limit))

@items_api.route('/item/getBrands', methods=['GET'])
def getBrands():
    page = int(request.args.get('page', 1))
    limit = int(request.args.get('limit', 1))
    offset = (page-1)*limit
    database_config = config()
    site_name = session['selected_site']
    brands = []
    count = 0
    with psycopg2.connect(**database_config) as conn:
        brands, count = database._paginateTableTuples(conn, site_name, f"{site_name}_brands", (limit, offset), convert=True)
    return jsonify(brands=brands, endpage=math.ceil(count['count']/limit))

@items_api.route('/item/updateItem', methods=['POST'])
def updateItem():
    if request.method == "POST":
        id = request.get_json()['id']
        data = request.get_json()['data']

        database_config = config()
        site_name = session['selected_site']

        transaction_data = {}
        for key in data.keys():
            for key_2 in data[key].keys():
                transaction_data[f"{key_2}_new"] = data[key][key_2]

        with psycopg2.connect(**database_config) as conn:
            item = database.getItemAllByID(conn, site_name, (id, ), convert=True)
            if 'item_info' in data.keys() and data['item_info'] != {}:
                for key in data['item_info'].keys():
                    transaction_data[f"{key}_old"] = item['item_info'][key]
                item_info_id = item['item_info_id']
                item_info = database.__updateTuple(conn, site_name, f"{site_name}_item_info", {'id': item_info_id, 'update': data['item_info']}, convert=True)
            if 'food_info' in data.keys() and data['food_info'] != {}:
                for key in data['food_info'].keys():
                    transaction_data[f"{key}_old"] = item['food_info'][key]
                food_info_id = item['food_info_id']
                print(food_info_id, data['food_info'])
                food_info = database.__updateTuple(conn, site_name, f"{site_name}_food_info", {'id': food_info_id, 'update': data['food_info']}, convert=True)
            if 'logistics_info' in data.keys() and data['logistics_info'] != {}:
                for key in data['logistics_info'].keys():
                    transaction_data[f"{key}_old"] = item['logistics_info'][key]
                logistics_info_id = item['logistics_info_id']
                print(logistics_info_id, data['logistics_info'])
                logistics_info = database.__updateTuple(conn, site_name, f"{site_name}_logistics_info", {'id': logistics_info_id, 'update': data['logistics_info']}, convert=True)
            if 'item' in data.keys() and data['item'] != {}:
                for key in data['item'].keys():
                    if key == "brand":
                        transaction_data[f"{key}_old"] = item['brand']['id']
                    else:
                        transaction_data[f"{key}_old"] = item[key]
                item = database.__updateTuple(conn, site_name, f"{site_name}_items", {'id': id, 'update': data['item']}, convert=True)

            trans = MyDataclasses.TransactionPayload(
                timestamp=datetime.datetime.now(),
                logistics_info_id=item['logistics_info_id'],
                barcode=item['barcode'],
                name=item['item_name'],
                transaction_type="UPDATE",
                quantity=0.0,
                description="Item was updated!",
                user_id=session['user_id'],
                data=transaction_data
            )
            database.insertTransactionsTuple(conn, site_name, trans.payload())

        return jsonify(error=False, message="Item updated successfully!")
    return jsonify(error=True, message="Unable to save, ERROR!")

@items_api.route('/item/updateItemLink', methods=['POST'])
def updateItemLink():
    if request.method == "POST":
        id = request.get_json()['id']
        conv_factor = request.get_json()['conv_factor']
        barcode = request.get_json()['barcode']
        old_conv_factor = request.get_json()['old_conv']


        database_config = config()
        site_name = session['selected_site']
        user_id = session['user_id']
        transaction_time = datetime.datetime.now()
        with psycopg2.connect(**database_config) as conn:
            linkedItem = database.getItemAllByBarcode(conn, site_name, (barcode, ), convert=True)

            transaction = MyDataclasses.TransactionPayload(
                timestamp=transaction_time,
                logistics_info_id=linkedItem['logistics_info_id'],
                barcode=barcode,
                name=linkedItem['item_name'],
                transaction_type='UPDATE',
                quantity=0.0,
                description='Link updated!',
                user_id=user_id,
                data={'new_conv_factor': conv_factor, 'old_conv_factor': old_conv_factor}
            )

            database.__updateTuple(conn, site_name, f"{site_name}_itemlinks", {'id': id, 'update': {'conv_factor': conv_factor}})
            database.insertTransactionsTuple(conn, site_name, transaction.payload())
            return jsonify(error=False, message="Linked Item was updated successfully")
    return jsonify(error=True, message="Unable to save this change, ERROR!")


@items_api.route('/item/getPossibleLocations', methods=["GET"])
@login_required
def getPossibleLocations():
    if request.method == "GET":
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 1))
        offset = (page-1)*limit
        database_config = config()
        site_name = session['selected_site']
        with psycopg2.connect(**database_config) as conn:
            locations, count = db.LocationsTable.paginateLocationsWithZone(conn, site_name, (limit, offset))
        return jsonify(locations=locations, end=math.ceil(count/limit))

@items_api.route('/item/getLinkedItem', methods=["GET"])
@login_required
def getLinkedItem():
    linked_item = {}
    if request.method == "GET":
        id = int(request.args.get('id', 1))
        database_config = config()
        site_name = session['selected_site']
        with psycopg2.connect(**database_config) as conn:
            linked_item = database.__selectTuple(conn, site_name, f"{site_name}_itemlinks", (id, ), convert=True)
        return jsonify({'linked_item': linked_item, 'error': False, 'message': 'Linked Item added!!'})
    return jsonify({'linked_item': linked_item, 'error': True, 'message': 'These was an error with adding to the linked list!'})

@items_api.route('/item/addLinkedItem', methods=["POST"])   
def addLinkedItem():
    if request.method == "POST":
        parent_id = request.get_json()['parent_id']
        child_id = request.get_json()['child_id']
        conv_factor = request.get_json()['conv_factor']

        database_config = config()
        site_name = session['selected_site']
        user_id = session['user_id']
        with psycopg2.connect(**database_config) as conn:
            print(parent_id, child_id, conv_factor)
            parent_item = database.getItemAllByID(conn, site_name, (parent_id, ), convert=True)
            child_item = database.getItemAllByID(conn, site_name, (child_id, ), convert=True)
            
            # i need to transact out ALL locations for child item.
            pprint.pprint(child_item)
            sum_child_qoh = 0
            for location in child_item['item_locations']:
                print(location)
                sum_child_qoh += location['quantity_on_hand']
                payload = {
                    'item_id': child_item['id'],
                    'logistics_info_id': child_item['logistics_info_id'],
                    'barcode': child_item['barcode'],
                    'item_name': child_item['item_name'],
                    'transaction_type': 'Adjust Out',
                    'quantity': location['quantity_on_hand'],
                    'description': f'Converted to {parent_item['barcode']}',
                    'cost': child_item['item_info']['cost'],
                    'vendor': 1,
                    'expires': False,
                    'location_id': location['location_id']
                }
                process.postTransaction(conn, site_name, user_id, payload)

            print(sum_child_qoh)

            primary_location = database.selectItemLocationsTuple(conn, site_name, (parent_item['id'], parent_item['logistics_info']['primary_location']['id']), convert=True)


            payload = {
                    'item_id': parent_item['id'],
                    'logistics_info_id': parent_item['logistics_info_id'],
                    'barcode': parent_item['barcode'],
                    'item_name': parent_item['item_name'],
                    'transaction_type': 'Adjust In',
                    'quantity': (float(sum_child_qoh)*float(conv_factor)),
                    'description': f'Converted from {child_item['barcode']}',
                    'cost': child_item['item_info']['cost'],
                    'vendor': 1,
                    'expires': None,
                    'location_id': primary_location['location_id']
                }
            
            pprint.pprint(payload)
            result = process.postTransaction(conn, site_name, user_id, payload)

            if result['error']:
                return jsonify(result)
            
            itemLink = MyDataclasses.ItemLinkPayload(
                barcode=child_item['barcode'],
                link=parent_item['id'],
                data=child_item,
                conv_factor=conv_factor
            )

            database.insertItemLinksTuple(conn, site_name, itemLink.payload())

            database.__updateTuple(conn, site_name, f"{site_name}_items", {'id': child_item['id'], 'update': {'row_type': 'link'}})
        
        return jsonify({'error': False, 'message': 'Linked Item added!!'})
    return jsonify({'error': True, 'message': 'These was an error with adding to the linked list!'})
    
@items_api.route('/items/addBlankItem', methods=["POST"])
def addBlankItem():
    if request.method == "POST":
        data = {
            'barcode': request.get_json()['barcode'], 
            'name': request.get_json()['name'], 
            'subtype': request.get_json()['subtype']
            }
        pprint.pprint(data)
        database_config = config()
        site_name = session['selected_site']
        user_id = session['user_id']
        try:
            with psycopg2.connect(**database_config) as conn:
                process.postNewBlankItem(conn, site_name, user_id, data)
        except Exception as error:
            conn.rollback()
            return jsonify({'error': True, 'message': error})
        return jsonify({'error': False, 'message': 'Item added!!'})
    return jsonify({'error': True, 'message': 'These was an error with adding Item!'})

@items_api.route('/items/addSKUPrefix', methods=["POST"])
def addSKUPrefix():
    if request.method == "POST":
        database_config = config()
        site_name = session['selected_site']
        try:
            with psycopg2.connect(**database_config) as conn:
                prefix = db.SKUPrefixTable.Payload(
                    request.get_json()['uuid'],
                    request.get_json()['name'], 
                    request.get_json()['description']
                )
                db.SKUPrefixTable.insert_tuple(conn, site_name, prefix.payload())
        except Exception as error:
            conn.rollback()
            return jsonify({'error': True, 'message': error})
        return jsonify({'error': False, 'message': 'Prefix added!!'})
    return jsonify({'error': True, 'message': 'These was an error with adding this Prefix!'})

@items_api.route('/item/addConversion', methods=['POST'])
def addConversion():
    if request.method == "POST":
        item_id = request.get_json()['parent_id']
        uom_id = request.get_json()['uom_id']
        conv_factor = request.get_json()['conv_factor']

        database_config = config()
        site_name = session['selected_site']
        with psycopg2.connect(**database_config) as conn:
            conversion = db.ConversionsTable.Payload(
                item_id, uom_id, conv_factor
            )
            db.ConversionsTable.insert_tuple(conn, site_name, conversion.payload())
            
            return jsonify(error=False, message="Conversion was added successfully")
    return jsonify(error=True, message="Unable to save this conversion, ERROR!")

@items_api.route('/item/deleteConversion', methods=['POST'])
def deleteConversion():
    if request.method == "POST":
        conversion_id = request.get_json()['conversion_id']
        print(conversion_id)
        database_config = config()
        site_name = session['selected_site']
        with psycopg2.connect(**database_config) as conn:
            db.ConversionsTable.delete_item_tuple(conn, site_name, (conversion_id,))
            
            return jsonify(error=False, message="Conversion was deleted successfully")
    return jsonify(error=True, message="Unable to delete this conversion, ERROR!")

@items_api.route('/item/updateConversion', methods=['POST'])
def updateConversion():
    if request.method == "POST":
        conversion_id = request.get_json()['conversion_id']
        update_dictionary = request.get_json()['update']

        database_config = config()
        site_name = session['selected_site']
        with psycopg2.connect(**database_config) as conn:
            db.ConversionsTable.update_item_tuple(conn, site_name, {'id': conversion_id, 'update': update_dictionary})
            return jsonify(error=False, message="Conversion was updated successfully")
    return jsonify(error=True, message="Unable to save this conversion, ERROR!")

@items_api.route('/item/addPrefix', methods=['POST'])
def addPrefix():
    if request.method == "POST":
        item_info_id = request.get_json()['parent_id']
        prefix_id = request.get_json()['prefix_id']
        print(item_info_id)
        print(prefix_id)
        database_config = config()
        site_name = session['selected_site']
        with psycopg2.connect(**database_config) as conn:
            prefixes = db.ItemInfoTable.select_tuple(conn, site_name, (item_info_id,))['prefixes']
            print(prefixes)
            prefixes.append(prefix_id)
            db.ItemInfoTable.update_tuple(conn, site_name, {'id': item_info_id, 'update':{'prefixes': prefixes}})
            return jsonify(error=False, message="Prefix was added successfully")
    return jsonify(error=True, message="Unable to save this prefix, ERROR!")

@items_api.route('/item/deletePrefix', methods=['POST'])
def deletePrefix():
    if request.method == "POST":
        item_info_id = request.get_json()['item_info_id']
        prefix_id = request.get_json()['prefix_id']

        database_config = config()
        site_name = session['selected_site']
        with psycopg2.connect(**database_config) as conn:
            prefixes = db.ItemInfoTable.select_tuple(conn, site_name, (item_info_id,))['prefixes']
            prefixes.remove(prefix_id)
            db.ItemInfoTable.update_tuple(conn, site_name, {'id': item_info_id, 'update':{'prefixes': prefixes}})
            return jsonify(error=False, message="Prefix was deleted successfully")
    return jsonify(error=True, message="Unable to delete this prefix, ERROR!")

@items_api.route('/item/refreshSearchString', methods=['POST'])
def refreshSearchString():
    if request.method == "POST":
        item_id = request.get_json()['item_id']

        database_config = config()
        site_name = session['selected_site']
        with psycopg2.connect(**database_config) as conn:
            item = db.ItemTable.getItemAllByID(conn, site_name, (item_id,))
            parameters = [f"id::{item['id']}", f"barcode::{item['barcode']}", f"name::{item['item_name']}", f"brand::{item['brand']['name']}", 
                          f"expires::{item['food_info']['expires']}", f"row_type::{item['row_type']}", f"item_type::{item['item_type']}"]
            
            for prefix in item['item_info']['prefixes']:
                parameters.append(f"prefix::{prefix['name']}")

            search_string = "&&".join(parameters)
            db.ItemTable.update_tuple(conn, site_name, {'id': item_id, 'update':{'search_string': search_string}})

            return jsonify(error=False, message="Search String was updated successfully")
    return jsonify(error=True, message="Unable to update this search string, ERROR!")

@items_api.route('/item/postNewItemLocation', methods=['POST'])
def postNewItemLocation():
    if request.method == "POST":
        item_id = request.get_json()['item_id']
        location_id = request.get_json()['location_id']
        database_config = config()
        site_name = session['selected_site']
        with psycopg2.connect(**database_config) as conn:
            item_location = db.ItemLocationsTable.Payload(
                item_id,
                location_id
            )
            db.ItemLocationsTable.insert_tuple(conn, site_name, item_location.payload())
            return jsonify(error=False, message="Location was added successfully")
    return jsonify(error=True, message="Unable to save this location, ERROR!")