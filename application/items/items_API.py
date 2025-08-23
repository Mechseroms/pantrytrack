# 3RD PARTY IMPORTS
from flask import (
    Blueprint, request, render_template, redirect, session, url_for, send_file, jsonify, Response
    )
import psycopg2
import math
import io
import csv
import datetime

# APPLICATION IMPORTS
from config import config
from application.access_module import access_api
import application.postsqldb as db
from application.items import database_items
from application.items import items_processes
import application.database_payloads as dbPayloads

items_api = Blueprint('items_api', __name__, template_folder="templates", static_folder="static")

def update_session_user():
  database_config = config()
  with psycopg2.connect(**database_config) as conn:
      user = db.LoginsTable.get_washed_tuple(conn, (session['user_id'],))
      session['user'] = user

# ROOT TEMPLATE ROUTES
@items_api.route("/")
@access_api.login_required
def items():
    update_session_user()
    sites = [site[1] for site in db.get_sites(session['user']['sites'])]
    return render_template("index.html", 
                           current_site=session['selected_site'], 
                           sites=sites)

@items_api.route("/<id>")
@access_api.login_required
def item(id):
    sites = [site[1] for site in db.get_sites(session['user']['sites'])]
    database_config = config()
    with psycopg2.connect(**database_config) as conn:
        units = db.UnitsTable.getAll(conn)
    return render_template("item_new.html", id=id, units=units, current_site=session['selected_site'], sites=sites)

@items_api.route("/transaction")
@access_api.login_required
def transaction():
  sites = [site[1] for site in db.get_sites(session['user']['sites'])]
  database_config = config()
  with psycopg2.connect(**database_config) as conn:
      units = db.UnitsTable.getAll(conn)
  return render_template("transaction.html", units=units, current_site=session['selected_site'], sites=sites, proto={'referrer': request.referrer})

@items_api.route("/transactions/<id>")
@access_api.login_required
def transactions(id):
  sites = [site[1] for site in db.get_sites(session['user']['sites'])]
  return render_template("transactions.html", id=id, current_site=session['selected_site'], sites=sites)

@items_api.route("/<parent_id>/itemLink/<id>")
@access_api.login_required
def itemLink(parent_id, id):
  sites = [site[1] for site in db.get_sites(session['user']['sites'])]
  return render_template("itemlink.html", current_site=session['selected_site'], sites=sites, proto={'referrer': request.referrer}, id=id)

# API CALLS
@items_api.route("/getTransactions", methods=["GET"])
@access_api.login_required
def getTransactions():
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
@access_api.login_required
def getTransaction():
    transaction = ()
    if request.method == "GET":
        id = int(request.args.get('id', 1))
        site_name = session['selected_site']
        transaction = database_items.getTransaction(site_name, (id, ))
        return jsonify({"transaction": transaction, "error": False, "message": ""})
    return jsonify({"transaction": transaction,  "error": True, "message": f"method {request.method} is not allowed."})

@items_api.route("/getItem", methods=["GET"])
@access_api.login_required
def get_item():
    if request.method == "GET":
        id = int(request.args.get('id', 1))
        site_name = session['selected_site']
        item = ()
        item = database_items.getItemAllByID(site_name, (id, ))
        return jsonify({'item': item, 'error': False, 'message': ''})
    return jsonify({'item': item, 'error': True, 'message': f'method {request.method} not allowed.'})

@items_api.route("/getItemsWithQOH", methods=['GET'])
@access_api.login_required
def pagninate_items():
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
@access_api.login_required
def getModalItems():
    recordset, count = tuple(), 0
    if request.method == "GET":
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 10))
        search_string = request.args.get('search_string', '')
        site_name = session['selected_site']
        offset = (page - 1) * limit
        recordset, count = database_items.getModalSKUs(site_name, (search_string, limit, offset))
        return jsonify({"items":recordset, "end":math.ceil(count/limit), "error":False, "message":"items fetched succesfully!"})
    return jsonify({"items":recordset, "end":math.ceil(count/limit), "error":True, "message": f"method {request.method} is not allowed."})

