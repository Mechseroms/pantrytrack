from flask import Blueprint, request, render_template, redirect, session, url_for, send_file, jsonify, Response
import psycopg2, math, json, datetime, main, copy, requests, process, database, pprint, MyDataclasses
from config import config, sites_config
from main import unfoldCostLayers
from threading import Thread
from queue import Queue
import time, process
from user_api import login_required
import webpush
from application.poe import poe_processes
from application import postsqldb

point_of_ease = Blueprint('poe', __name__, template_folder="templates", static_folder="static")


@point_of_ease.route('/scanner', methods=["GET"])
def scannerEndpoint():
    sites = [site[1] for site in main.get_sites(session['user']['sites'])]
    return render_template('scanner.html', current_site=session['selected_site'], 
                           sites=sites)
    
@point_of_ease.route('/receipts', methods=["GET"])
def receiptsEndpoint():
    sites = [site[1] for site in main.get_sites(session['user']['sites'])]
    database_config = config()
    with psycopg2.connect(**database_config) as conn:
        units = postsqldb.UnitsTable.getAll(conn)
        #units = db.UnitsTable.getAll(conn)
    return render_template('receipts.html', current_site=session['selected_site'], 
                           sites=sites, units=units)

# DONT NEED
@point_of_ease.route('/getItemLocations', methods=["GET"])
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


# in item api, DONT NEED
@point_of_ease.route('/getItem', methods=["GET"])
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

@point_of_ease.route('/getItem/barcode', methods=["GET"])
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

# in items api DONT NEED
@point_of_ease.route('/getModalItems', methods=["GET"])
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

@point_of_ease.route('/postTransaction', methods=["POST"])
def post_transaction():
    if request.method == "POST":
        print('test two')
        result = poe_processes.postTransaction(
            site_name=session['selected_site'],
            user_id=session['user_id'],
            data=dict(request.json)
        )
        return jsonify(result)
    return jsonify({"error":True, "message":"There was an error with this POST statement"})


@point_of_ease.route('/postReceipt', methods=["POST"])
def post_receipt():
    if request.method == "POST":
        site_name = session['selected_site']
        user_id = session['user_id']
        data= {'items': request.json['items']}
        status = poe_processes.post_receipt(site_name, user_id, data)
        return jsonify(status)
    return jsonify({"error":True, "message":"There was an error with this POST statement"})