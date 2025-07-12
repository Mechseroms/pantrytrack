from flask import Blueprint, request, render_template, redirect, session, url_for, send_file, jsonify, Response
import psycopg2, math, json, datetime, main, copy, requests, process, database
from config import config, sites_config
from main import unfoldCostLayers

# this is a test!

database_api= Blueprint('database_api', __name__)

@database_api.route("/changeSite", methods=["POST"])
def changeSite():
    if request.method == "POST":
        site = request.json['site']
    session['selected_site'] = site
    return jsonify({'error': False, 'message': 'Site Changed!'})

@database_api.route("/getVendors")
def get_vendors():
    database_config = config()
    site_name = session['selected_site']
    vendors = []
    with psycopg2.connect(**database_config) as conn:
        try:
            with conn.cursor() as cur:
                sql = f"SELECT * FROM {site_name}_vendors;"
                cur.execute(sql)
                vendors = cur.fetchall()
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)
    
    return jsonify(vendors=vendors)