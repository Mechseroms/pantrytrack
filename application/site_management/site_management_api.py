# 3RD PARTY IMPORTS
from flask import (
    Blueprint, request, render_template, redirect, session, jsonify
    )
import math

# APPLICATION IMPORTS
from user_api import login_required
from application import postsqldb, database_payloads
from application.site_management import site_management_database

site_management_api = Blueprint('site_management_api', __name__, template_folder="templates", static_folder="static")

# ROOT TEMPLATE ROUTES
@site_management_api.route("/")
@login_required
def site_management_index():
    sites = [site[1] for site in postsqldb.get_sites(session['user']['sites'])]
    if not session.get('user')['system_admin']:
        return redirect('/logout')
    site_name = session['selected_site']
    zones = site_management_database.selectZonesTuples(site_name, convert=False)
    return render_template("site_management.html", current_site=site_name, sites=sites, zones=zones)

# API CALLS
# added to database
@site_management_api.route('/api/getZones', methods=['GET'])
@login_required
def getZones():
    if request.method == "GET":
        records = []
        count = 0
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 10))
        offset = (page - 1) * limit
        site_name = session['selected_site']
        records, count = site_management_database.paginateZonesTuples(site_name, (limit, offset))
        return jsonify({'zones': records, "end": math.ceil(count/limit), 'error':False, 'message': 'Zones Loaded Successfully!'})
    return jsonify({'zones': records, "end": math.ceil(count/limit), 'error':True, 'message': 'There was a problem loading Zones!'})

# added to database
@site_management_api.route('/api/getLocations', methods=['GET'])
@login_required
def getLocations():
    if request.method == "GET":
        records = []
        count = 0
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 10))
        offset = (page - 1) * limit
        site_name = session['selected_site']
        records, count = site_management_database.paginateLocationsTuples(site_name, (limit, offset))
        return jsonify({'locations': records, "end": math.ceil(count/limit), 'error':False, 'message': 'Zones Loaded Successfully!'})
    return jsonify({'locations': records, "end": math.ceil(count/limit), 'error':True, 'message': 'There was a problem loading Zones!'})

# added to database
@site_management_api.route('/api/getVendors', methods=['GET'])
@login_required
def getVendors():
    if request.method == "GET":
        records = []
        count = 0
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 10))
        offset = (page - 1) * limit
        site_name = session['selected_site']
        records, count = site_management_database.paginateVendorsTuples(site_name, (limit, offset))
        return jsonify({'vendors': records, "end": math.ceil(count/limit), 'error':False, 'message': 'Zones Loaded Successfully!'})
    return jsonify({'vendors': records, "end": math.ceil(count/limit), 'error':True, 'message': 'There was a problem loading Zones!'})

# added to database
@site_management_api.route('/api/getBrands', methods=['GET'])
@login_required
def getBrands():
    if request.method == "GET":
        records = []
        count = 0
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 10))
        offset = (page - 1) * limit
        site_name = session['selected_site']
        records, count = site_management_database.paginateBrandsTuples(site_name, (limit, offset))
        return jsonify({'brands': records, "end": math.ceil(count/limit), 'error':False, 'message': 'Zones Loaded Successfully!'})
    return jsonify({'brands': records, "end": math.ceil(count/limit), 'error':True, 'message': 'There was a problem loading Zones!'})

# added to database
@site_management_api.route('/api/getPrefixes', methods=['GET'])
@login_required
def getPrefixes():
    if request.method == "GET":
        records = []
        count = 0
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 10))
        offset = (page - 1) * limit
        site_name = session['selected_site']
        records, count = site_management_database.paginatePrefixesTuples(site_name, (limit, offset))
        return jsonify({'prefixes': records, "end": math.ceil(count/limit), 'error':False, 'message': 'Zones Loaded Successfully!'})
    return jsonify({'prefixes': records, "end": math.ceil(count/limit), 'error':True, 'message': 'There was a problem loading Zones!'})

# added to database
@site_management_api.route('/api/postAddZone', methods=["POST"])
def postAddZone():
    if request.method == "POST":
        site_name = session['selected_site']
        zone = database_payloads.ZonesPayload(request.get_json()['name'], request.get_json()['description'])
        site_management_database.insertZonesTuple(site_name, zone.payload())
        return jsonify({'error': False, 'message': f"Zone added to {site_name}."})
    return jsonify({'error': True, 'message': f"These was an error with adding this Zone to {site_name}."})