@items_api.route('/getPrefixes', methods=["GET"])
@access_api.login_required
def getModalPrefixes():
    recordset = []
    count = 0
    if request.method == "GET":
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 10))
        site_name = session['selected_site']
        offset = (page - 1) * limit
        recordset, count = database_items.getPrefixes(site_name, (limit, offset))
        return jsonify({"prefixes":recordset, "end":math.ceil(count/limit), "error":False, "message":"items fetched succesfully!"})
    return jsonify({"prefixes":recordset, "end":math.ceil(count/limit), "error":True, "message":f"method {request.method} is not allowed!"})

@items_api.route('/getZonesBySku', methods=["GET"])
@access_api.login_required
def getZonesbySku():
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
@access_api.login_required
def getLocationsBySkuZone():
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
@access_api.login_required
def getBrands():
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
@access_api.login_required
def updateItem():
    if request.method == "POST":
        id = request.get_json()['id']
        data = request.get_json()['data']
        site_name = session['selected_site']
        database_items.postUpdateItem(site_name, {'id': id, 'update': data, 'user_id': session['user_id']})
        return jsonify({'error': False, 'message': f'Item was updated successfully!'})
    return jsonify({'error': True, 'message': f'method {request.method} is not allowed!'})

@items_api.route('/api/inactivateItem', methods=['POST'])
@access_api.login_required
def inactivateItem():
    if request.method == "POST":
        id = request.get_json()['item_id']
        data = request.get_json()['data']
        site_name = session['selected_site']
        database_items.postUpdateItem(site_name, {'id': id, 'update': data, 'user_id': session['user_id']})
        return jsonify({'error': False, 'message': f'Item was updated successfully!'})
    return jsonify({'error': True, 'message': f'method {request.method} is not allowed!'})

@items_api.route('/updateItemLink', methods=['POST'])
@access_api.login_required
def updateItemLink():
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
@access_api.login_required
def getPossibleLocations():
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
@access_api.login_required
def getLinkedItem():
    linked_item = {}
    if request.method == "GET":
        id = int(request.args.get('id', 1))
        site_name = session['selected_site']
        linked_item = database_items.getItemLink(site_name, (id, ))
        return jsonify({'linked_item': linked_item, 'error': False, 'message': 'Linked Item added!!'})
    return jsonify({'linked_item': linked_item, 'error': True, 'message': f'method {request.method} not allowed'})

@items_api.route('/addLinkedItem', methods=["POST"])
@access_api.login_required 
def addLinkedItem():
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
@access_api.login_required
def addBlankItem():
    if request.method == "POST":
        data = {
            'barcode': request.get_json()['barcode'], 
            'name': request.get_json()['name'], 
            'subtype': request.get_json()['subtype']
            }
        site_name = session['selected_site']
        user_id = session['user_id']
        
        items_processes.postNewBlankItem(site_name, user_id, data)
      
        return jsonify({'error': False, 'message': 'Item added!!'})
    return jsonify({'error': True, 'message': 'These was an error with adding Item!'})

@items_api.route('/addSKUPrefix', methods=["POST"])
@access_api.login_required
def addSKUPrefix():
    if request.method == "POST":
        site_name = session['selected_site']
        prefix = dbPayloads.SKUPrefixPayload(
            request.get_json()['uuid'],
            request.get_json()['name'], 
            request.get_json()['description']
        )
        database_items.insertSKUPrefixtuple(site_name, prefix.payload())
        return jsonify({'error': False, 'message': 'Prefix added!!'})
    return jsonify({'error': True, 'message': 'These was an error with adding this Prefix!'})

