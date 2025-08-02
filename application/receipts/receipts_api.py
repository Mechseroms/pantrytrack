# 3RD PARTY IMPORTS
from flask import (Blueprint, request, render_template, session, jsonify, current_app, send_from_directory)
import math
import postsqldb
import mimetypes
import os

# APPLICATION IMPORTS
import webpush
from user_api import login_required
from application import postsqldb, database_payloads
from application.receipts import receipts_processes, receipts_database


receipt_api = Blueprint('receipt_api', __name__, template_folder='templates', static_folder='static')


# ROOT TEMPLATE ROUTES
@receipt_api.route("/")
@login_required
def receipts():
    sites = [site[1] for site in postsqldb.get_sites(session['user']['sites'])]
    return render_template("receipts_index.html", current_site=session['selected_site'], sites=sites)

@receipt_api.route("/<id>")
@login_required
def receipt(id):
    sites = [site[1] for site in postsqldb.get_sites(session['user']['sites'])]
    units = postsqldb.get_units_of_measure()
    return render_template("receipt.html", id=id, current_site=session['selected_site'], sites=sites, units=units)


# API ROUTES
# Added to Database
@receipt_api.route('/api/getItems', methods=["GET"])
def getItems():
    recordset = []
    count = {'count': 0}
    if request.method == "GET":
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 10))
        site_name = session['selected_site']
        offset = (page - 1) * limit
        sort_order = "ID ASC"
        payload = ("%%", limit, offset, sort_order)
        recordset, count = receipts_database.getItemsWithQOH(site_name, payload)
        return jsonify({"items":recordset, "end":math.ceil(count['count']/limit), "error":False, "message":"items fetched succesfully!"})
    return jsonify({"items":recordset, "end":math.ceil(count['count']/limit), "error":True, "message":"There was an error with this GET statement"})

# Added to Database
@receipt_api.route('/api/getVendors', methods=["GET"])
def getVendors():
    recordset = []
    count = 0
    if request.method == "GET":
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 10))
        site_name = session['selected_site']
        offset = (page - 1) * limit
        recordset, count = receipts_database.paginateVendorsTuples(site_name, payload=(limit, offset))
        return jsonify({"vendors":recordset, "end":math.ceil(count/limit), "error":False, "message":"items fetched succesfully!"})
    return jsonify({"vendors":recordset, "end":math.ceil(count/limit), "error":True, "message":"There was an error with this GET statement"})

# Added to Database
@receipt_api.route('/api/getLinkedLists', methods=["GET"])
def getLinkedLists():
    recordset = []
    count = 0
    if request.method == "GET":
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 10))
        site_name = session['selected_site']
        offset = (page - 1) * limit
        recordset, count = receipts_database.paginateLinkedLists(site_name, payload=(limit, offset))
        return jsonify({"items":recordset, "end":math.ceil(count/limit), "error":False, "message":"items fetched succesfully!"})
    return jsonify({"items":recordset, "end":math.ceil(count/limit), "error":True, "message":"There was an error with this GET statement"})

# Added to database
@receipt_api.route('/api/getReceipts', methods=["GET"])
def getReceipts():
    recordset = []
    if request.method == "GET":
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 50))
        offset = (page - 1) * limit
        site_name = session['selected_site']
        recordset, count = receipts_database.paginateReceiptsTuples(site_name, payload=(limit, offset))
        return jsonify({'receipts':recordset, "end": math.ceil(count/limit), 'error': False, "message": "Get Receipts Successful!"})
    return jsonify({'receipts': recordset, "end": math.ceil(count/limit), 'error': True, "message": "Something went wrong while getting receipts!"})

# Added to database
@receipt_api.route('/api/getReceipt', methods=["GET"])
def getReceipt():
    receipt = []
    if request.method == "GET":
        receipt_id = int(request.args.get('id', 1))
        site_name = session['selected_site']
        receipt = receipts_database.getReceiptByID(site_name, (receipt_id, ))
        return jsonify({'receipt': receipt, 'error': False, "message": "Get Receipts Successful!"})
    return jsonify({'receipt': receipt,  'error': True, "message": "Something went wrong while getting receipts!"})

