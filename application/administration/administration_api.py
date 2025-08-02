from flask import Blueprint, request, render_template, redirect, session, url_for, send_file, jsonify, Response
import psycopg2, math, json, datetime, main, copy, requests
from config import config, sites_config
from main import unfoldCostLayers, get_sites, get_roles, create_site_secondary, getUser
from manage import create
from user_api import login_required
import postsqldb, process, hashlib


# APPLICATION IMPORTS
from application.administration import administration_database, administration_processes
from application import database_payloads


admin_api = Blueprint('admin_api', __name__, template_folder="templates", static_folder="static")


# ROOT TEMPLATE ROUTES
@admin_api.route('/')
def admin_index():
    sites = [site[1] for site in main.get_sites(session['user']['sites'])]
    return render_template("admin_index.html", current_site=session['selected_site'], sites=sites)

# Added to Database
@admin_api.route('/site/<id>')
@login_required
def adminSites(id):
    if id == "new":
        new_site_payload = database_payloads.SitePayload("", "", session['user_id'])
        return render_template("site.html", site=new_site_payload.get_dictionary())
    else:
        site = administration_database.selectSitesTuple((id,))
        return render_template('site.html', site=site)

# Added to database
@admin_api.route('/role/<id>')
@login_required
def adminRoles(id):
    sites = administration_database.selectSitesTuples()
    if id == "new":
        new_role_payload = database_payloads.RolePayload("", "", 0)
        return render_template("role.html", role=new_role_payload.get_dictionary(), sites=sites)
    else:
        role = administration_database.selectRolesTuple((id,))
        return render_template('role.html', role=role, sites=sites)

# Added to database
@admin_api.route('/user/<id>')
@login_required
def adminUser(id):
    if id == "new":
        new_user_payload = database_payloads.LoginsPayload("", "", "", "")
        return render_template("user.html", user=new_user_payload.get_dictionary())
    else:
        user = administration_database.selectLoginsTuple(int(id))
        return render_template('user.html', user=user)

# API ROUTES
# add to database
@admin_api.route('/api/getSites', methods=['GET'])
@login_required
def getSites():
    if request.method == "GET":
        records = []
        count = 0
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 10))
        offset = (page - 1) * limit
        records, count = administration_database.paginateSitesTuples((limit, offset))
        return jsonify({'sites': records, "end": math.ceil(count/limit), 'error':False, 'message': 'Sites Loaded Successfully!'})
    return jsonify({'sites': records, "end": math.ceil(count/limit), 'error':True, 'message': 'There was a problem loading Sites!'})

# Added to database
@admin_api.route('/api/getRoles', methods=['GET'])
@login_required
def getRoles():
    if request.method == "GET":
        records = []
        count = 0
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 10))
        offset = (page - 1) * limit
        records, count = administration_database.paginateRolesTuples((limit, offset))
        return jsonify({'roles': records, "end": math.ceil(count/limit), 'error':False, 'message': 'Roles Loaded Successfully!'})
    return jsonify({'roles': records, "end": math.ceil(count/limit), 'error':True, 'message': 'There was a problem loading Roles!'})

# Added to Database
@admin_api.route('/api/getLogins', methods=['GET'])
@login_required
def getLogins():
    if request.method == "GET":
        records = []
        count = 0
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 10))
        offset = (page - 1) * limit
        records, count = administration_database.paginateLoginsTuples((limit, offset))
        return jsonify({'logins': records, "end": math.ceil(count/limit), 'error':False, 'message': 'logins Loaded Successfully!'})
    return jsonify({'logins': records, "end": math.ceil(count/limit), 'error':True, 'message': 'There was a problem loading logins!'})

# Added to database and Processses.
@admin_api.route('/api/site/postDeleteSite', methods=["POST"])
def postDeleteSite():
    if request.method == "POST":
        site_id = request.get_json()['site_id']
        user_id = session['user_id']
        site = administration_database.selectSitesTuple((site_id,))
        user = administration_database.selectLoginsTuple((user_id,))
        if user['id'] != site['site_owner_id']:
            return jsonify({'error': True, 'message': f"You must be the owner of this site to delete."})
        
        try:
            administration_processes.deleteSite(site, user)
        except Exception as err:
            print(err)

        return jsonify({'error': False, 'message': f""})
    return jsonify({'error': True, 'message': f""})

