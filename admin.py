from flask import Blueprint, request, render_template, redirect, session, url_for, send_file, jsonify, Response
import psycopg2, math, json, datetime, main, copy, requests
from config import config, sites_config
from main import unfoldCostLayers, get_sites, get_roles, create_site_secondary, getUser
from manage import create

admin = Blueprint('admin_api', __name__)

@admin.route("/admin/getSites")
def getSites():
    sites = get_sites(session.get('user')[13])
    return jsonify(sites=sites)

@admin.route("/getRoles")
def getRoles():
    sites_roles = {}
    sites = get_sites(session.get('user')[13])
    for site in sites:
        site_roles = get_roles(site_id=site[0])
        sites_roles[site[1]] = site_roles
    return jsonify(sites=sites_roles)

@admin.route("/admin/getUsers", methods=["POST"])
def getUsers():
    if request.method == "POST":
        page = request.get_json()['page']
        limit = request.get_json()['limit']
        offset = (page - 1) * limit

        database_config = config()
        with psycopg2.connect(**database_config) as conn:
            try:
                with conn.cursor() as cur:
                    sql = f"SELECT * FROM logins LIMIT %s OFFSET %s;"
                    cur.execute(sql, (limit, offset))
                    users = cur.fetchall()
                    cur.execute("SELECT COUNT(*) FROM main_items;")
                    count = cur.fetchone()[0]
                    return jsonify(users=users, endpage=math.ceil(count/limit))
            except (Exception, psycopg2.DatabaseError) as error:
                print(error)
                conn.rollback()
                return jsonify(message="FAILED")
    return jsonify(message="FAILED")


@admin.route("/admin/editRole/<id>")
def getRole(id):
    database_config = config()
    with psycopg2.connect(**database_config) as conn:
        try:
            with conn.cursor() as cur:
                sql = f"SELECT * FROM roles LEFT JOIN sites ON sites.id = roles.site_id WHERE roles.id = %s;"
                cur.execute(sql, (id, ))
                role = cur.fetchone()
                return render_template("admin/role.html", role=role, proto={'referrer': request.referrer})
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)
            conn.rollback()
            return jsonify(message="FAILED")

@admin.route("/addRole", methods=["POST"])
def addRole():
    if request.method == "POST":
        role_name = request.get_json()['role_name']
        role_description = request.get_json()['role_description']
        site_id = request.get_json()['site_id']


        sql = f"INSERT INTO roles (role_name, role_description, site_id) VALUES (%s, %s, %s);"
        print(role_name, role_description, site_id)


        database_config = config()
        with psycopg2.connect(**database_config) as conn:
            try:
                with conn.cursor() as cur:
                    data = (role_name, role_description, site_id)
                    cur.execute(sql, data)            
            except (Exception, psycopg2.DatabaseError) as error:
                print(error)
                conn.rollback()
                return jsonify(message="FAILED")

        return jsonify(message="SUCCESS")
    
    return jsonify(message="FAILED")

@admin.route("/deleteRole", methods=["POST"])
def deleteRole():
    if request.method == "POST":
        role_id = request.get_json()['role_id']
        database_config = config()
        with psycopg2.connect(**database_config) as conn:
            try:
                with conn.cursor() as cur:
                    sql = f"DELETE FROM roles WHERE roles.id = %s;"
                    cur.execute(sql, (role_id, ))
                    return jsonify(message="Role Deleted!")            
            except (Exception, psycopg2.DatabaseError) as error:
                print(error)
                conn.rollback()
                return jsonify(message=error)
    return jsonify(message="FAILED")

@admin.route("/addSite", methods=["POST"])
async def addSite():
    if request.method == "POST":
        site_name = request.get_json()['site_name']
        site_description = request.get_json()['site_description']
        default_zone = request.get_json()["default_zone"]
        default_location = request.get_json()['default_location']
        username = session.get('user')[1]
        user_id = session.get('user')[0]

        create(site_name, username, default_zone, default_location)
        result = await create_site_secondary(site_name, user_id, default_zone, default_location, default_location, site_description)
        
        if result:
            return jsonify(message="Success!")
        
    return jsonify(message="Failed!")