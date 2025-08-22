# 3RD PARTY IMPORTS
from flask import (
    Blueprint, request, render_template, redirect, session, url_for, send_file, jsonify, Response
    )
import psycopg2
import math
import datetime

# APPLICATION IMPORTS
from config import config
from application.access_module import access_api
from application import postsqldb, database_payloads
from application.meal_planner import meal_planner_database, meal_planner_processes

meal_planner_api = Blueprint('meal_planner_api', __name__, template_folder="templates", static_folder="static")


@meal_planner_api.route('/', methods=["GET"])
@access_api.login_required
def plannerIndex():
    sites = [site[1] for site in postsqldb.get_sites(session['user']['sites'])]
    return render_template('meal_planner.html', current_site=session['selected_site'], sites=sites)

@meal_planner_api.route('/api/getEventsByMonth', methods=["GET"])
@access_api.login_required
def getEventsByMonth():
    if request.method == "GET":
        site_name = session['selected_site']
        year = int(request.args.get('year', 2025))
        month = int(request.args.get('month', 1))
        events = ()
        events = meal_planner_database.selectPlanEventsByMonth(site_name, (year, month))
        return jsonify(status=201, message="Events fetched Successfully!", events=events)
    return jsonify(status=405, message=f"{request.method} is not an allowed method on this endpoint!", events=events)

@meal_planner_api.route('/api/getEventByUUID', methods=["GET"])
@access_api.login_required
def getEventByUUID():
    if request.method == "GET":
        site_name = session['selected_site']
        event_uuid = request.args.get('event_uuid', "")
        event = ()
        event = meal_planner_database.selectPlanEventByUUID(site_name, (event_uuid,))

        return jsonify(status=201, message="Event fetched Successfully!", event=event)
    return jsonify(status=405, message=f"{request.method} is not an allowed method on this endpoint!", event=event)


@meal_planner_api.route('/api/getRecipes', methods=["GET"])
@access_api.login_required
def getRecipes():
    if request.method == "GET":
        site_name = session['selected_site']
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 50))
        search_string = request.args.get('search_string', "")

        offset = (page - 1) * limit
        recipes, count = [], 0
        recipes, count = meal_planner_database.paginateRecipesTuples(site_name, (limit, offset))

        return jsonify(status=201, message="Recipes fetched Successfully!", recipes=recipes, end=math.ceil(count/limit))
    return jsonify(status=405, message=f"{request.method} is not an allowed method on this endpoint!", recipes=recipes, end=math.ceil(count/limit))


@meal_planner_api.route('/api/getVendors', methods=["GET"])
@access_api.login_required
def getVendors():
    if request.method == "GET":
        site_name = session['selected_site']
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 50))
        search_string = request.args.get('search_string', "")

        offset = (page - 1) * limit
        vendors, count = [], 0
        vendors, count = meal_planner_database.paginateVendorsTuples(site_name, (limit, offset))

        return jsonify(status=201, message="Recipes fetched Successfully!", vendors=vendors, end=math.ceil(count/limit))
    return jsonify(status=405, message=f"{request.method} is not an allowed method on this endpoint!", vendors=vendors, end=math.ceil(count/limit))


@meal_planner_api.route('/api/addEvent', methods=["POST"])
@access_api.login_required
def addEvent():
    if request.method == "POST":
        site_name = session['selected_site']
        event_date_start = datetime.datetime.strptime(request.get_json()['event_date_start'], "%Y-%m-%d")
        event_date_end = datetime.datetime.strptime(request.get_json()['event_date_end'], "%Y-%m-%d")

        event_payload = database_payloads.PlanEventPayload(
            plan_uuid=None,
            event_shortname=request.get_json()['event_shortname'],
            event_description=request.get_json()['event_description'],
            event_date_start=event_date_start,
            event_date_end=event_date_end,
            created_by=session['user_id'],
            recipe_uuid=request.get_json()['recipe_uuid'],
            receipt_uuid=None,
            event_type=request.get_json()['event_type']
        )

        meal_planner_database.insertPlanEventTuple(site_name, event_payload.payload())

        return jsonify(status=201, message="Event added Successfully!")
    return jsonify(status=405, message=f"{request.method} is not an allowed method on this endpoint!")

@meal_planner_api.route('/api/addTOEvent', methods=["POST"])
@access_api.login_required
def addTOEvent():
    if request.method == "POST":
        site_name = session['selected_site']
        data= request.get_json()
        user_id = session['user_id']

        meal_planner_processes.addTakeOutEvent(site_name, data, user_id)

        return jsonify(status=201, message="Event added Successfully!")
    return jsonify(status=405, message=f"{request.method} is not an allowed method on this endpoint!")


@meal_planner_api.route('/api/saveEvent', methods=["POST"])
@access_api.login_required
def saveEvent():
    if request.method == "POST":
        site_name = session['selected_site']
        event_uuid = request.get_json()['event_uuid']
        update = request.get_json()['update']

        meal_planner_database.updatePlanEventTuple(site_name, {'uuid': event_uuid, "update": update})

        return jsonify(status=201, message="Event Saved Successfully!")
    return jsonify(status=405, message=f"{request.method} is not an allowed method on this endpoint!")

@meal_planner_api.route('/api/removeEvent', methods=["POST"])
@access_api.login_required
def removeEvent():
    if request.method == "POST":
        site_name = session['selected_site']
        event_uuid = request.get_json()['event_uuid']

        meal_planner_database.deletePlanEventTuple(site_name, (event_uuid, ))

        return jsonify(status=201, message="Event removed Successfully!")
    return jsonify(status=405, message=f"{request.method} is not an allowed method on this endpoint!")