from flask import Blueprint, request, render_template, redirect, session, url_for, send_file, jsonify, Response, current_app, send_from_directory
import psycopg2, math, json, datetime, main, copy, requests, process, database, pprint, MyDataclasses
from config import config, sites_config
from user_api import login_required
import openfoodfacts
import postsqldb
import mimetypes, os
import pymupdf, PIL
import webpush


def create_pdf_preview(pdf_path, output_path, size=(600, 400)):
    pdf = pymupdf.open(pdf_path)
    page = pdf[0]
    file_name = os.path.basename(pdf_path).replace('.pdf', "")
    pix = page.get_pixmap()
    img = PIL.Image.frombytes("RGB", (pix.width, pix.height), pix.samples)
    output_path = output_path + file_name + '.jpg'
    img.thumbnail(size)
    img.save(output_path)
    return file_name + '.jpg'


receipt_api = Blueprint('receipt_api', __name__)

@receipt_api.route("/receipt/<id>")
@login_required
def receipt(id):
    sites = [site[1] for site in main.get_sites(session['user']['sites'])]
    database_config = config()
    with psycopg2.connect(**database_config) as conn:
        units = postsqldb.UnitsTable.getAll(conn)
    return render_template("receipts/receipt.html", id=id, current_site=session['selected_site'], sites=sites, units=units)

@receipt_api.route("/receipts")
@login_required
def receipts():
    sites = [site[1] for site in main.get_sites(session['user']['sites'])]
    return render_template("receipts/index.html", current_site=session['selected_site'], sites=sites)

@receipt_api.route('/receipts/getItems', methods=["GET"])
def getItems():
    recordset = []
    count = {'count': 0}
    if request.method == "GET":
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 10))
        site_name = session['selected_site']
        offset = (page - 1) * limit
        database_config = config()
        with psycopg2.connect(**database_config) as conn:
            payload = ("%%", limit, offset)
            recordset, count = database.getItemsWithQOH(conn, site_name, payload, convert=True)
        return jsonify({"items":recordset, "end":math.ceil(count['count']/limit), "error":False, "message":"items fetched succesfully!"})
    return jsonify({"items":recordset, "end":math.ceil(count['count']/limit), "error":True, "message":"There was an error with this GET statement"})

@receipt_api.route('/receipt/getVendors', methods=["GET"])
def getVendors():
    recordset = []
    count = 0
    if request.method == "GET":
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 10))
        site_name = session['selected_site']
        offset = (page - 1) * limit
        database_config = config()
        with psycopg2.connect(**database_config) as conn:
            payload = (limit, offset)
            recordset, count = postsqldb.VendorsTable.paginateVendors(conn, site_name, payload)
        return jsonify({"vendors":recordset, "end":math.ceil(count/limit), "error":False, "message":"items fetched succesfully!"})
    return jsonify({"vendors":recordset, "end":math.ceil(count/limit), "error":True, "message":"There was an error with this GET statement"})

@receipt_api.route('/receipt/getLinkedLists', methods=["GET"])
def getLinkedLists():
    recordset = []
    count = 0
    if request.method == "GET":
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 10))
        site_name = session['selected_site']
        offset = (page - 1) * limit
        database_config = config()
        with psycopg2.connect(**database_config) as conn:
            payload = (limit, offset)
            recordset, count = postsqldb.ItemTable.paginateLinkedLists(conn, site_name, payload)
        return jsonify({"items":recordset, "end":math.ceil(count/limit), "error":False, "message":"items fetched succesfully!"})
    return jsonify({"items":recordset, "end":math.ceil(count/limit), "error":True, "message":"There was an error with this GET statement"})

@receipt_api.route('/receipts/getReceipts', methods=["GET"])
def getReceipts():
    recordset = []
    if request.method == "GET":
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 50))
        offset = (page - 1) * limit
        site_name = session['selected_site']
        database_config = config()
        with psycopg2.connect(**database_config) as conn:
            recordset, count = database.getReceipts(conn, site_name, payload=(limit, offset), convert=True)
            return jsonify({'receipts':recordset, "end": math.ceil(count/limit), 'error': False, "message": "Get Receipts Successful!"})
    return jsonify({'receipts': recordset, "end": math.ceil(count/limit), 'error': True, "message": "Something went wrong while getting receipts!"})

@receipt_api.route('/receipts/getReceipt', methods=["GET"])
def getReceipt():
    record = []
    if request.method == "GET":
        receipt_id = int(request.args.get('id', 1))
        site_name = session['selected_site']
        database_config = config()
        with psycopg2.connect(**database_config) as conn:
            record = database.getReceiptByID(conn, site_name, payload=(receipt_id, ), convert=True)
            return jsonify({'receipt': record, 'error': False, "message": "Get Receipts Successful!"})
    return jsonify({'receipt': record,  'error': True, "message": "Something went wrong while getting receipts!"})

