# 3rd Party imports
from flask import (
    Blueprint, request, render_template, redirect, session, url_for, send_file, jsonify, Response
    )
import psycopg2

# applications imports
from config import config
from user_api import login_required
from application.poe import poe_processes, poe_database
from application import postsqldb


point_of_ease = Blueprint('poe', __name__, template_folder="templates", static_folder="static")


@point_of_ease.route('/scanner', methods=["GET"])
@login_required
def scannerEndpoint():
    sites = [site[1] for site in postsqldb.get_sites(session['user']['sites'])]
    return render_template('scanner.html', current_site=session['selected_site'], 
                           sites=sites)
    
@point_of_ease.route('/receipts', methods=["GET"])
@login_required
def receiptsEndpoint():
    sites = [site[1] for site in postsqldb.get_sites(session['user']['sites'])]
    database_config = config()
    with psycopg2.connect(**database_config) as conn:
        units = postsqldb.UnitsTable.getAll(conn)
    return render_template('receipts.html', current_site=session['selected_site'], 
                           sites=sites, units=units)

@point_of_ease.route('/getItem/barcode', methods=["GET"])
@login_required
def getItemBarcode():
    record = {}
    if request.method == "GET":
        item_barcode = f"%{str(request.args.get('barcode', 1))}%"
        site_name = session['selected_site']
        record = poe_database.selectItemAllByBarcode(site_name, (item_barcode,))
        if record == {}:
            return jsonify({"item":None,  "error":True, "message":"Item either does not exist or there was a larger problem!"}) 
        else:
            return jsonify({"item":record,  "error":False, "message":"item fetched succesfully!"})
    return jsonify({"item":record, "error":True, "message":"There was an error with this GET statement"})


@point_of_ease.route('/postTransaction', methods=["POST"])
@login_required
def post_transaction():
    if request.method == "POST":
        result = poe_processes.postTransaction(
            site_name=session['selected_site'],
            user_id=session['user_id'],
            data=dict(request.json)
        )
        return jsonify(result)
    return jsonify({"error":True, "message":"There was an error with this POST statement"})


@point_of_ease.route('/postReceipt', methods=["POST"])
@login_required
def post_receipt():
    if request.method == "POST":
        site_name = session['selected_site']
        user_id = session['user_id']
        data= {'items': request.json['items']}
        status = poe_processes.post_receipt(site_name, user_id, data)
        return jsonify(status)
    return jsonify({"error":True, "message":"There was an error with this POST statement"})