# Added to Database and Processes
@admin_api.route('/api/site/postAddSite', methods=["POST"])
def postAddSite():
    if request.method == "POST":
        payload = request.get_json()['payload']
        site_name = session['selected_site']
        user_id = session['user_id']
        user = administration_database.selectLoginsTuple((user_id,))
        payload['admin_user'] = (user['username'], user['password'], user['email'], user['row_type'])
        
        administration_processes.addSite(payload)
        

        return jsonify({'error': False, 'message': f"Zone added to {site_name}."})
    return jsonify({'error': True, 'message': f"These was an error with adding this Zone to {site_name}."})

@admin_api.route('/api/site/postEditSite', methods=["POST"])
def postEditSite():
    if request.method == "POST":
        payload = request.get_json()['payload']
        database_config = config()
        try:
            with psycopg2.connect(**database_config) as conn:
                postsqldb.SitesTable.update_tuple(conn, payload)
        except Exception as error:
            conn.rollback()
            return jsonify({'error': True, 'message': error})
        return jsonify({'error': False, 'message': f"Site updated."})
    return jsonify({'error': True, 'message': f"These was an error with updating Site."})

@admin_api.route('/api/role/postAddRole', methods=["POST"])
def postAddRole():
    if request.method == "POST":
        payload = request.get_json()['payload']
        database_config = config()
        print(payload)
        try:
            with psycopg2.connect(**database_config) as conn:
                role = postsqldb.RolesTable.Payload(
                    payload['role_name'],
                    payload['role_description'],
                    payload['site_id']
                )
                postsqldb.RolesTable.insert_tuple(conn, role.payload())
                
        except Exception as error:
            conn.rollback()
            return jsonify({'error': True, 'message': error})
        return jsonify({'error': False, 'message': f"Role added."})
    return jsonify({'error': True, 'message': f"These was an error with adding this Role."})

@admin_api.route('/api/role/postEditRole', methods=["POST"])
def postEditRole():
    if request.method == "POST":
        payload = request.get_json()['payload']
        database_config = config()
        print(payload)
        try:
            with psycopg2.connect(**database_config) as conn:
                postsqldb.RolesTable.update_tuple(conn, payload)
                
        except Exception as error:
            conn.rollback()
            return jsonify({'error': True, 'message': error})
        return jsonify({'error': False, 'message': f"Role updated."})
    return jsonify({'error': True, 'message': f"These was an error with updating this Role."})

@admin_api.route('/api/user/postAddLogin', methods=["POST"])
def postAddLogin():
    if request.method == "POST":
        payload = request.get_json()['payload']
        database_config = config()
        user = []
        try:
            with psycopg2.connect(**database_config) as conn:
                user = postsqldb.LoginsTable.Payload(
                    payload['username'],
                    hashlib.sha256(payload['password'].encode()).hexdigest(),
                    payload['email'],
                    payload['row_type']
                )
                user = postsqldb.LoginsTable.insert_tuple(conn, user.payload())
        except postsqldb.DatabaseError as error:
            conn.rollback()
            return jsonify({'user': user, 'error': True, 'message': error})
        return jsonify({'user': user, 'error': False, 'message': f"User added."})
    return jsonify({'user': user, 'error': True, 'message': f"These was an error with adding this User."})

@admin_api.route('/api/user/postEditLogin', methods=["POST"])
def postEditLogin():
    if request.method == "POST":
        payload = request.get_json()['payload']
        database_config = config()
        try:
            with psycopg2.connect(**database_config) as conn:
                postsqldb.LoginsTable.update_tuple(conn, payload)
        except Exception as error:
            conn.rollback()
            return jsonify({'error': True, 'message': error})
        return jsonify({'error': False, 'message': f"User was Added Successfully."})
    return jsonify({'error': True, 'message': f"These was an error with adding this user."})

@admin_api.route('/api/user/postEditLoginPassword', methods=["POST"])
def postEditLoginPassword():
    if request.method == "POST":
        payload = request.get_json()['payload']
        database_config = config()
        try:
            with psycopg2.connect(**database_config) as conn:
                user = postsqldb.LoginsTable.select_tuple(conn, (payload['id'],))
                if hashlib.sha256(payload['current_password'].encode()).hexdigest() != user['password']:
                    return jsonify({'error': True, 'message': "The provided current password is incorrect"})
                payload['update']['password'] = hashlib.sha256(payload['update']['password'].encode()).hexdigest()
                postsqldb.LoginsTable.update_tuple(conn, payload)
        except Exception as error:
            conn.rollback()
            return jsonify({'error': True, 'message': error})
        return jsonify({'error': False, 'message': f"Password was changed successfully."})
    return jsonify({'error': True, 'message': f"These was an error with updating this Users password."})
