from flask import Blueprint, request, render_template, redirect, session, url_for, send_file, jsonify, Response
import psycopg2, math, json, datetime, main, copy, requests, process, database, pprint, MyDataclasses
from config import config, sites_config
from main import unfoldCostLayers
from threading import Thread
from queue import Queue
import time, process
from user_api import login_required
import webpush

external_api = Blueprint('external', __name__)

@external_api.route('/external/getItemLocations', methods=["GET"])
def getItemLocations():
    recordset = []
    count = 0
    if request.method == "GET":
        item_id = int(request.args.get('id', 1))
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 10))
        site_name = session['selected_site']
        offset = (page - 1) * limit
        database_config = config()
        with psycopg2.connect(**database_config) as conn:
            recordset, count = database.getItemLocations(conn, site_name, (item_id, limit, offset), convert=True)
        return jsonify({"locations":recordset, "end":math.ceil(count/limit), "error":False, "message":"item fetched succesfully!"})
    return jsonify({"locations":recordset, "end": math.ceil(count/limit), "error":True, "message":"There was an error with this GET statement"})

@external_api.route('/external/getItem', methods=["GET"])
def getItem():
    record = {}
    if request.method == "GET":
        item_id = int(request.args.get('id', 1))
        site_name = session['selected_site']
        database_config = config()
        with psycopg2.connect(**database_config) as conn:
            record = database.getItemAllByID(conn, site_name, (item_id, ), convert=True)
        return jsonify({"item":record,  "error":False, "message":"item fetched succesfully!"})
    return jsonify({"item":record, "error":True, "message":"There was an error with this GET statement"})

@external_api.route('/external/getItem/barcode', methods=["GET"])
def getItemBarcode():
    record = {}
    if request.method == "GET":
        item_barcode = f"%{str(request.args.get('barcode', 1))}%"
        site_name = session['selected_site']
        database_config = config()
        with psycopg2.connect(**database_config) as conn:
            record = database.getItemAllByBarcode(conn, site_name, (item_barcode, ), convert=True)
        if record == {}:
            return jsonify({"item":None,  "error":True, "message":"Item either does not exist or there was a larger problem!"}) 
        else:
            return jsonify({"item":record,  "error":False, "message":"item fetched succesfully!"})
    return jsonify({"item":record, "error":True, "message":"There was an error with this GET statement"})

@external_api.route('/external/getModalItems', methods=["GET"])
@login_required
def getModalItems():
    recordset = []
    count = {'count': 0}
    if request.method == "GET":
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 10))
        search_string = request.args.get('search_string', '')
        site_name = session['selected_site']
        offset = (page - 1) * limit
        database_config = config()
        with psycopg2.connect(**database_config) as conn:
            payload = (search_string, limit, offset)
            recordset, count = database.getItemsForModal(conn, site_name, payload, convert=True)
        return jsonify({"items":recordset, "end":math.ceil(count['count']/limit), "error":False, "message":"items fetched succesfully!"})
    return jsonify({"items":recordset, "end":math.ceil(count['count']/limit), "error":True, "message":"There was an error with this GET statement"})

@external_api.route('/external/postTransaction', methods=["POST"])
def post_transaction():
    if request.method == "POST":
        database_config = config()
        with psycopg2.connect(**database_config) as conn:
            result = process.postTransaction(
                conn=conn,
                site_name=session['selected_site'],
                user_id=session['user_id'],
                data=dict(request.json)
            )  
        return jsonify(result)
    return jsonify({"error":True, "message":"There was an error with this POST statement"})


@external_api.route('/external/postReceipt', methods=["POST"])
def post_receipt():
    if request.method == "POST":
        site_name = session['selected_site']
        user_id = session['user_id']
        database_config = config()
        with psycopg2.connect(**database_config) as conn:
            items = request.json['items']
            receipt_id = database.request_receipt_id(conn, site_name)
            receipt_id = f"SIR-{receipt_id}"
            receipt = MyDataclasses.ReceiptPayload(
               receipt_id=receipt_id,
               submitted_by=user_id
            )
            receipt = database.insertReceiptsTuple(conn, site_name, receipt.payload(), convert=True)
            
            for item in items:
                
                receipt_item = MyDataclasses.ReceiptItemPayload(
                    type=item['type'],
                    receipt_id=receipt['id'],
                    barcode=item['item']['barcode'],
                    name=item['item']['item_name'],
                    qty=item['item']['qty'],
                    uom=item['item']['uom'],
                    data=item['item']['data']
                )
                database.insertReceiptItemsTuple(conn, site_name, receipt_item.payload())
            #webpush.push_notifications('New Receipt', f"Receipt {receipt['receipt_id']} was added to Site -> {site_name}!")
            webpush.push_ntfy('New Receipt', f"Receipt {receipt['receipt_id']} was added to Site -> {site_name}!")
            return jsonify({"error":False, "message":"Transaction Complete!"})
    return jsonify({"error":True, "message":"There was an error with this POST statement"})