@receipt_api.route('/receipts/addReceipt', methods=["POST", "GET"])
def addReceipt():
    if request.method == "GET":
        user_id = session['user_id']
        site_name = session['selected_site']
        database_config = config()
        with psycopg2.connect(**database_config) as conn:
            receipt = MyDataclasses.ReceiptPayload(
                receipt_id=f"PR-{database.request_receipt_id(conn, site_name)}",
                submitted_by=user_id
            )
            database.insertReceiptsTuple(conn, site_name, receipt.payload())
        return jsonify({'error': False, "message": "Receipt Added Successful!"})
    return jsonify({'error': True, "message": "Something went wrong while adding receipt!"})

@receipt_api.route('/receipts/addSKULine', methods=["POST"])
def addSKULine():
    if request.method == "POST":
        item_id = int(request.get_json()['item_id'])
        receipt_id = int(request.get_json()['receipt_id'])

        site_name = session['selected_site']
        database_config = config()
        with psycopg2.connect(**database_config) as conn:
            item = database.getItemAllByID(conn, site_name, (item_id, ), convert=True)
            data = {
                'cost': item['item_info']['cost'],
                'expires': item['food_info']['expires']
            }
            receipt_item = MyDataclasses.ReceiptItemPayload(
                type="sku",
                receipt_id=receipt_id,
                barcode=item['barcode'],
                name=item['item_name'],
                qty=item['item_info']['uom_quantity'],
                uom=item['item_info']['uom'],
                data=data
            )
            database.insertReceiptItemsTuple(conn, site_name, receipt_item.payload())
        return jsonify({'error': False, "message": "Line added Succesfully"})
    return jsonify({'error': True, "message": "Something went wrong while add SKU line!"})

@receipt_api.route('/receipts/deleteLine', methods=["POST"])
def deleteLine():
    if request.method == "POST":
        line_id = int(request.get_json()['line_id'])
        site_name = session['selected_site']
        database_config = config()
        with psycopg2.connect(**database_config) as conn:
            database.deleteReceiptItemsTuple(conn, site_name, (line_id, ))
        
        return jsonify({'error': False, "message": "Line Deleted Succesfully"})
    return jsonify({'error': True, "message": "Something went wrong while deleting line!"})

@receipt_api.route('/receipts/denyLine', methods=["POST"])
def denyLine():
    if request.method == "POST":
        line_id = int(request.get_json()['line_id'])
        site_name = session['selected_site']
        database_config = config()
        with psycopg2.connect(**database_config) as conn:
            database.__updateTuple(conn, site_name, f"{site_name}_receipt_items", {'id': line_id, 'update': {'status': 'Denied'}})
        return jsonify({'error': False, "message": "Line Denied Succesfully"})
    return jsonify({'error': True, "message": "Something went wrong while denying line!"})

@receipt_api.route('/receipts/saveLine', methods=["POST"])
def saveLine():
    if request.method == "POST":
        line_id = int(request.get_json()['line_id'])
        payload = request.get_json()['payload']
        site_name = session['selected_site']
        database_config = config()
        with psycopg2.connect(**database_config) as conn:
            receipt_item = database.__selectTuple(conn, site_name, f"{site_name}_receipt_items", (line_id, ), convert=True)
            if 'api_data' in receipt_item['data'].keys():
                payload['data']['api_data'] = receipt_item['data']['api_data']
            database.__updateTuple(conn, site_name, f"{site_name}_receipt_items", {'id': line_id, 'update': payload})
        return jsonify({'error': False, "message": "Line Saved Succesfully"})
    return jsonify({'error': True, "message": "Something went wrong while saving line!"})