# added to database
@receipt_api.route('/api/addReceipt', methods=["POST", "GET"])
def addReceipt():
    if request.method == "GET":
        user_id = session['user_id']
        site_name = session['selected_site']
        receipt = database_payloads.ReceiptPayload(
            receipt_id=f"PR-{receipts_database.requestNextReceiptID(site_name)}",
            submitted_by=user_id
        )
        receipts_database.insertReceiptsTuple(site_name, receipt.payload())
        return jsonify({'error': False, "message": "Receipt Added Successful!"})
    return jsonify({'error': True, "message": "Something went wrong while adding receipt!"})

# Added to Database
@receipt_api.route('/api/addSKULine', methods=["POST"])
def addSKULine():
    if request.method == "POST":
        item_id = int(request.get_json()['item_id'])
        receipt_id = int(request.get_json()['receipt_id'])

        site_name = session['selected_site']
        item = receipts_database.getItemAllByID(site_name, (item_id, ))
        data = {
            'cost': item['item_info']['cost'],
            'expires': item['food_info']['expires']
        }
        receipt_item = database_payloads.ReceiptItemPayload(
            type="sku",
            receipt_id=receipt_id,
            barcode=item['barcode'],
            name=item['item_name'],
            qty=item['item_info']['uom_quantity'],
            uom=item['item_info']['uom']['id'],
            data=data
        )
        receipts_database.insertReceiptItemsTuple(site_name, receipt_item.payload())
        return jsonify({'error': False, "message": "Line added Succesfully"})
    return jsonify({'error': True, "message": "Something went wrong while add SKU line!"})

# Added to Database
@receipt_api.route('/api/deleteLine', methods=["POST"])
def deleteLine():
    if request.method == "POST":
        line_id = int(request.get_json()['line_id'])
        site_name = session['selected_site']
        receipts_database.deleteReceiptItemsTuple(site_name, (line_id, ))
        return jsonify({'error': False, "message": "Line Deleted Succesfully"})
    return jsonify({'error': True, "message": "Something went wrong while deleting line!"})

# Added to Database
@receipt_api.route('/api/denyLine', methods=["POST"])
def denyLine():
    if request.method == "POST":
        line_id = int(request.get_json()['line_id'])
        site_name = session['selected_site']
        receipts_database.updateReceiptItemsTuple(site_name, {'id': line_id, 'update': {'status': 'Denied'}})
        return jsonify({'error': False, "message": "Line Denied Succesfully"})
    return jsonify({'error': True, "message": "Something went wrong while denying line!"})

# Added to database
@receipt_api.route('/api/saveLine', methods=["POST"])
def saveLine():
    if request.method == "POST":
        line_id = int(request.get_json()['line_id'])
        payload = request.get_json()['payload']
        site_name = session['selected_site']
        receipt_item = receipts_database.selectReceiptItemsTuple(site_name, (line_id, ))
        if 'api_data' in receipt_item['data'].keys():
            payload['data']['api_data'] = receipt_item['data']['api_data']
        receipts_database.updateReceiptItemsTuple(site_name, {'id': line_id, 'update': payload})
        return jsonify({'error': False, "message": "Line Saved Succesfully"})
    return jsonify({'error': True, "message": "Something went wrong while saving line!"})

# Added to Process and database!
@receipt_api.route('/api/postLinkedItem', methods=["POST"])
def postLinkedItem():
    if request.method == "POST":
        receipt_item_id = int(request.get_json()['receipt_item_id'])
        link_list_id = int(request.get_json()['link_list_id'])
        conv_factor = float(request.get_json()['conv_factor'])

        site_name = session['selected_site']
        user_id = session['user_id']

        payload = {
            'receipt_item_id': receipt_item_id,
            'linked_list_id': link_list_id,
            'conv_factor': conv_factor
        }

        receipts_processes.linkItem(site_name, user_id, payload)
            
        return jsonify({'error': False, "message": "Line Saved Succesfully"})
    return jsonify({'error': True, "message": "Something went wrong while saving line!"})
