from flask import Blueprint, request, render_template, redirect, session, url_for, send_file, jsonify, Response, current_app, send_from_directory
import psycopg2, math, json, datetime, main, copy, requests, process, database, pprint, MyDataclasses
from config import config, sites_config
from main import unfoldCostLayers
from user_api import login_required
import os
import postsqldb, webpush
from flasgger import swag_from
from scripts.recipes import database_recipes 
from scripts import postsqldb as db
from flask_restx import Api, fields

recipes_api = Blueprint('recipes_api', __name__)
model_api = Api(recipes_api)

@recipes_api.route("/recipes")
@login_required
def recipes():
    """This is the main endpoint to reach the webpage for a list of all recipes
    ---
    responses:
        200:
            description: returns recipes/index.html with sites, current_site.
    """
    sites = [site[1] for site in main.get_sites(session['user']['sites'])]
    return render_template("recipes/index.html", 
                           current_site=session['selected_site'], 
                           sites=sites)

@recipes_api.route("/recipe/<mode>/<id>")
@login_required
def recipe(id, mode='view'):
    """This is the main endpoint to reach the webpage for a recipe's view or edit mode.
    ---
    parameters:
      - name: mode
        in: path
        type: string
        required: true
        default: view
      - name: id
        in: path
        type: integer
        required: true
        default: all
    responses:
      200:
        description: Respondes with either the Edit or View webpage for the recipe.
    """
    database_config = config()
    with psycopg2.connect(**database_config) as conn:
        units = postsqldb.UnitsTable.getAll(conn)

    if mode == "edit":
        return render_template("recipes/recipe_edit.html", recipe_id=id, current_site=session['selected_site'], units=units)
    if mode == "view":
        return render_template("recipes/recipe_view.html", recipe_id=id, current_site=session['selected_site'])

@recipes_api.route('/recipes/getRecipes', methods=["GET"])
@login_required
def getRecipes():
    """ Get a subquery of recipes from the database by passing a page, limit
    ---
    responses:
        200:
            description: limit of rows passed returned to requester
    """
    recipes = []
    count=0
    if request.method == "GET":
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 1))
        offset = (page-1)*limit
        site_name = session['selected_site']
        recipes, count = database_recipes.getRecipes(site_name, (limit, offset))
        return jsonify({'recipes': recipes, 'end': math.ceil(count/limit), 'error': False, 'message': 'fetch was successful!'})
    return jsonify({'recipes': recipes, 'end': math.ceil(count/limit), 'error': True, 'message': f'method is not allowed: {request.method}'})

@recipes_api.route('/recipe/getRecipe', methods=["GET"])
@login_required
def getRecipe():
    """ Get a query for recipe id from database by passing an id
    ---
    responses:
        200:
            description: id queried successfully!

    """
    recipe = {}
    if request.method == "GET":
        id = int(request.args.get('id', 1))
        site_name = session['selected_site']
        recipe = database_recipes.getRecipe(site_name, (id,), convert=True)
        return jsonify({'recipe': recipe, 'error': False, 'message': 'Recipe returned successfully!'})
    return jsonify({'recipe': recipe, 'error': True, 'message': f'method {request.method} not allowed'})

@recipes_api.route('/recipes/addRecipe', methods=["POST"])
@login_required
def addRecipe():
    """ post a new recipe into the database by passing a recipe_name and recipe description
    ---
    responses:
        200:
            description: Recipe was added successfully into the system
    """
    if request.method == "POST":
        recipe_name = request.get_json()['recipe_name']
        recipe_description = request.get_json()['recipe_description']
        database_config = config()
        site_name = session['selected_site']
        user_id = session['user_id']
        with psycopg2.connect(**database_config) as conn:
            recipe = db.RecipesTable.Payload(
                name=recipe_name,
                author=user_id,
                description=recipe_description
            )
            recipe = database_recipes.postRecipe(site_name, recipe.payload())
            webpush.push_ntfy('New Recipe', f"New Recipe added to {site_name}; {recipe_name}! {recipe_description} \n http://test.treehousefullofstars.com/recipe/view/{recipe['id']} \n http://test.treehousefullofstars.com/recipe/edit/{recipe['id']}")
        return jsonify({'recipe': recipe, 'error': False, 'message': 'Recipe added successful!'})
    return jsonify({'recipe': recipe, 'error': True, 'message': f'method {request.method}'})

