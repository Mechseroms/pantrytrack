# 3RD PARTY IMPORTS
from flask import (
    Blueprint, request, render_template, session, jsonify, current_app, send_from_directory
    )
import math

# APPLICATION IMPORTS
import main
import webpush
from application.access_module import access_api
from application.recipes import database_recipes, recipe_processes
from application import postsqldb as db

recipes_api = Blueprint('recipes_api', __name__, template_folder="templates", static_folder="static")

@recipes_api.route("/")
@access_api.login_required
def recipes():
    sites = [site[1] for site in main.get_sites(session['user']['sites'])]
    return render_template("recipes_index.html", 
                           current_site=session['selected_site'], 
                           sites=sites)

@recipes_api.route("/<mode>/<id>")
@access_api.login_required
def recipe(id, mode='view'):
    units = database_recipes.getUnits()
    print("woot")
    print(session)
    if mode == "edit":
        return render_template("recipe_edit.html", recipe_id=id, current_site=session['selected_site'], units=units)
    if mode == "view":
        return render_template("recipe_view.html", recipe_id=id, current_site=session['selected_site'])

@recipes_api.route('/getRecipes', methods=["GET"])
@access_api.login_required
def getRecipes():
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

@recipes_api.route('/api/deleteRecipe', methods=["POST"])
@access_api.login_required
def deleteRecipe():
    if request.method == "POST":
        recipe_id = request.get_json()['recipe_id']
        site_name = session['selected_site']
        database_recipes.deleteRecipe(site_name, (recipe_id, ))
        return jsonify(status=201, message="Recipe deleted successfully!")
    return jsonify(status=405, message=f"{request.method} is not an allowed method on this endpoint.")

@recipes_api.route('/getRecipe', methods=["GET"])
@access_api.login_required
def getRecipe():
    recipe = {}
    if request.method == "GET":
        id = int(request.args.get('id', 1))
        site_name = session['selected_site']
        recipe = database_recipes.getRecipe(site_name, (id,), convert=True)
        return jsonify({'recipe': recipe, 'error': False, 'message': 'Recipe returned successfully!'})
    return jsonify({'recipe': recipe, 'error': True, 'message': f'method {request.method} not allowed'})

@recipes_api.route('/addRecipe', methods=["POST"])
@access_api.login_required
def addRecipe():
    if request.method == "POST":
        recipe_name = request.get_json()['recipe_name']
        recipe_description = request.get_json()['recipe_description']
        site_name = session['selected_site']
        user_id = session['user_id']
        recipe = db.RecipesTable.Payload(
            name=recipe_name,
            author=user_id,
            description=recipe_description
        )
        recipe = database_recipes.postAddRecipe(site_name, recipe.payload())
        webpush.push_ntfy('New Recipe', f"New Recipe added to {site_name}; {recipe_name}! {recipe_description} \n http://test.treehousefullofstars.com/recipe/view/{recipe['id']} \n http://test.treehousefullofstars.com/recipe/edit/{recipe['id']}")
        return jsonify({'recipe': recipe, 'error': False, 'message': 'Recipe added successful!'})
    return jsonify({'recipe': recipe, 'error': True, 'message': f'method {request.method}'})

@recipes_api.route('/getItems', methods=["GET"])
@access_api.login_required
def getItems():
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

@recipes_api.route('/postUpdate', methods=["POST"])
@access_api.login_required
def postUpdate():
    recipe = {}
    if request.method == "POST":
        recipe_id = int(request.get_json()['recipe_id'])
        update = request.get_json()['update']
        site_name = session['selected_site']
        recipe = database_recipes.postUpdateRecipe(site_name, {'id': recipe_id, 'update': update})
        return jsonify({'recipe': recipe, 'error': False, 'message': 'Update of Recipe successful!'})
    return jsonify({'recipe': recipe, 'error': True, 'message': 'Update of Recipe unsuccessful!'})

@recipes_api.route('/postCustomItem', methods=["POST"])
@access_api.login_required
def postCustomItem():
    recipe = {}
    if request.method == "POST":
        site_name = session['selected_site']
        rp_id = int(request.get_json()['rp_id'])
        recipe_item = db.RecipesTable.ItemPayload(
            item_uuid=None,
            rp_id=rp_id,
            item_type=request.get_json()['item_type'],
            item_name=request.get_json()['item_name'],
            uom=request.get_json()['uom'],
            qty=float(request.get_json()['qty']),
            links=request.get_json()['links']
        )
        database_recipes.postAddRecipeItem(site_name, recipe_item.payload())
        recipe = database_recipes.getRecipe(site_name, (rp_id, ))
        return jsonify({'recipe': recipe, 'error': False, 'message': 'Recipe Item was added successful!'})
    return jsonify({'recipe': recipe, 'error': True, 'message': f'method {request.method} not allowed!'})