@receipt_api.route('/receipt/postLinkedItem', methods=["POST"])
def postLinkedItem():
    if request.method == "POST":
        receipt_item_id = int(request.get_json()['receipt_item_id'])
        link_list_id = int(request.get_json()['link_list_id'])
        conv_factor = float(request.get_json()['conv_factor'])

        site_name = session['selected_site']
        user_id = session['user_id']
        database_config = config()
        with psycopg2.connect(**database_config) as conn:
            receipt_item = postsqldb.ReceiptTable.select_item_tuple(conn, site_name, (receipt_item_id,))
            # get link list item
            linked_list = postsqldb.ItemTable.getItemAllByID(conn, site_name, (link_list_id, ))
            # add item to database
            if receipt_item['type'] == 'api':
                
                data = {
                    'barcode': receipt_item['barcode'], 
                    'name': receipt_item['name'], 
                    'subtype': 'FOOD'
                }
                process.postNewBlankItem(conn, site_name, user_id, data)

            name = receipt_item['name']
            if receipt_item['name'] == "unknown":
                name = linked_list['item_name']
            if receipt_item['type'] == "new sku":
                data = {
                    'barcode': receipt_item['barcode'], 
                    'name': name, 
                    'subtype': 'FOOD'
                }
                process.postNewBlankItem(conn, site_name, user_id, data)

            new_item = postsqldb.ItemTable.getItemAllByBarcode(conn, site_name, (receipt_item['barcode'], ))
            new_item = postsqldb.ItemTable.update_tuple(conn, site_name, {'id': new_item['id'], 'update':{'row_type': 'link'}})

            # add item to link list
            item_link = postsqldb.ItemLinksTable.Payload(
                new_item['barcode'],
                linked_list['id'],
                new_item,
                conv_factor
            )
            postsqldb.ItemLinksTable.insert_tuple(conn, site_name, item_link.payload())
            # update line item with link list name and item_link with link list id
            payload = {'id': receipt_item['id'], 'update': {
                'barcode': linked_list['barcode'],
                'name': linked_list['item_name'],
                'uom': linked_list['item_info']['uom']['id'],
                'qty': float(receipt_item['qty']*conv_factor),
                'type': 'sku'
            }}
            postsqldb.ReceiptTable.update_receipt_item(conn, site_name, payload)
            
        return jsonify({'error': False, "message": "Line Saved Succesfully"})
    return jsonify({'error': True, "message": "Something went wrong while saving line!"})

@receipt_api.route('/receipts/resolveLine', methods=["POST"])
def resolveLine():
    if request.method == "POST":
        line_id = int(request.get_json()['line_id'])
        site_name = session['selected_site']
        user_id = session['user_id']
        database_config = config()
        with psycopg2.connect(**database_config) as conn:
            transaction_time = datetime.datetime.now()
            receipt_item = database.__selectTuple(conn, site_name, f"{site_name}_receipt_items", (line_id, ), convert=True)
            receipt = database.getReceiptByID(conn, site_name, (receipt_item['receipt_id'], ), convert=True)
            conv_factor = 1.0
            if receipt_item['data']['expires'] is not False:
                print(receipt_item['data']['expires'])
                expiration = datetime.datetime.strptime(receipt_item['data']['expires'], "%Y-%m-%d")
            else:
                expiration = None

            if receipt_item['type'] == 'sku':
                linked_item = database.getLinkedItemByBarcode(conn, site_name, (receipt_item['barcode'], ))
                if len(linked_item) > 1:
                    conv_factor = linked_item['conv_factor']
                    receipt_item['data']['linked_child'] = linked_item['barcode']
                
            if receipt_item['type'] == 'api':
                
                data = {
                    'barcode': receipt_item['barcode'], 
                    'name': receipt_item['name'], 
                    'subtype': 'FOOD'
                }
                process.postNewBlankItem(conn, site_name, user_id, data)

            if receipt_item['type'] == "new sku":
                data = {
                    'barcode': receipt_item['barcode'], 
                    'name': receipt_item['name'], 
                    'subtype': 'FOOD'
                }
                process.postNewBlankItem(conn, site_name, user_id, data)
            
            item = database.getItemAllByBarcode(conn, site_name, (receipt_item['barcode'], ), convert=True)
            location = database.selectItemLocationsTuple(conn, site_name, (item['id'], item['logistics_info']['primary_location']['id']), convert=True)
            cost_layers: list = location['cost_layers']

            receipt_item['data']['location'] = item['logistics_info']['primary_location']['uuid']

            transaction = MyDataclasses.TransactionPayload(
                timestamp=transaction_time,
                logistics_info_id=item['logistics_info_id'],
                barcode=item['barcode'],
                name=item['item_name'],
                transaction_type="Adjust In",
                quantity=(float(receipt_item['qty'])*conv_factor),
                description=f"{receipt['receipt_id']}",
                user_id=session['user_id'],
                data=receipt_item['data']
            )

            cost_layer = MyDataclasses.CostLayerPayload(
                aquisition_date=transaction_time,
                quantity=float(receipt_item['qty']),
                cost=float(receipt_item['data']['cost']),
                currency_type="USD",
                vendor=receipt['vendor_id'],
                expires=expiration
            )

            cost_layer = database.insertCostLayersTuple(conn, site_name, cost_layer.payload(), convert=True)
            cost_layers.append(cost_layer['id'])

            quantity_on_hand = float(location['quantity_on_hand']) + float(receipt_item['qty'])

            updated_item_location_payload = (cost_layers, quantity_on_hand, item['id'], item['logistics_info']['primary_location']['id'])
            database.updateItemLocation(conn, site_name, updated_item_location_payload)

            site_location = database.__selectTuple(conn, site_name, f"{site_name}_locations", (location['location_id'], ), convert=True)

            receipt_item['data']['location'] = site_location['uuid']

            database.insertTransactionsTuple(conn, site_name, transaction.payload())
            
            database.__updateTuple(conn, site_name, f"{site_name}_receipt_items", {'id': receipt_item['id'], 'update': {'status': "Resolved"}})
    

        return jsonify({'error': False, "message": "Line Saved Succesfully"})
    return jsonify({'error': True, "message": "Something went wrong while saving line!"})

