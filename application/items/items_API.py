# 3rd Party imports
from flask import (
    Blueprint, request, render_template, redirect, session, url_for, send_file, jsonify, Response
    )
import psycopg2
import math 
import json
import datetime
import copy
import requests
import pprint

# applications imports
from config import config, sites_config
from main import unfoldCostLayers
import process
import database
import main
import MyDataclasses
from user_api import login_required
import application.postsqldb as db
from application.items import database_items
from application.items import items_processes

items_api = Blueprint('items_api', __name__, template_folder="templates", static_folder="static")


def update_session_user():
    database_config = config()
    with psycopg2.connect(**database_config) as conn:
        user = db.LoginsTable.get_washed_tuple(conn, (session['user_id'],))
        session['user'] = user

@items_api.route("/")
@login_required
def items():
    update_session_user()
    sites = [site[1] for site in main.get_sites(session['user']['sites'])]
    return render_template("index.html", 
                           current_site=session['selected_site'], 
                           sites=sites)

@items_api.route("/<id>")
@login_required
def item(id):
    sites = [site[1] for site in main.get_sites(session['user']['sites'])]
    database_config = config()
    with psycopg2.connect(**database_config) as conn:
        units = db.UnitsTable.getAll(conn)
    return render_template("item_new.html", id=id, units=units, current_site=session['selected_site'], sites=sites)

@items_api.route("/transaction")
@login_required
def transaction():
    sites = [site[1] for site in main.get_sites(session['user']['sites'])]
    database_config = config()
    with psycopg2.connect(**database_config) as conn:
        units = db.UnitsTable.getAll(conn)
    return render_template("transaction.html", units=units, current_site=session['selected_site'], sites=sites, proto={'referrer': request.referrer})

@items_api.route("/transactions/<id>")
@login_required
def transactions(id):
    """This is the main endpoint to reach the webpage for an items transaction history
    ---
    parameters:
      - name: id
        in: path
        type: integer
        required: true
        default: all
    responses:
      200:
        description: Returns the transactions.html webpage for the item with passed ID
    """
    sites = [site[1] for site in main.get_sites(session['user']['sites'])]
    return render_template("transactions.html", id=id, current_site=session['selected_site'], sites=sites)

@items_api.route("/<parent_id>/itemLink/<id>")
@login_required
def itemLink(parent_id, id):
    sites = [site[1] for site in main.get_sites(session['user']['sites'])]
    return render_template("itemlink.html", current_site=session['selected_site'], sites=sites, proto={'referrer': request.referrer}, id=id)

@items_api.route("/getTransactions", methods=["GET"])
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

@items_api.route("/getTransaction", methods=["GET"])
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

@items_api.route("/getItem", methods=["GET"])
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

@items_api.route("/getItemsWithQOH", methods=['GET'])
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

@items_api.route('/getModalItems', methods=["GET"])
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

@items_api.route('/getPrefixes', methods=["GET"])
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

@items_api.route('/getZonesBySku', methods=["GET"])
@login_required
def getZonesbySku():
    """ GET zones by sku by passing page, limit, item_id
    ---
    parameters:
        - in: query
          name: page
          schema:
            type: integer
            minimum: 1
            default: 1
          description: page of the records to GET
        - in: query
          name: limit
          schema:
            type: integer
            minimum: 1
            default: 10
          description: number of records to grab from the system
        - in: query
          name: item_id
          schema:
            type: integer
            minimum: 1
            default: 1
          description: item_id to pull zones for
    responses:
        200:
            description: Zones received successfully.
    """
    zones, count = [], 0
    if request.method == "GET":
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 10))
        item_id = int(request.args.get('item_id'))
        site_name = session['selected_site']
        offset = (page - 1) * limit
        zones, count = database_items.paginateZonesBySku(site_name, (item_id, limit, offset))
        return jsonify({'zones': zones, 'endpage': math.ceil(count/limit), 'error':False, 'message': f''})
    return jsonify({'zones': zones, 'endpage': math.ceil(count/limit), 'error':False, 'message': f'method {request.method} not allowed.'})

