from flask import Blueprint, request, render_template, redirect, session, url_for, send_file, jsonify, Response, current_app, send_from_directory
import psycopg2, math, json, datetime, main, copy, requests, process, database, pprint, MyDataclasses
from config import config, sites_config
from main import unfoldCostLayers
from user_api import login_required
import os
import postsqldb

recipes_api = Blueprint('recipes_api', __name__)

@recipes_api.route("/recipes")
@login_required
def recipes():
    sites = [site[1] for site in main.get_sites(session['user']['sites'])]
    return render_template("recipes/index.html", 
                           current_site=session['selected_site'], 
                           sites=sites)

@recipes_api.route("/recipe/<mode>/<id>")
@login_required
def recipe(mode, id):

    database_config = config()
    with psycopg2.connect(**database_config) as conn:
        units = postsqldb.UnitsTable.getAll(conn)

    if mode == "edit":
        return render_template("recipes/recipe_edit.html", recipe_id=id, current_site=session['selected_site'], units=units)
    if mode == "view":
        return render_template("recipes/recipe_view.html", recipe_id=id, current_site=session['selected_site'])


@recipes_api.route('/recipes/getRecipes', methods=["GET"])
def getRecipes():
    recipes = []
    if request.method == "GET":
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 1))
        offset = (page-1)*limit
        database_config = config()
        site_name = session['selected_site']
        with psycopg2.connect(**database_config) as conn:
            recipes, count = postsqldb.RecipesTable.getRecipes(conn, site_name, (limit, offset), convert=True)
    return jsonify({'recipes': recipes, 'end': math.ceil(count/limit), 'error': False, 'message': 'bleh'})

@recipes_api.route('/recipe/getRecipe', methods=["GET"])
def getRecipe():
    recipe = {}
    if request.method == "GET":
        id = int(request.args.get('id', 1))
        database_config = config()
        site_name = session['selected_site']
        with psycopg2.connect(**database_config) as conn:
            recipe = postsqldb.RecipesTable.getRecipe(conn, site_name, (id,), convert=True)
    return jsonify({'recipe': recipe, 'error': False, 'message': 'bleh'})

@recipes_api.route('/recipes/addRecipe', methods=["POST"])
def addRecipe():
    if request.method == "POST":
        recipe_name = request.get_json()['recipe_name']
        recipe_description = request.get_json()['recipe_description']
        database_config = config()
        site_name = session['selected_site']
        user_id = session['user_id']
        with psycopg2.connect(**database_config) as conn:
            recipe = postsqldb.RecipesTable.Payload(
                name=recipe_name,
                author=user_id,
                description=recipe_description
            )
            postsqldb.RecipesTable.insert_tuple(conn, site_name, recipe.payload())
        return jsonify({'recipe': recipe, 'error': False, 'message': 'Add Recipe successful!'})
    return jsonify({'recipe': recipe, 'error': True, 'message': 'Add Recipe unsuccessful!'})

@recipes_api.route('/recipe/getItems', methods=["GET"])
def getItems():
    recordset = []
    count = {'count': 0}
    if request.method == "GET":
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 10))
        search_string = request.args.get('search_string', 10)
        site_name = session['selected_site']
        offset = (page - 1) * limit
        database_config = config()
        with psycopg2.connect(**database_config) as conn:
            payload = (search_string, limit, offset)
            recordset, count = database.getItemsWithQOH(conn, site_name, payload, convert=True)
        return jsonify({"items":recordset, "end":math.ceil(count['count']/limit), "error":False, "message":"items fetched succesfully!"})
    return jsonify({"items":recordset, "end":math.ceil(count['count']/limit), "error":True, "message":"There was an error with this GET statement"})


@recipes_api.route('/recipe/postUpdate', methods=["POST"])
def postUpdate():
    recipe = {}
    if request.method == "POST":
        recipe_id = int(request.get_json()['recipe_id'])
        update = request.get_json()['update']
        database_config = config()
        site_name = session['selected_site']
        with psycopg2.connect(**database_config) as conn:
            recipe = postsqldb.RecipesTable.updateRecipe(conn, site_name, {'id': recipe_id, 'update': update}, convert=True)
        return jsonify({'recipe': recipe, 'error': False, 'message': 'Update of Recipe successful!'})
    return jsonify({'recipe': recipe, 'error': True, 'message': 'Update of Recipe unsuccessful!'})