@receipt_api.route('/receipt/postVendorUpdate', methods=["POST"])
def postVendorUpdate():
    if request.method == "POST":
        receipt_id = int(request.get_json()['receipt_id'])
        vendor_id = int(request.get_json()['vendor_id'])
        site_name = session['selected_site']
        database_config = config()
        with psycopg2.connect(**database_config) as conn:
            postsqldb.ReceiptTable.update_receipt(conn, site_name, {'id': receipt_id, 'update': {'vendor_id': vendor_id}})
            return jsonify({'error': False, "message": "Line Saved Succesfully"})
    return jsonify({'error': True, "message": "Something went wrong while saving line!"})

@receipt_api.route('/receipts/resolveReceipt', methods=["POST"])
def resolveReceipt():
    if request.method == "POST":
        receipt_id = int(request.get_json()['receipt_id'])
        site_name = session['selected_site']
        user= session['user']
        database_config = config()
        with psycopg2.connect(**database_config) as conn:
            receipt = postsqldb.ReceiptTable.update_receipt(conn, site_name, {'id': receipt_id, 'update': {'receipt_status': 'Resolved'}})
            webpush.push_ntfy(title=f"Receipt '{receipt['receipt_id']}' Resolved", body=f"Receipt {receipt['receipt_id']} was completed by {user['username']}.")
            return jsonify({'error': False, "message": "Line Saved Succesfully"})
    return jsonify({'error': True, "message": "Something went wrong while saving line!"})

@receipt_api.route('/receipt/uploadfile/<receipt_id>', methods=["POST"])
def uploadFile(receipt_id):
    file = request.files['file']
    file_path = current_app.config['FILES_FOLDER'] + f"/receipts/{file.filename.replace(" ", "_")}"
    file.save(file_path)
    file_type, _ = mimetypes.guess_type(file.filename)
    preview_image = ""
    if file_type == "application/pdf":
        output_path = "static/files/receipts/previews/"
        preview_image = create_pdf_preview(file_path, output_path)

    file_size = os.path.getsize(file_path)
    database_config = config()
    site_name = session['selected_site']
    username = session['user']['username']
    with psycopg2.connect(**database_config) as conn:
        files = postsqldb.ReceiptTable.select_tuple(conn, site_name, (receipt_id, ))['files']
        files[file.filename.replace(" ", "_")] = {'file_path': file.filename.replace(" ", "_"), 'file_type': file_type, 'file_size': file_size, 'uploaded_by': username, 'preview_image': preview_image}
        postsqldb.ReceiptTable.update_receipt(conn, site_name, {'id': receipt_id, 'update': {'files': files}})
    
    return jsonify({})

@receipt_api.route('/receipt/getFile/<file_name>')
def getFile(file_name):
    return send_from_directory('static/files/receipts', file_name)

@receipt_api.route('/receipts/checkAPI', methods=["POST"])
def checkAPI():
    if request.method == "POST":
        line_id = int(request.get_json()['line_id'])
        barcode = request.get_json()['barcode']
        site_name = session['selected_site']
        database_config = config()
        with psycopg2.connect(**database_config) as conn:
            print(barcode, line_id)
            api_response, api_data = get_open_facts(barcode)
            if api_response:
                receipt_item = database.__selectTuple(conn, site_name, f"{site_name}_receipt_items", (line_id, ), convert=True)
                item_data = receipt_item['data']
                item_data['api_data'] = api_data
                database.__updateTuple(conn, site_name, f"{site_name}_receipt_items", 
                                       {'id': line_id, 'update': {
                                           'type': 'api',
                                           'data': item_data,
                                           'name': api_data['product_name']
                                       }})
                return jsonify({'error': False, "message": "Line updated for API, Succesfully"})
            else:
                return jsonify({'error': True, "message": "Item not in WorldFoodFacts!"})
        return jsonify({'error': False, "message": "Line Saved Succesfully"})
    return jsonify({'error': True, "message": "Something went wrong while saving line!"})

open_food_api = openfoodfacts.API(user_agent="MyAwesomeApp/1.0")

open_food_enabled = True

def get_open_facts(barcode):
    if open_food_enabled:
        barcode: str = barcode.replace('%', "")
        data = open_food_api.product.get(barcode)
        if data != None:
            return True, data
    return False, {}