@recipes_api.route('/postSKUItem', methods=["POST"])
@access_api.login_required
def postSKUItem():
    recipe = {}
    if request.method == "POST":
        recipe_id = int(request.get_json()['recipe_id'])
        item_id = int(request.get_json()['item_id'])
        site_name = session['selected_site']
        item = database_recipes.getItemData(site_name, (item_id, ))
        recipe_item = db.RecipesTable.ItemPayload(
            item_uuid=item['item_uuid'],
            rp_id=recipe_id,
            item_type='sku',
            item_name=item['item_name'],
            uom=item['uom'],
            qty=float(item['uom_quantity']),
            item_id=item['id'],
            links=item['links']
        )
        database_recipes.postAddRecipeItem(site_name, recipe_item.payload())
        recipe = database_recipes.getRecipe(site_name, (recipe_id, ))
        return jsonify({'recipe': recipe, 'error': False, 'message': 'Recipe Item was added successful!'})
    return jsonify({'recipe': recipe, 'error': True, 'message': f'method {request.method} is not allowed!'})

@recipes_api.route('/postImage/<recipe_id>', methods=["POST"])
@access_api.login_required
def uploadImage(recipe_id):
    file = request.files['file']
    file_path = current_app.config['UPLOAD_FOLDER'] + f"/recipes/{file.filename.replace(" ", "_")}"
    file.save(file_path)
    site_name = session['selected_site']
    database_recipes.postUpdateRecipe(site_name, {'id': recipe_id, 'update': {'picture_path': file.filename.replace(" ", "_")}})    
    return jsonify({'error': False, 'message': 'Recipe was updated successfully!'})

@recipes_api.route('/getImage/<recipe_id>')
@access_api.login_required
def get_image(recipe_id):
    site_name = session['selected_site']
    picture_path = database_recipes.getPicturePath(site_name, (recipe_id,))
    path = f"{current_app.config['UPLOAD_FOLDER']}/recipes"
    return send_from_directory(path, picture_path)

@recipes_api.route('/deleteRecipeItem', methods=["POST"])
@access_api.login_required
def deleteRecipeItem():
    recipe = {}
    if request.method == "POST":
        id = int(request.get_json()['id'])
        site_name = session['selected_site']
        deleted_item = database_recipes.postDeleteRecipeItem(site_name, (id, ))
        recipe = database_recipes.getRecipe(site_name, (int(deleted_item['rp_id']),))
        return jsonify({'recipe': recipe, 'error': False, 'message': f'Recipe Item {deleted_item['item_name']} was deleted successful!'})
    return jsonify({'recipe': recipe, 'error': True, 'message': f'method {request.method} is not allowed!'})

@recipes_api.route('/api/saveRecipeItem', methods=["POST"])
@access_api.login_required
def saveRecipeItem():
    recipe = {}
    if request.method == "POST":
        id = int(request.get_json()['id'])
        update = request.get_json()['update']
        site_name = session['selected_site']
        updated_line = database_recipes.postUpdateRecipeItem(site_name, {'id': id, 'update': update})
        recipe = database_recipes.getRecipe(site_name, (int(updated_line['rp_id']), ))
        return jsonify({'recipe': recipe, 'error': False, 'message': f'Recipe Item {updated_line['item_name']} was updated successful!'})
    return jsonify({'recipe': recipe, 'error': True, 'message': f'method {request.method} not allowed!'})


@recipes_api.route('/api/receiptRecipe', methods=["POST"])
@access_api.login_required
def receiptRecipe():
    if request.method == "POST":
        site_name = session['selected_site']
        user_id = session['user_id']
        status, message = recipe_processes.process_recipe_receipt(site_name, user_id, request.get_json())
        if not status:
            return jsonify(status=400, message=message)
        return jsonify(status=201, message="Recipe Transacted Successfully!")
    return jsonify(status=405, message=f"{request.method} is not an allowed method on this endpoint!")