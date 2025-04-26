from flask import Blueprint, request, render_template, redirect, session, url_for, send_file, jsonify, Response
import psycopg2, math, json, datetime, main, copy, requests, process, database, pprint, MyDataclasses
from config import config, sites_config
from main import unfoldCostLayers
from user_api import login_required
import postsqldb

workshop_api = Blueprint('workshop_api', __name__)

@workshop_api.route("/workshop")
@login_required
def workshop():
    print(session['user'])
    sites = [site[1] for site in main.get_sites(session['user']['sites'])]
    print(session.get('user')['system_admin'])
    if not session.get('user')['system_admin']:
        return redirect('/logout')
    database_config = config()
    site_name = session['selected_site']
    with psycopg2.connect(**database_config) as conn:
        with conn.cursor() as cur:
            sql = f"SELECT id, name FROM {site_name}_zones;"
            cur.execute(sql)
            zones = cur.fetchall()
    return render_template("other/workshop.html", current_site=session['selected_site'], sites=sites, zones=zones)


@workshop_api.route('/workshop/getZones', methods=['GET'])
@login_required
def getZones():
    if request.method == "GET":
        records = []
        count = 0
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 10))
        offset = (page - 1) * limit
        database_config = config()
        site_name = session['selected_site']
        with psycopg2.connect(**database_config) as conn:
            records, count = postsqldb.ZonesTable.paginateZones(conn, site_name, (limit, offset))
            return jsonify({'zones': records, "end": math.ceil(count/limit), 'error':False, 'message': 'Zones Loaded Successfully!'})
    return jsonify({'zones': records, "end": math.ceil(count/limit), 'error':True, 'message': 'There was a problem loading Zones!'})

@workshop_api.route('/workshop/getLocations', methods=['GET'])
@login_required
def getLocations():
    if request.method == "GET":
        records = []
        count = 0
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 10))
        offset = (page - 1) * limit
        database_config = config()
        site_name = session['selected_site']
        with psycopg2.connect(**database_config) as conn:
            records, count = postsqldb.LocationsTable.paginateLocations(conn, site_name, (limit, offset))
            return jsonify({'locations': records, "end": math.ceil(count/limit), 'error':False, 'message': 'Zones Loaded Successfully!'})
    return jsonify({'locations': records, "end": math.ceil(count/limit), 'error':True, 'message': 'There was a problem loading Zones!'})

@workshop_api.route('/workshop/getVendors', methods=['GET'])
@login_required
def getVendors():
    if request.method == "GET":
        records = []
        count = 0
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 10))
        offset = (page - 1) * limit
        database_config = config()
        site_name = session['selected_site']
        with psycopg2.connect(**database_config) as conn:
            records, count = postsqldb.VendorsTable.paginateVendors(conn, site_name, (limit, offset))
            return jsonify({'vendors': records, "end": math.ceil(count/limit), 'error':False, 'message': 'Zones Loaded Successfully!'})
    return jsonify({'vendors': records, "end": math.ceil(count/limit), 'error':True, 'message': 'There was a problem loading Zones!'})

@workshop_api.route('/workshop/getBrands', methods=['GET'])
@login_required
def getBrands():
    if request.method == "GET":
        records = []
        count = 0
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 10))
        offset = (page - 1) * limit
        database_config = config()
        site_name = session['selected_site']
        with psycopg2.connect(**database_config) as conn:
            records, count = postsqldb.BrandsTable.paginateBrands(conn, site_name, (limit, offset))
            return jsonify({'brands': records, "end": math.ceil(count/limit), 'error':False, 'message': 'Zones Loaded Successfully!'})
    return jsonify({'brands': records, "end": math.ceil(count/limit), 'error':True, 'message': 'There was a problem loading Zones!'})

@workshop_api.route('/workshop/getPrefixes', methods=['GET'])
@login_required
def getPrefixes():
    if request.method == "GET":
        records = []
        count = 0
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 10))
        offset = (page - 1) * limit
        database_config = config()
        site_name = session['selected_site']
        with psycopg2.connect(**database_config) as conn:
            records, count = postsqldb.SKUPrefixTable.paginatePrefixes(conn, site_name, (limit, offset))
            return jsonify({'prefixes': records, "end": math.ceil(count/limit), 'error':False, 'message': 'Zones Loaded Successfully!'})
    return jsonify({'prefixes': records, "end": math.ceil(count/limit), 'error':True, 'message': 'There was a problem loading Zones!'})


@workshop_api.route('/workshop/postAddZone', methods=["POST"])
def postAddZone():
    if request.method == "POST":
        database_config = config()
        site_name = session['selected_site']
        try:
            with psycopg2.connect(**database_config) as conn:
                with conn.cursor() as cur:
                    cur.execute(f"SELECT id FROM sites WHERE site_name = %s;", (site_name,))
                    site_id = cur.fetchone()[0]
                zone = postsqldb.ZonesTable.Payload(
                    request.get_json()['name'],
                    request.get_json()['description']
                )
                postsqldb.ZonesTable.insert_tuple(conn, site_name, zone.payload())
        except Exception as error:
            conn.rollback()
            return jsonify({'error': True, 'message': error})
        return jsonify({'error': False, 'message': f"Zone added to {site_name}."})
    return jsonify({'error': True, 'message': f"These was an error with adding this Zone to {site_name}."})

@workshop_api.route('/workshop/postEditZone', methods=["POST"])
def postEditZone():
    if request.method == "POST":
        database_config = config()
        site_name = session['selected_site']
        try:
            with psycopg2.connect(**database_config) as conn:
                payload = {'id': request.get_json()['zone_id'], 
                           'update': request.get_json()['update']}
                zone = postsqldb.ZonesTable.update_tuple(conn, site_name, payload)
        except Exception as error:
            conn.rollback()
            return jsonify({'error': True, 'message': error})
        return jsonify({'error': False, 'message': f"{zone['name']} edited in site {site_name}."})
    return jsonify({'error': True, 'message': f"These was an error with editing Zone {zone['name']} in {site_name}."})