@items_api.route('/getLocationsBySkuZone', methods=['GET'])
@login_required
def getLocationsBySkuZone():
    """ GET locations by sku by passing page, limit, item_id, zone_id
    ---
    parameters:
        - in: query
          name: page
          schema:
            type: integer
            minimum: 1
            default: 1
          description: page of the records to GET
        - in: query
          name: limit
          schema:
            type: integer
            minimum: 1
            default: 10
          description: number of records to grab from the system
        - in: query
          name: item_id
          schema:
            type: integer
            minimum: 1
            default: 1
          description: item_id to pull locations for zone_id
        - in: query
          name: zone_id
          schema:
            type: integer
            minimum: 1
            default: 1
          description: zone_id to pull locations for item_id
    responses:
        200:
            description: Locations received successfully.
    """
    locations, count = [], 0
    if request.method == "GET":
        zone_id = int(request.args.get('zone_id', 1))
        part_id = int(request.args.get('part_id', 1))
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 1))
        offset = (page-1)*limit
        site_name = session['selected_site']
        locations, count = database_items.paginateLocationsBySkuZone(site_name, (part_id, zone_id, limit, offset))
        return jsonify({'locations': locations, 'endpage': math.ceil(count/limit), 'error': False, 'message': f''})
    return jsonify({'locations': locations, 'endpage': math.ceil(count/limit), 'error': True, 'message': f'method {request.method} is not allowed.'})

@items_api.route('/getBrands', methods=['GET'])
@login_required
def getBrands():
    """ GET brands from the system by passing page, limit
    ---
    parameters:
        - in: query
          name: page
          schema:
            type: integer
            minimum: 1
            default: 1
          description: page of the records to GET
        - in: query
          name: limit
          schema:
            type: integer
            minimum: 1
            default: 10
          description: number of records to grab from the system
    responses:
        200:
            description: Brands received successfully.
    """
    brands, count = [], 0
    if request.method == "GET":
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 1))
        offset = (page-1)*limit
        site_name = session['selected_site']
        brands, count = database_items.paginateBrands(site_name, (limit, offset))
        return jsonify({'brands': brands, 'endpage': math.ceil(count/limit), 'error': False, 'message': f''})
    return jsonify({'brands': brands, 'endpage': math.ceil(count/limit), 'error': True, 'message': f'method {request.method} is not allowed.'})


@items_api.route('/updateItem', methods=['POST'])
@login_required
def updateItem():
    """ POST update to item in the system by passing item_id, data
    ---
    parameters:
        - in: query
          name: item_id
          schema:
            type: integer
            minimum: 1
            default: 1
          description: item_id that the POST targets
        - in: header
          name: data
          description: data to update in system
    responses:
        200:
            description: item updated successfully.
    """
    if request.method == "POST":
        id = request.get_json()['id']
        data = request.get_json()['data']
        site_name = session['selected_site']
        database_items.postUpdateItem(site_name, {'id': id, 'update': data, 'user_id': session['user_id']})
        return jsonify({'error': False, 'message': f'Item was updated successfully!'})
    return jsonify({'error': True, 'message': f'method {request.method} is not allowed!'})

@items_api.route('/updateItemLink', methods=['POST'])
@login_required
def updateItemLink():
    """ UPDATE item link by passing id, conv_factor, barcode, old_conv
    ---
    parameters:
        - in: query
          name: id
          schema:
            type: integer
            minimum: 1
            default: 1
          required: true
          description: Id of item link to update
        - in: query
          name: conv_factor
          schema:
            type: integer
          required: true
          description: new conversion factor of item_link id
        - in: query
          name: barcode
          schema:
            type: string
          required: true
          description: barcode of item_link id
        - in: query
          name: old_conv
          schema:
            type: integer
          required: true
          description: old conversion factor of item_link id
    responses:
        200:
            description: Item Link updated successfully.
    """
    if request.method == "POST":
        id = request.get_json()['id']
        conv_factor = request.get_json()['conv_factor']
        barcode = request.get_json()['barcode']
        old_conv_factor = request.get_json()['old_conv']
        site_name = session['selected_site']
        payload = {'id': id, 'update':{'conv_factor': conv_factor}, 'barcode': barcode, 'old_conv_factor': old_conv_factor, 'user_id':session['user_id'] }
        database_items.postUpdateItemLink(site_name, payload)
        return jsonify({'error':False, 'message': "Linked Item was updated successfully"})
    return jsonify({'error': True, 'message': f"method {request.method} not allowed."})