@items_api.route('/addConversion', methods=['POST'])
@access_api.login_required
def addConversion():
    
    if request.method == "POST":
        item_id = request.get_json()['parent_id']
        uom_id = request.get_json()['uom_id']
        conv_factor = request.get_json()['conv_factor']
        site_name = session['selected_site']

        conversion = dbPayloads.ConversionPayload(
            item_id, uom_id, conv_factor
        )

        database_items.insertConversionTuple(site_name, conversion.payload())
            
        return jsonify(error=False, message="Conversion was added successfully")
    return jsonify(error=True, message="Unable to save this conversion, ERROR!")

@items_api.route('/deleteConversion', methods=['POST'])
@access_api.login_required
def deleteConversion():
    if request.method == "POST":
        conversion_id = request.get_json()['conversion_id']
        site_name = session['selected_site']
        database_items.deleteConversionTuple(site_name, (conversion_id,))
        return jsonify(error=False, message="Conversion was deleted successfully")
    return jsonify(error=True, message="Unable to delete this conversion, ERROR!")

@items_api.route('/updateConversion', methods=['POST'])
@access_api.login_required
def updateConversion():
    if request.method == "POST":
        conversion_id = request.get_json()['conversion_id']
        update_dictionary = request.get_json()['update']
        site_name = session['selected_site']
        database_items.updateConversionTuple(site_name, {'id': conversion_id, 'update': update_dictionary})
        return jsonify(error=False, message="Conversion was updated successfully")
    return jsonify(error=True, message="Unable to save this conversion, ERROR!")

@items_api.route('/addPrefix', methods=['POST'])
@access_api.login_required
def addPrefix():
    if request.method == "POST":
        item_info_id = request.get_json()['parent_id']
        prefix_id = request.get_json()['prefix_id']
        site_name = session['selected_site']
        prefixes = database_items.getItemInfoTuple(site_name, (item_info_id,))['prefixes']
        prefixes.append(prefix_id)
        database_items.updateItemInfoTuple(site_name, {'id': item_info_id, 'update':{'prefixes': prefixes}})
        return jsonify(error=False, message="Prefix was added successfully")
    return jsonify(error=True, message="Unable to save this prefix, ERROR!")

@items_api.route('/deletePrefix', methods=['POST'])
@access_api.login_required
def deletePrefix():
    if request.method == "POST":
        item_info_id = request.get_json()['item_info_id']
        prefix_id = request.get_json()['prefix_id']
        site_name = session['selected_site']
        prefixes = database_items.getItemInfoTuple(site_name, (item_info_id,))['prefixes']
        prefixes.remove(prefix_id)
        database_items.updateItemInfoTuple(site_name, {'id': item_info_id, 'update':{'prefixes': prefixes}})
        return jsonify(error=False, message="Prefix was deleted successfully")
    return jsonify(error=True, message="Unable to delete this prefix, ERROR!")

@items_api.route('/refreshSearchString', methods=['POST'])
@access_api.login_required
def refreshSearchString():
    if request.method == "POST":
        item_id = request.get_json()['item_id']
        site_name = session['selected_site']
        item = database_items.getItemAllByID(site_name, (item_id,))
        search_string = items_processes.createSearchStringFromItem(item)
        database_items.postUpdateItemByID(site_name, {'id': item_id, 'update':{'search_string': search_string}})
        return jsonify(error=False, message="Search String was updated successfully")
    return jsonify(error=True, message="Unable to update this search string, ERROR!")

@items_api.route('/postNewItemLocation', methods=['POST'])
@access_api.login_required
def postNewItemLocation():
    if request.method == "POST":
        item_id = request.get_json()['item_id']
        location_id = request.get_json()['location_id']
        site_name = session['selected_site']
        item_location = dbPayloads.ItemLocationPayload(item_id, location_id)
        database_items.insertItemLocationsTuple(site_name, item_location.payload())
        return jsonify(error=False, message="Location was added successfully")
    return jsonify(error=True, message="Unable to save this location, ERROR!")