@recipes_api.route('/recipe/postCustomItem', methods=["POST"])
def postCustomItem():
    recipe = {}
    if request.method == "POST":
        database_config = config()
        site_name = session['selected_site']
        with psycopg2.connect(**database_config) as conn:
            recipe_item = postsqldb.RecipesTable.ItemPayload(
                uuid=f"%{int(request.get_json()['rp_id'])}{database.getUUID(6)}%",
                rp_id=int(request.get_json()['rp_id']),
                item_type=request.get_json()['item_type'],
                item_name=request.get_json()['item_name'],
                uom=request.get_json()['uom'],
                qty=float(request.get_json()['qty']),
                links=request.get_json()['links']
            )
            postsqldb.RecipesTable.insert_item_tuple(conn, site_name, recipe_item.payload(), convert=True)
            recipe = postsqldb.RecipesTable.getRecipe(conn, site_name, (int(request.get_json()['rp_id']), ), convert=True)
        return jsonify({'recipe': recipe, 'error': False, 'message': 'Recipe Item was added successful!'})
    return jsonify({'recipe': recipe, 'error': True, 'message': 'Recipe Item was not added unsuccessful!'})

@recipes_api.route('/recipe/postSKUItem', methods=["POST"])
def postSKUItem():
    recipe = {}
    if request.method == "POST":
        recipe_id = int(request.get_json()['recipe_id'])
        item_id = int(request.get_json()['item_id'])

        database_config = config()
        site_name = session['selected_site']
        with psycopg2.connect(**database_config) as conn:
            item = database.getItemAllByID(conn, site_name, (item_id, ), convert=True)
            recipe_item = postsqldb.RecipesTable.ItemPayload(
                uuid=item['barcode'],
                rp_id=recipe_id,
                item_type='sku',
                item_name=item['item_name'],
                uom=item['item_info']['uom']['id'],
                qty=float(item['item_info']['uom_quantity']),
                item_id=item['id'],
                links=item['links']
            )
            postsqldb.RecipesTable.insert_item_tuple(conn, site_name, recipe_item.payload(), convert=True)
            recipe = postsqldb.RecipesTable.getRecipe(conn, site_name, (recipe_id, ), convert=True)
        return jsonify({'recipe': recipe, 'error': False, 'message': 'Recipe Item was added successful!'})
    return jsonify({'recipe': recipe, 'error': True, 'message': 'Recipe Item was not added unsuccessful!'})

@recipes_api.route('/recipe/postImage/<recipe_id>', methods=["POST"])
def uploadImage(recipe_id):
    file = request.files['file']
    file_path = current_app.config['UPLOAD_FOLDER'] + f"/recipes/{file.filename.replace(" ", "_")}"
    file.save(file_path)

    database_config = config()
    site_name = session['selected_site']
    with psycopg2.connect(**database_config) as conn:
        postsqldb.RecipesTable.updateRecipe(conn, site_name, {'id': recipe_id, 'update': {'picture_path': file.filename.replace(" ", "_")}})
    
    return jsonify({})

@recipes_api.route('/recipe/getImage/<recipe_id>')
def get_image(recipe_id):
    database_config = config()
    site_name = session['selected_site']
    with psycopg2.connect(**database_config) as conn:
        with conn.cursor() as cur:
            cur.execute(f"SELECT picture_path FROM {site_name}_recipes WHERE id=%s;", (recipe_id,))
            rows = cur.fetchone()[0]
            return send_from_directory('static/pictures/recipes', rows)

@recipes_api.route('/recipe/deleteRecipeItem', methods=["POST"])
def deleteRecipeItem():
    recipe = {}
    if request.method == "POST":
        id = int(request.get_json()['id'])
        database_config = config()
        site_name = session['selected_site']
        with psycopg2.connect(**database_config) as conn:
            deleted_item = postsqldb.RecipesTable.delete_item_tuple(conn, site_name, (id, ), convert=True)
            recipe = postsqldb.RecipesTable.getRecipe(conn, site_name, (int(deleted_item['rp_id']), ), convert=True)
        return jsonify({'recipe': recipe, 'error': False, 'message': f'Recipe Item {deleted_item['item_name']} was deleted successful!'})
    return jsonify({'recipe': recipe, 'error': True, 'message': 'Recipe Item was not deleted unsuccessful!'})

@recipes_api.route('/recipe/saveRecipeItem', methods=["POST"])
def saveRecipeItem():
    recipe = {}
    if request.method == "POST":
        id = int(request.get_json()['id'])
        update = request.get_json()['update']
        database_config = config()
        site_name = session['selected_site']
        with psycopg2.connect(**database_config) as conn:
            updated_line = postsqldb.RecipesTable.update_item_tuple(conn, site_name, {'id': id, 'update': update}, convert=True)
            recipe = postsqldb.RecipesTable.getRecipe(conn, site_name, (int(updated_line['rp_id']), ), convert=True)
        return jsonify({'recipe': recipe, 'error': False, 'message': f'Recipe Item {updated_line['item_name']} was updated successful!'})
    return jsonify({'recipe': recipe, 'error': True, 'message': 'Recipe Item was not updated unsuccessful!'})