# added to database
@site_management_api.route('/api/postEditZone', methods=["POST"])
def postEditZone():
    if request.method == "POST":
        site_name = session['selected_site']
        payload = {'id': request.get_json()['zone_id'], 'update': request.get_json()['update']}
        zone = site_management_database.updateZonesTuple(site_name, payload)  
        return jsonify({'error': False, 'message': f"{zone['name']} edited in site {site_name}."})
    return jsonify({'error': True, 'message': f"These was an error with editing Zone {zone['name']} in {site_name}."})

# added to database
@site_management_api.route('/api/postAddLocation', methods=["POST"])
def postAddLocation():
    if request.method == "POST":
        site_name = session['selected_site']
        location = database_payloads.LocationsPayload(request.get_json()['uuid'], request.get_json()['name'], request.get_json()['zone_id'])
        site_management_database.insertLocationsTuple(site_name, location.payload())
        return jsonify({'error': False, 'message': f"Zone added to {site_name}."})
    return jsonify({'error': True, 'message': f"These was an error with adding this Zone to {site_name}."})

# added to database
@site_management_api.route('/api/postAddVendor', methods=["POST"])
def postAddVendor():
    if request.method == "POST":
        site_name = session['selected_site']
        
        vendor = database_payloads.VendorsPayload(
            request.get_json()['vendor_name'],
            session['user_id'],
            request.get_json()['vendor_address'],
            request.get_json()['vendor_phone_number'],
        )
        site_management_database.insertVendorsTuple(site_name, vendor.payload())
        return jsonify({'error': False, 'message': f"Zone added to {site_name}."})
    return jsonify({'error': True, 'message': f"These was an error with adding this Zone to {site_name}."})

# added to database
@site_management_api.route('/api/postEditVendor', methods=["POST"])
def postEditVendor():
    if request.method == "POST":
        site_name = session['selected_site']
        payload = {'id': request.get_json()['vendor_id'], 'update': request.get_json()['update']}
        vendor = site_management_database.updateVendorsTuple(site_name, payload)            
        return jsonify({'error': False, 'message': f"{vendor['vendor_name']} edited in site {site_name}."})
    return jsonify({'error': True, 'message': f"These was an error with editing Zone {vendor['vendor_name']} in {site_name}."})

# added to database
@site_management_api.route('/api/postAddBrand', methods=["POST"])
def postAddBrand():
    if request.method == "POST":
        site_name = session['selected_site']
        brand = database_payloads.BrandsPayload(request.get_json()['brand_name'])
        site_management_database.insertBrandsTuple(site_name, brand.payload())
        return jsonify({'error': False, 'message': f"Brand added to {site_name}."})
    return jsonify({'error': True, 'message': f"These was an error with adding this Zone to {site_name}."})

# added to database
@site_management_api.route('/api/postEditBrand', methods=["POST"])
def postEditBrand():
    if request.method == "POST":
        site_name = session['selected_site']
        payload = {'id': request.get_json()['brand_id'], 'update': request.get_json()['update']}
        brand = site_management_database.updateBrandsTuple(site_name, payload)
        return jsonify({'error': False, 'message': f"{brand['name']} edited in site {site_name}."})
    return jsonify({'error': True, 'message': f"These was an error with editing Zone {brand['name']} in {site_name}."})

# added to database
@site_management_api.route('/api/postAddPrefix', methods=["POST"])
def postAddPrefix():
    if request.method == "POST":
        site_name = session['selected_site']
        prefix = database_payloads.SKUPrefixPayload(request.get_json()['prefix_uuid'], request.get_json()['prefix_name'], request.get_json()['prefix_description'])
        site_management_database.insertSKUPrefixesTuple(site_name, prefix.payload())
        return jsonify({'error': False, 'message': f"Prefix added to {site_name}."})
    return jsonify({'error': True, 'message': f"These was an error with adding this Prefix to {site_name}."})

# added to database
@site_management_api.route('/api/postEditPrefix', methods=["POST"])
def postEditPrefix():
    if request.method == "POST":
        site_name = session['selected_site']
        payload = {'id': request.get_json()['prefix_id'], 'update': request.get_json()['update']}
        prefix = site_management_database.updateSKUPrefixesTuple(site_name, payload)        
        return jsonify({'error': False, 'message': f"{prefix['name']} edited in site {site_name}."})
    return jsonify({'error': True, 'message': f"These was an error with editing Zone {prefix['name']} in {site_name}."})