@workshop_api.route('/workshop/postAddLocation', methods=["POST"])
def postAddLocation():
    if request.method == "POST":
        database_config = config()
        site_name = session['selected_site']
        try:
            with psycopg2.connect(**database_config) as conn:
                   
                location = postsqldb.LocationsTable.Payload(
                    request.get_json()['uuid'],
                    request.get_json()['name'],
                    request.get_json()['zone_id']
                )
                print(request.get_json())
                postsqldb.LocationsTable.insert_tuple(conn, site_name, location.payload())
        except Exception as error:
            conn.rollback()
            return jsonify({'error': True, 'message': error})
        return jsonify({'error': False, 'message': f"Zone added to {site_name}."})
    return jsonify({'error': True, 'message': f"These was an error with adding this Zone to {site_name}."})

@workshop_api.route('/workshop/postAddVendor', methods=["POST"])
def postAddVendor():
    if request.method == "POST":
        database_config = config()
        site_name = session['selected_site']
        try:
            with psycopg2.connect(**database_config) as conn:
                vendor = postsqldb.VendorsTable.Payload(
                    request.get_json()['vendor_name'],
                    session['user_id'],
                    request.get_json()['vendor_address'],
                    request.get_json()['vendor_phone_number'],
                )
                postsqldb.VendorsTable.insert_tuple(conn, site_name, vendor.payload())
        except Exception as error:
            conn.rollback()
            return jsonify({'error': True, 'message': error})
        return jsonify({'error': False, 'message': f"Zone added to {site_name}."})
    return jsonify({'error': True, 'message': f"These was an error with adding this Zone to {site_name}."})

@workshop_api.route('/workshop/postEditVendor', methods=["POST"])
def postEditVendor():
    if request.method == "POST":
        database_config = config()
        site_name = session['selected_site']
        try:
            with psycopg2.connect(**database_config) as conn:
                payload = {'id': request.get_json()['vendor_id'], 
                           'update': request.get_json()['update']}
                vendor = postsqldb.VendorsTable.update_tuple(conn, site_name, payload)
        except Exception as error:
            conn.rollback()
            return jsonify({'error': True, 'message': error})
        return jsonify({'error': False, 'message': f"{vendor['vendor_name']} edited in site {site_name}."})
    return jsonify({'error': True, 'message': f"These was an error with editing Zone {vendor['vendor_name']} in {site_name}."})

@workshop_api.route('/workshop/postAddBrand', methods=["POST"])
def postAddBrand():
    if request.method == "POST":
        database_config = config()
        site_name = session['selected_site']
        try:
            with psycopg2.connect(**database_config) as conn:
                brand = postsqldb.BrandsTable.Payload(
                    request.get_json()['brand_name']
                )
                postsqldb.BrandsTable.insert_tuple(conn, site_name, brand.payload())
        except Exception as error:
            conn.rollback()
            return jsonify({'error': True, 'message': error})
        return jsonify({'error': False, 'message': f"Brand added to {site_name}."})
    return jsonify({'error': True, 'message': f"These was an error with adding this Zone to {site_name}."})

@workshop_api.route('/workshop/postEditBrand', methods=["POST"])
def postEditBrand():
    if request.method == "POST":
        database_config = config()
        site_name = session['selected_site']
        try:
            with psycopg2.connect(**database_config) as conn:
                payload = {'id': request.get_json()['brand_id'], 
                           'update': request.get_json()['update']}
                brand = postsqldb.BrandsTable.update_tuple(conn, site_name, payload)
        except Exception as error:
            conn.rollback()
            return jsonify({'error': True, 'message': error})
        return jsonify({'error': False, 'message': f"{brand['name']} edited in site {site_name}."})
    return jsonify({'error': True, 'message': f"These was an error with editing Zone {brand['name']} in {site_name}."})

@workshop_api.route('/workshop/postAddPrefix', methods=["POST"])
def postAddPrefix():
    if request.method == "POST":
        database_config = config()
        site_name = session['selected_site']
        try:
            with psycopg2.connect(**database_config) as conn:
                prefix = postsqldb.SKUPrefixTable.Payload(
                    request.get_json()['prefix_uuid'],
                    request.get_json()['prefix_name'],
                    request.get_json()['prefix_description']
                )
                postsqldb.SKUPrefixTable.insert_tuple(conn, site_name, prefix.payload())
        except Exception as error:
            conn.rollback()
            return jsonify({'error': True, 'message': error})
        return jsonify({'error': False, 'message': f"Prefix added to {site_name}."})
    return jsonify({'error': True, 'message': f"These was an error with adding this Prefix to {site_name}."})

@workshop_api.route('/workshop/postEditPrefix', methods=["POST"])
def postEditPrefix():
    if request.method == "POST":
        database_config = config()
        site_name = session['selected_site']
        try:
            with psycopg2.connect(**database_config) as conn:
                payload = {'id': request.get_json()['prefix_id'], 
                           'update': request.get_json()['update']}
                prefix = postsqldb.SKUPrefixTable.update_tuple(conn, site_name, payload)
        except Exception as error:
            conn.rollback()
            return jsonify({'error': True, 'message': error})
        return jsonify({'error': False, 'message': f"{prefix['name']} edited in site {site_name}."})
    return jsonify({'error': True, 'message': f"These was an error with editing Zone {prefix['name']} in {site_name}."})
