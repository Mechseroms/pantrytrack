from flask import Blueprint, request, render_template, redirect, session, url_for, send_file, jsonify, Response
import psycopg2, math, json, datetime, main, copy, requests
from config import config, sites_config
from main import unfoldCostLayers, get_sites, get_roles, create_site_secondary, getUser
from manage import create
from user_api import login_required
import postsqldb, process, hashlib, database_admin


admin_api = Blueprint('admin_api', __name__)

@admin_api.route('/admin')
def admin_index():
    sites = [site[1] for site in main.get_sites(session['user']['sites'])]
    return render_template("admin/index.html", 
                           current_site=session['selected_site'], 
                           sites=sites)

@admin_api.route('/admin/site/<id>')
@login_required
def adminSites(id):
    if id == "new":
        new_site = postsqldb.SitesTable.Payload(
            "",
            "",
            session['user_id']
        )
        return render_template("admin/site.html", site=new_site.get_dictionary())
    else:
        database_config = config()
        with psycopg2.connect(**database_config) as conn:
            site = postsqldb.SitesTable.select_tuple(conn, (id,))
            return render_template('admin/site.html', site=site)

@admin_api.route('/admin/role/<id>')
@login_required
def adminRoles(id):
    database_config = config()
    with psycopg2.connect(**database_config) as conn:
        sites = postsqldb.SitesTable.selectTuples(conn)
        if id == "new":
            new_role = postsqldb.RolesTable.Payload(
                "",
                "",
                0
            )
            return render_template("admin/role.html", role=new_role.get_dictionary(), sites=sites)
        else:
            role = postsqldb.RolesTable.select_tuple(conn, (id,))
            return render_template('admin/role.html', role=role, sites=sites)

@admin_api.route('/admin/user/<id>')
@login_required
def adminUser(id):
    database_config = config()
    with psycopg2.connect(**database_config) as conn:
        if id == "new":
            new_user = postsqldb.LoginsTable.Payload("", "", "", "")
            return render_template("admin/user.html", user=new_user.get_dictionary())
        else:
            user = database_admin.selectLoginsUser(int(id))
            return render_template('admin/user.html', user=user)

@admin_api.route('/admin/getSites', methods=['GET'])
@login_required
def getSites():
    if request.method == "GET":
        records = []
        count = 0
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 10))
        offset = (page - 1) * limit
        database_config = config()
        with psycopg2.connect(**database_config) as conn:
            records, count = postsqldb.SitesTable.paginateTuples(conn, (limit, offset))
            return jsonify({'sites': records, "end": math.ceil(count/limit), 'error':False, 'message': 'Sites Loaded Successfully!'})
    return jsonify({'sites': records, "end": math.ceil(count/limit), 'error':True, 'message': 'There was a problem loading Sites!'})

@admin_api.route('/admin/getRoles', methods=['GET'])
@login_required
def getRoles():
    if request.method == "GET":
        records = []
        count = 0
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 10))
        offset = (page - 1) * limit
        database_config = config()
        with psycopg2.connect(**database_config) as conn:
            records, count = postsqldb.RolesTable.paginate_tuples(conn, (limit, offset))
            return jsonify({'roles': records, "end": math.ceil(count/limit), 'error':False, 'message': 'Roles Loaded Successfully!'})
    return jsonify({'roles': records, "end": math.ceil(count/limit), 'error':True, 'message': 'There was a problem loading Roles!'})

@admin_api.route('/admin/getLogins', methods=['GET'])
@login_required
def getLogins():
    if request.method == "GET":
        records = []
        count = 0
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 10))
        offset = (page - 1) * limit
        database_config = config()
        with psycopg2.connect(**database_config) as conn:
            records, count = postsqldb.LoginsTable.paginate_tuples(conn, (limit, offset))
            return jsonify({'logins': records, "end": math.ceil(count/limit), 'error':False, 'message': 'logins Loaded Successfully!'})
    return jsonify({'logins': records, "end": math.ceil(count/limit), 'error':True, 'message': 'There was a problem loading logins!'})

@admin_api.route('/admin/site/postDeleteSite', methods=["POST"])
def postDeleteSite():
    if request.method == "POST":
        site_id = request.get_json()['site_id']
        database_config = config()
        user_id = session['user_id']
        try:
            with psycopg2.connect(**database_config) as conn:
                user = postsqldb.LoginsTable.select_tuple(conn, (user_id,))
                admin_user = (user['username'], user['password'], user['email'], user['row_type'])
                site = postsqldb.SitesTable.select_tuple(conn, (site_id,))
                site = postsqldb.SitesTable.Manager(
                    site['site_name'],
                    admin_user,
                    site['default_zone'],
                    site['default_primary_location'],
                    site['site_description']
                )
                process.deleteSite(site_manager=site)
        except Exception as error:
            conn.rollback()
            return jsonify({'error': True, 'message': error})
        return jsonify({'error': False, 'message': f""})
    return jsonify({'error': True, 'message': f""})

@admin_api.route('/admin/site/postAddSite', methods=["POST"])
def postAddSite():
    if request.method == "POST":
        payload = request.get_json()['payload']
        database_config = config()
        site_name = session['selected_site']
        user_id = session['user_id']
        print(payload)
        try:
            with psycopg2.connect(**database_config) as conn:
                user = postsqldb.LoginsTable.select_tuple(conn, (user_id,))
                admin_user = (user['username'], user['password'], user['email'], user['row_type'])
                site = postsqldb.SitesTable.Manager(
                    payload['site_name'],
                    admin_user,
                    payload['default_zone'],
                    payload['default_primary_location'],
                    payload['site_description']
                )
                process.addSite(site_manager=site)
                
        except Exception as error:
            conn.rollback()
            return jsonify({'error': True, 'message': error})
        return jsonify({'error': False, 'message': f"Zone added to {site_name}."})
    return jsonify({'error': True, 'message': f"These was an error with adding this Zone to {site_name}."})

@admin_api.route('/admin/site/postEditSite', methods=["POST"])
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

@admin_api.route('/admin/role/postAddRole', methods=["POST"])
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

@admin_api.route('/admin/role/postEditRole', methods=["POST"])
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

@admin_api.route('/admin/user/postAddLogin', methods=["POST"])
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

@admin_api.route('/admin/user/postEditLogin', methods=["POST"])
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

@admin_api.route('/admin/user/postEditLoginPassword', methods=["POST"])
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
