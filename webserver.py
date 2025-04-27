import celery.schedules
from flask import Flask, render_template, session, request, redirect, jsonify
from flask_assets import Environment, Bundle
import api, config, user_api, psycopg2, main, api_admin, item_API, receipts_API, shopping_list_API, group_api
from user_api import login_required, update_session_user
from external_API import external_api
from workshop_api import workshop_api
import database
import postsqldb
from webpush import trigger_push_notifications_for_subscriptions
from application.recipes import recipes_api
from flasgger import Swagger


app = Flask(__name__, instance_relative_config=True)
swagger = Swagger(app)
UPLOAD_FOLDER = 'static/pictures'
FILES_FOLDER = 'static/files'
app.config.from_pyfile('application.cfg.py')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['FILES_FOLDER'] = FILES_FOLDER


assets = Environment(app)
app.secret_key = '11gs22h2h1a4h6ah8e413a45'
app.register_blueprint(api.database_api)
app.register_blueprint(user_api.login_app)
app.register_blueprint(api_admin.admin_api)
app.register_blueprint(item_API.items_api)
app.register_blueprint(external_api)
app.register_blueprint(workshop_api)
app.register_blueprint(receipts_API.receipt_api)
app.register_blueprint(shopping_list_API.shopping_list_api)
app.register_blueprint(group_api.groups_api)
app.register_blueprint(recipes_api.recipes_api)



js = Bundle('js/uikit.min.js', 'js/uikit-icons.min.js', output='gen/main.js')
assets.register('js_all', js)

assets.init_app(app)

@app.context_processor
def inject_user():
    if 'user_id' in session.keys() and session['user_id'] is not None:
        database_config = config.config()
        with psycopg2.connect(**database_config) as conn:
            try:
                with conn.cursor() as cur:
                    sql = f"SELECT id, username, sites, site_roles, system_admin, flags FROM logins WHERE id=%s;"
                    cur.execute(sql, (session['user_id'],))
                    user = cur.fetchone()
                    user = database.tupleDictionaryFactory(cur.description, user)
                    session['user'] = user
            except (Exception, psycopg2.DatabaseError) as error:
                print(error)
                conn.rollback()
                return dict(username="")
        return dict(
            user_id=session.get('user')['id'], 
            username=session.get('user')['username'],
            system_admin=session.get('user')['system_admin']
            )
    
    return dict(username="")


@app.route("/transactions/<id>")
@login_required
def transactions(id):
    """This is the main endpoint to reach the webpage for an items transaction history
    ---
    parameters:
      - name: id
        in: path
        type: integer
        required: true
        default: all
    responses:
      200:
        description: Returns the transactions.html webpage for the item with passed ID
    """
    sites = [site[1] for site in main.get_sites(session['user']['sites'])]
    return render_template("items/transactions.html", id=id, current_site=session['selected_site'], sites=sites)


@app.route("/item/<id>")
@login_required
def item(id):
    sites = [site[1] for site in main.get_sites(session['user']['sites'])]
    database_config = config.config()
    with psycopg2.connect(**database_config) as conn:
        units = postsqldb.UnitsTable.getAll(conn)
    return render_template("items/item_new.html", id=id, units=units, current_site=session['selected_site'], sites=sites)

@app.route("/transaction")
@login_required
def transaction():
    sites = [site[1] for site in main.get_sites(session['user']['sites'])]
    database_config = config.config()
    with psycopg2.connect(**database_config) as conn:
        units = postsqldb.UnitsTable.getAll(conn)
    return render_template("other/transaction.html", units=units, current_site=session['selected_site'], sites=sites, proto={'referrer': request.referrer})

@app.route("/items")
@login_required
def items():
    update_session_user()
    sites = [site[1] for site in main.get_sites(session['user']['sites'])]
    return render_template("items/index.html", 
                           current_site=session['selected_site'], 
                           sites=sites)

@app.route("/api/push-subscriptions", methods=["POST"])
def create_push_subscription():
    json_data = request.get_json()
    database_config = config.config()
    with psycopg2.connect(**database_config) as conn:
        with conn.cursor() as cur:
            cur.execute(f"SELECT * FROM push_subscriptions WHERE subscription_json = %s;", (json_data['subscription_json'],))
            rows = cur.fetchone()
            if rows is None:
                cur.execute(f"INSERT INTO push_subscriptions (subscription_json) VALUES (%s);", (json_data['subscription_json'],))
        return jsonify({
            "status": "success"
        })

@app.route("/subscribe")
def subscribe():
    return render_template("subscribe.html")

@app.route("/")
@login_required
def home():
    update_session_user()
    sites = [site[1] for site in main.get_sites(session['user']['sites'])]
    session['selected_site'] = sites[0]
    return redirect("/items")

app.run(host="0.0.0.0", port=5810, debug=True)