@recipes_api.route('/recipe/getItems', methods=["GET"])
@login_required
def getItems():
    """ Pass along a page, limit, and search strings to get a pagination of items from the system
    ---
    responses:
        200:
            description: Items were returned successfully!
    """
    recordset = []
    count = {'count': 0}
    if request.method == "GET":
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 10))
        search_string = request.args.get('search_string', "")
        site_name = session['selected_site']
        offset = (page - 1) * limit
        recordset, count = database_recipes.getModalSKUs(site_name, (search_string, limit, offset))
        return jsonify({"items":recordset, "end":math.ceil(count/limit), "error":False, "message":"items fetched succesfully!"})
    return jsonify({"items":recordset, "end":math.ceil(count/limit), "error":True, "message":"There was an error with this GET statement"})

update_model = model_api.model('model', {
    'id': fields.Integer(min=1),
    'update': fields.Raw(required=True, description="all the data to be updated!")
})

@recipes_api.route('/recipe/postUpdate', methods=["POST"])
@login_required
@model_api.expect(update_model)
def postUpdate():
    """ This is an endpoint for updating an RecipeTuple in the sites recipes table
    ---
    responses:
        200:
            description: The time was updated successfully!

    Returns:
        dict: returns a dictionary containing the updated recipe object, error status, and a message to post for notifications
    """
    recipe = {}
    if request.method == "POST":
        recipe_id = int(request.get_json()['recipe_id'])
        update = request.get_json()['update']
        site_name = session['selected_site']
        recipe = database_recipes.postRecipeUpdate(site_name, {'id': recipe_id, 'update': update})
        return jsonify({'recipe': recipe, 'error': False, 'message': 'Update of Recipe successful!'})
    return jsonify({'recipe': recipe, 'error': True, 'message': 'Update of Recipe unsuccessful!'})

@recipes_api.route('/recipe/postCustomItem', methods=["POST"])
@login_required
def postCustomItem():
    """ post a recipe item to the database by passing a uuid, recipe_id, item_type, item_name, uom, qty, and link
    ---
    responses:
        200:
            description: Recipe Item posted successfully!
    """
    recipe = {}
    if request.method == "POST":
        site_name = session['selected_site']
        rp_id = int(request.get_json()['rp_id'])
        recipe_item = db.RecipesTable.ItemPayload(
            uuid=f"%{int(request.get_json()['rp_id'])}{database.getUUID(6)}%",
            rp_id=rp_id,
            item_type=request.get_json()['item_type'],
            item_name=request.get_json()['item_name'],
            uom=request.get_json()['uom'],
            qty=float(request.get_json()['qty']),
            links=request.get_json()['links']
        )
        database_recipes.postRecipeItem(site_name, recipe_item.payload())
        recipe = database_recipes.getRecipe(site_name, (rp_id, ))
        return jsonify({'recipe': recipe, 'error': False, 'message': 'Recipe Item was added successful!'})
    return jsonify({'recipe': recipe, 'error': True, 'message': f'method {request.method} not allowed!'})

@recipes_api.route('/recipe/postSKUItem', methods=["POST"])
@login_required
def postSKUItem():
    """ post a recipe item to the database by passing a recipe_id and item_id
    ---
    responses:
        200:
            description: recipe item was posted successfully!
    """
    recipe = {}
    if request.method == "POST":
        recipe_id = int(request.get_json()['recipe_id'])
        item_id = int(request.get_json()['item_id'])
        site_name = session['selected_site']
        item = database_recipes.getItemData(site_name, (item_id, ))
        print(item)
        recipe_item = db.RecipesTable.ItemPayload(
            uuid=item['barcode'],
            rp_id=recipe_id,
            item_type='sku',
            item_name=item['item_name'],
            uom=item['uom'],
            qty=float(item['uom_quantity']),
            item_id=item['id'],
            links=item['links']
        )
        database_recipes.postRecipeItem(site_name, recipe_item.payload())
        recipe = database_recipes.getRecipe(site_name, (recipe_id, ))
        return jsonify({'recipe': recipe, 'error': False, 'message': 'Recipe Item was added successful!'})
    return jsonify({'recipe': recipe, 'error': True, 'message': f'method {request.method} is not allowed!'})

@recipes_api.route('/recipe/postImage/<recipe_id>', methods=["POST"])
@login_required
def uploadImage(recipe_id):
    """ post an image for a recipe into the database and files by passing the recipe_id and picture_path
    ---
    parameters:
    - name: recipe_id
      in: path
      required: true
      schema:
        type: integer
    responses:
        200:
            description: image uploaded succesfully!
    """
    file = request.files['file']
    file_path = current_app.config['UPLOAD_FOLDER'] + f"/recipes/{file.filename.replace(" ", "_")}"
    file.save(file_path)
    site_name = session['selected_site']
    database_recipes.postRecipeUpdate(site_name, {'id': recipe_id, 'update': {'picture_path': file.filename.replace(" ", "_")}})    
    return jsonify({'error': False, 'message': 'Recipe was updated successfully!'})

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