# Added to processes and Database
@receipt_api.route('/api/resolveLine', methods=["POST"])
def resolveLine():
    if request.method == "POST":
        line_id = int(request.get_json()['line_id'])
        site_name = session['selected_site']
        user_id = session['user_id']
        payload = {'line_id': line_id}
        receipts_processes.postLine(site_name, user_id, payload)
        return jsonify({'error': False, "message": "Line Saved Succesfully"})
    return jsonify({'error': True, "message": "Something went wrong while saving line!"})

# add to database
@receipt_api.route('/api/postVendorUpdate', methods=["POST"])
def postVendorUpdate():
    if request.method == "POST":
        receipt_id = int(request.get_json()['receipt_id'])
        vendor_id = int(request.get_json()['vendor_id'])
        site_name = session['selected_site']
        receipts_database.updateReceiptsTuple(site_name, {'id': receipt_id, 'update': {'vendor_id': vendor_id}})
        return jsonify({'error': False, "message": "Line Saved Succesfully"})
    return jsonify({'error': True, "message": "Something went wrong while saving line!"})

# added to database
@receipt_api.route('/api/resolveReceipt', methods=["POST"])
def resolveReceipt():
    if request.method == "POST":
        receipt_id = int(request.get_json()['receipt_id'])
        site_name = session['selected_site']
        user= session['user']
        receipt = receipts_database.updateReceiptsTuple(site_name, {'id': receipt_id, 'update': {'receipt_status': 'Resolved'}})
        webpush.push_ntfy(title=f"Receipt '{receipt['receipt_id']}' Resolved", body=f"Receipt {receipt['receipt_id']} was completed by {user['username']}.")
        return jsonify({'error': False, "message": "Line Saved Succesfully"})
    return jsonify({'error': True, "message": "Something went wrong while saving line!"})

# added to database
@receipt_api.route('/api/uploadfile/<receipt_id>', methods=["POST"])
def uploadFile(receipt_id):
    file = request.files['file']
    file_path = current_app.config['FILES_FOLDER'] + f"/receipts/{file.filename.replace(" ", "_")}"
    file.save(file_path)
    file_type, _ = mimetypes.guess_type(file.filename)
    preview_image = ""
    if file_type == "application/pdf":
        output_path = "static/files/receipts/previews/"
        preview_image = receipts_processes.create_pdf_preview(file_path, output_path)

    file_size = os.path.getsize(file_path)
    site_name = session['selected_site']
    username = session['user']['username']
    receipt_files = receipts_database.selectReceiptsTuple(site_name, (receipt_id, ))['files']
    receipt_files[file.filename.replace(" ", "_")] = {'file_path': file.filename.replace(" ", "_"), 'file_type': file_type, 'file_size': file_size, 'uploaded_by': username, 'preview_image': preview_image}
    receipts_database.updateReceiptsTuple(site_name, {'id': receipt_id, 'update': {'files': receipt_files}})
    return jsonify({})

# Does not need to be added to Database
@receipt_api.route('/api/getFile/<file_name>')
def getFile(file_name):
    path_ = current_app.config['FILES_FOLDER'] + "/receipts"
    print(path_)
    return send_from_directory(path_, file_name)

# Added to database
@receipt_api.route('/api/checkAPI', methods=["POST"])
def checkAPI():
    if request.method == "POST":
        line_id = int(request.get_json()['line_id'])
        barcode = request.get_json()['barcode']
        site_name = session['selected_site']
        api_response, api_data = receipts_processes.get_open_facts(barcode)
        if api_response:
            receipt_item = receipts_database.selectReceiptItemsTuple(site_name, (line_id, ))
            item_data = receipt_item['data']
            item_data['api_data'] = api_data
            payload = {'id': line_id, 'update': {'type': 'api','data': item_data,'name': api_data['product_name']}}
            receipts_database.updateReceiptItemsTuple(site_name, payload)
            return jsonify({'error': False, "message": "Line updated for API, Succesfully"})
        else:
            return jsonify({'error': True, "message": "Item not in WorldFoodFacts!"})
        return jsonify({'error': False, "message": "Line Saved Succesfully"})
    return jsonify({'error': True, "message": "Something went wrong while saving line!"})