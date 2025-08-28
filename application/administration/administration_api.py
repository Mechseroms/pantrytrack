# 3RD PARTY IMPORTS
from flask import (
    Blueprint, request, render_template, session, jsonify, redirect
    )
import math
import hashlib

# APPLICATION IMPORTS
from application.access_module import access_api
from application.administration import administration_database, administration_services
from application import database_payloads, postsqldb


admin_api = Blueprint('admin_api', __name__, template_folder="templates", static_folder="static")


# ROOT TEMPLATE ROUTES
@admin_api.route('/')
@access_api.login_required
def admin_index():
    sites = [site[1] for site in postsqldb.get_sites(session['user']['sites'])]
    return render_template("admin_index.html", current_site=session['selected_site'], sites=sites)

@admin_api.route('/site/<id>')
@access_api.login_required
def adminSites(id):
    if id == "new":
        new_site_payload = database_payloads.SitePayload("", "", session['user_id'])
        return render_template("site.html", site=new_site_payload.get_dictionary())
    else:
        site = administration_database.selectSitesTuple((id,))
        return render_template('site.html', site=site)

@admin_api.route('/role/<id>')
@access_api.login_required
def adminRoles(id):
    sites = administration_database.selectSitesTuples()
    if id == "new":
        new_role_payload = database_payloads.RolePayload("", "", 0)
        return render_template("role.html", role=new_role_payload.get_dictionary(), sites=sites)
    else:
        role = administration_database.selectRolesTuple((id,))
        return render_template('role.html', role=role, sites=sites)

@admin_api.route('/user/<id>')
@access_api.login_required
def adminUser(id):
    if id == "new":
        new_user_payload = database_payloads.LoginsPayload("", "", "", "")
        return render_template("user.html", user=new_user_payload.get_dictionary())
    else:
        user = administration_database.selectLoginsTuple((int(id),))
        return render_template('user.html', user=user)

@admin_api.route('/setup', methods=['GET', 'POST'])
def first_time_setup():
    if request.method == "POST":
        database_address = request.form['database_address']
        database_port = request.form['database_port']
        database_name = request.form['database_name']
        database_user = request.form['database_user']
        database_password = request.form['database_address']

        payload = {
            "site_name" : request.form['site_name'],
            "admin_user": (request.form['username'], hashlib.sha256(request.form['password'].encode()).hexdigest(), request.form['email']),
            "default_zone": request.form['site_default_zone'],
            "default_primary_location": request.form['site_default_location'],
            "site_description": request.form['site_description'] 
        }

        administration_services.addSite(payload)

        return redirect("/login")
    
    return render_template("setup.html")

# API ROUTES
@admin_api.route('/api/getSites', methods=['GET'])
@access_api.login_required
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

@admin_api.route('/api/getRoles', methods=['GET'])
@access_api.login_required
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

@admin_api.route('/api/getLogins', methods=['GET'])
@access_api.login_required
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

@admin_api.route('/api/site/postDeleteSite', methods=["POST"])
@access_api.login_required
def postDeleteSite():
    if request.method == "POST":
        site_id = request.get_json()['site_id']
        user_id = session['user_id']
        site = administration_database.selectSitesTuple((site_id,))
        user = administration_database.selectLoginsTuple((user_id,))
        if user['id'] != site['site_owner_id']:
            return jsonify({'error': True, 'message': f"You must be the owner of this site to delete."})
        
        try:
            administration_services.deleteSite(site, user)
        except Exception as err:
            print(err)

        return jsonify({'error': False, 'message': f""})
    return jsonify({'error': True, 'message': f""})

@admin_api.route('/api/site/postAddSite', methods=["POST"])
@access_api.login_required
def postAddSite():
    if request.method == "POST":
        payload = request.get_json()['payload']
        site_name = session['selected_site']
        user_id = session['user_id']
        user = administration_database.selectLoginsTuple((user_id,))
        payload['admin_user'] = (user['username'], user['password'], user['email'], user['row_type'])
        
        administration_services.addSite(payload)
        

        return jsonify({'error': False, 'message': f"Zone added to {site_name}."})
    return jsonify({'error': True, 'message': f"These was an error with adding this Zone to {site_name}."})

@admin_api.route('/api/site/postEditSite', methods=["POST"])
@access_api.login_required
def postEditSite():
    if request.method == "POST":
        payload = request.get_json()['payload']
        administration_database.updateSitesTuple(payload)
        return jsonify({'error': False, 'message': f"Site updated."})
    return jsonify({'error': True, 'message': f"These was an error with updating Site."})

@admin_api.route('/api/role/postAddRole', methods=["POST"])
@access_api.login_required
def postAddRole():
    if request.method == "POST":
        payload = request.get_json()['payload']
        print(payload)
        role = database_payloads.RolePayload(
            payload['role_name'],
            payload['role_description'],
            payload['site_id']
        )
        administration_database.insertRolesTuple(role.payload())                
        return jsonify({'error': False, 'message': f"Role added."})
    return jsonify({'error': True, 'message': f"These was an error with adding this Role."})

@admin_api.route('/api/role/postEditRole', methods=["POST"])
@access_api.login_required
def postEditRole():
    if request.method == "POST":
        payload = request.get_json()['payload']
        administration_database.updateRolesTuple(payload)     
        return jsonify({'error': False, 'message': f"Role updated."})
    return jsonify({'error': True, 'message': f"These was an error with updating this Role."})

@admin_api.route('/api/user/postAddLogin', methods=["POST"])
@access_api.login_required
def postAddLogin():
    if request.method == "POST":
        payload = request.get_json()['payload']
        user = database_payloads.LoginsPayload(
            payload['username'],
            hashlib.sha256(payload['password'].encode()).hexdigest(),
            payload['email'],
            payload['row_type']
        )
        user = administration_database.insertLoginsTuple(user.payload())
            
        return jsonify({'user': user, 'error': False, 'message': f"User added."})
    return jsonify({'user': user, 'error': True, 'message': f"These was an error with adding this User."})

@admin_api.route('/api/user/postEditLogin', methods=["POST"])
@access_api.login_required
def postEditLogin():
    if request.method == "POST":
        payload = request.get_json()['payload']
        administration_database.updateLoginsTuple(payload)
        return jsonify({'error': False, 'message': f"User was Added Successfully."})
    return jsonify({'error': True, 'message': f"These was an error with adding this user."})

@admin_api.route('/api/user/postEditLoginPassword', methods=["POST"])
@access_api.login_required
def postEditLoginPassword():
    if request.method == "POST":
        payload = request.get_json()['payload']
        user = administration_database.selectLoginsTuple((payload['id'],))
        if hashlib.sha256(payload['current_password'].encode()).hexdigest() != user['password']:
            return jsonify({'error': True, 'message': "The provided current password is incorrect"})  
        payload['update']['password'] = hashlib.sha256(payload['update']['password'].encode()).hexdigest()
        administration_database.updateLoginsTuple(payload)
        return jsonify({'error': False, 'message': f"Password was changed successfully."})
    return jsonify({'error': True, 'message': f"These was an error with updating this Users password."})