@items_api.route('/getPossibleLocations', methods=["GET"])
@login_required
def getPossibleLocations():
    """ GET locations with zones by passing a page and limit
    ---
    parameters:
        - in: query
          name: page
          schema:
            type: interger
            minimum: 1
            default: 1
          description: page in the records to GET
        - in: query
          name: limit
          schema:
            type: interger
            minimum: 1
            default: 1
          description: number of records to GET
    responses:
        200:
            description: Locations GET successful.
    """
    locations, count = (), 0
    if request.method == "GET":
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 1))
        offset = (page-1)*limit
        site_name = session['selected_site']
        locations, count = database_items.paginateLocationsWithZone(site_name, (limit, offset))
        return jsonify({'locations': locations, 'end':math.ceil(count/limit), 'error':False, 'message': f'Locations received successfully!'})
    return jsonify({'locations': locations, 'end':math.ceil(count/limit), 'error':True, 'message': f'method {request.method} not allowed.'})

@items_api.route('/getLinkedItem', methods=["GET"])
@login_required
def getLinkedItem():
    """ GET itemlink from system by passing an ID
    ---
    parameters:
        - in: query
          name: id
          schema:
            type: integer
            default: 1
          required: true
          description: item link to get from the system
    responses:
        200:
            description: Item Link GET successful.
    """
    linked_item = {}
    if request.method == "GET":
        id = int(request.args.get('id', 1))
        site_name = session['selected_site']
        linked_item = database_items.getItemLink(site_name, (id, ))
        return jsonify({'linked_item': linked_item, 'error': False, 'message': 'Linked Item added!!'})
    return jsonify({'linked_item': linked_item, 'error': True, 'message': f'method {request.method} not allowed'})

@items_api.route('/addLinkedItem', methods=["POST"])
@login_required 
def addLinkedItem():
    """ POST a link between items by passing a parent_id, a child_id, conv_factor
    ---
    parameters:
        - in: query
          name: parent_id
          schema:
            type: integer
            default: 1
          required: true
          description: id to linked list item
        - in: query
          name: child_id
          schema:
            type: integer
            default: 1
          required: true
          description: id to item to be linked to list.
        - in: query
          name: conv_factor
          schema:
            type: integer
            default: 1
          required: true
          description: integer factor between child id to parent id.
    responses:
        200:
            description: Items linked successfully.
    """
    if request.method == "POST":
        parent_id = request.get_json()['parent_id']
        child_id = request.get_json()['child_id']
        conv_factor = request.get_json()['conv_factor']
        site_name = session['selected_site']
        user_id = session['user_id']
        
        items_processes.postLinkedItem(site_name, {
            'parent_id': parent_id,
            'child_id': child_id,
            'user_id': user_id,
            'conv_factor': conv_factor
        })
            
        return jsonify({'error': False, 'message': 'Linked Item added!!'})
    return jsonify({'error': True, 'message': 'These was an error with adding to the linked list!'})
    
@items_api.route('/addBlankItem', methods=["POST"])
def addBlankItem():
    if request.method == "POST":
        data = {
            'barcode': request.get_json()['barcode'], 
            'name': request.get_json()['name'], 
            'subtype': request.get_json()['subtype']
            }
        database_config = config()
        site_name = session['selected_site']
        user_id = session['user_id']
        
        items_processes.postNewBlankItem(site_name, user_id, data)
      
        return jsonify({'error': False, 'message': 'Item added!!'})
    return jsonify({'error': True, 'message': 'These was an error with adding Item!'})

@items_api.route('/addSKUPrefix', methods=["POST"])
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

@items_api.route('/addConversion', methods=['POST'])
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

@items_api.route('/deleteConversion', methods=['POST'])
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

@items_api.route('/updateConversion', methods=['POST'])
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

@items_api.route('/addPrefix', methods=['POST'])
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

@items_api.route('/deletePrefix', methods=['POST'])
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

@items_api.route('/refreshSearchString', methods=['POST'])
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

@items_api.route('/postNewItemLocation', methods=['POST'])
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