@items_api.route("/getItemLocations", methods=["GET"])
@access_api.login_required
def getItemLocations():
    recordset = []
    count = 0
    if request.method == "GET":
        item_id = int(request.args.get('id', 1))
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 10))
        site_name = session['selected_site']
        offset = (page - 1) * limit
        recordset, count = database_items.getItemLocations(site_name, (item_id, limit, offset))
        return jsonify({"locations":recordset, "end":math.ceil(count/limit), "error":False, "message":"item fetched succesfully!"})
    return jsonify({"locations":recordset, "end": math.ceil(count/limit), "error":True, "message":"There was an error with this GET statement"})

@items_api.route('/postTransaction', methods=["POST"])
@access_api.login_required
def post_transaction():
    if request.method == "POST":
        result = items_processes.postAdjustment(
            site_name=session['selected_site'],
            user_id=session['user_id'],
            data=dict(request.json)
        )  
        return jsonify(result)
    return jsonify({"error":True, "message":"There was an error with this POST statement"})


@items_api.route('/api/addBarcode', methods=['POST'])
@access_api.login_required
def addBarcode():
    """API endpoint to add a barcode

    Returns:
        Response: returns a status and status message to requestor
    """
    if request.method == "POST":
        site_name = session['selected_site']
        barcode_tuple = dbPayloads.BarcodesPayload(
            barcode = request.get_json()['barcode'],
            item_uuid= request.get_json()['item_uuid'],
            in_exchange= request.get_json()['in_exchange'],
            out_exchange= request.get_json()['out_exchange'],
            descriptor= request.get_json()['descriptor']
        )
        try:
            database_items.insertBarcodesTuple(site_name, barcode_tuple.payload())
            return jsonify(status=201, message=f"Barcode {request.get_json()['barcode']} was added successfully.")
        except Exception as error:
            return jsonify(status=400, message=str(error))
        
    return jsonify(status=405, message=f"The request method: {request.method} is not allowed on this endpoint!")

@items_api.route('/api/saveBarcode', methods=["POST"])
@access_api.login_required
def saveBarcode():
    """API endpoint to update a barcode

    Returns:
        Response: returns a status and status message to requestor
    """
    if request.method == "POST":
        payload = {'barcode': request.get_json()['barcode'], 'update': request.get_json()['update']}
        site_name = session['selected_site']
        try:
            database_items.updateBarcodesTuple(site_name, payload)
            return jsonify(status=201, message=f"{payload['barcode']} was updated successfully.")
        except Exception as error:
            return jsonify(status=400, message=str(error))
    return jsonify(status=405, message=f"The request method: {request.method} is not allowed on this endpoint!")

@items_api.route('/api/deleteBarcode', methods=["POST"])
@access_api.login_required
def deleteBarcode():
    """API endpoint to delete a barcode

    Returns:
        Response: returns a status and status message to requestor
    """
    if request.method == "POST":
        barcode = request.get_json()['barcode']
        site_name = session['selected_site']
        try:
            database_items.deleteBarcodesTuple(site_name, (barcode,))
            return jsonify(status=201, message=f"{barcode} was deleted successfully.")
        except Exception as error:
            return jsonify(status=400, message=str(error))
    return jsonify(status=405, message=f"The request method: {request.method} is not allowed on this endpoint!")

@items_api.route('/download_csv', methods=["GET"])
def downloadItemsCSV():
    if request.method == "GET":
        site_name = session['selected_site']
        records, headers, types = database_items.getItemsAll(site_name, convert=False)
        si = io.StringIO()
        writer = csv.writer(si)
        writer.writerow(headers)
        writer.writerow(types)
        writer.writerows(records)
        output = si.getvalue()
        filename = f"{site_name}_items_{str(datetime.datetime.now())}.csv"
        response = Response(
            output,
            mimetype='text/csv',
            headers={"Content-Disposition": f"attachment;filename={filename}"}
        )
        return response
    return jsonify(status=405, message=f"The request method: {request.method} is not allowed on this endpoint!")