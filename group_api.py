from flask import Blueprint, request, render_template, redirect, session, url_for, send_file, jsonify, Response
import psycopg2, math, json, datetime, main, copy, requests, process, database, pprint, MyDataclasses
from config import config, sites_config
from main import unfoldCostLayers
from user_api import login_required

groups_api = Blueprint('groups_api', __name__)

@groups_api.route("/groups")
@login_required
def groups():
    sites = [site[1] for site in main.get_sites(session['user']['sites'])]
    return render_template("groups/index.html", 
                           current_site=session['selected_site'], 
                           sites=sites)

@groups_api.route("/group/<id>")
@login_required
def group(id):
    sites = [site[1] for site in main.get_sites(session['user']['sites'])]
    return render_template("groups/group.html", id=id, current_site=session['selected_site'], sites=sites)

@groups_api.route('/groups/getGroups', methods=["GET"])
def getGroups():
    groups = []
    if request.method == "GET":
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 1))
        offset = (page-1)*limit
        database_config = config()
        site_name = session['selected_site']
        with psycopg2.connect(**database_config) as conn:
            groups, count = database.getGroups(conn, site_name, (limit, offset), convert=True)
    return jsonify({'groups': groups, 'end': math.ceil(count/limit), 'error': False, 'message': 'bleh'})