from flask import Flask, render_template, session, request, redirect, jsonify
from flask_assets import Environment, Bundle
from authlib.integrations.flask_client import OAuth
import config, psycopg2, main
import database
from webpush import trigger_push_notifications_for_subscriptions
from application.administration import administration_api
from application.access_module import access_api
from application.site_management import site_management_api
from application.recipes import recipes_api
from application.items import items_API
from application.poe import poe_api
from application.shoppinglists import shoplist_api
from application.receipts import receipts_api
from flasgger import Swagger
from outh import oauth

app = Flask(__name__, instance_relative_config=True)
oauth.init_app(app)
swagger = Swagger(app)
UPLOAD_FOLDER = 'static/pictures'
FILES_FOLDER = 'static/files'
app.config.from_pyfile('application.cfg.py')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['FILES_FOLDER'] = FILES_FOLDER

oauth.register(
    name='authentik',
    client_id='gh8rLyXC6hfI7W5mDX26OJFGHxmU0nMzeYl3B04G',
    client_secret='aRHyAkDDeU22s69Ig0o7f46Xn3HCnB8guZoMHuA23B7x1e2YL8FhAqZbu1f3naiaLyTLi9ICIiBc6dxOp5eIO4fEI9paL2NwKXmqYCRmzNzWAfwmcsIh2qTlQfAfsh6e',
    access_token_url="https://auth.treehousefullofstars.com/application/o/token/",
    authorize_url="https://auth.treehousefullofstars.com/application/o/authorize/",
    userinfo_endpoint="https://auth.treehousefullofstars.com/application/o/userinfo/",
    api_base_url="https://auth.treehousefullofstars.com/application/o/",
    jwks_uri="https://auth.treehousefullofstars.com/application/o/pantry/jwks/",
    client_kwargs={'scope': 'openid profile email'},
)


assets = Environment(app)
app.secret_key = '11gs22h2h1a4h6ah8e413a45'
app.register_blueprint(access_api.access_api, url_prefix="/access")
app.register_blueprint(administration_api.admin_api, url_prefix='/admin')
app.register_blueprint(items_API.items_api, url_prefix='/items')
app.register_blueprint(poe_api.point_of_ease, url_prefix='/poe')
app.register_blueprint(site_management_api.site_management_api, url_prefix="/site_management")
app.register_blueprint(receipts_api.receipt_api, url_prefix='/receipts')
app.register_blueprint(shoplist_api.shopping_list_api, url_prefix="/shopping-lists")
app.register_blueprint(recipes_api.recipes_api, url_prefix='/recipes')

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

@app.route("/changeSite", methods=["POST"])
def changeSite():
    if request.method == "POST":
        site = request.json['site']
    session['selected_site'] = site
    return jsonify({'error': False, 'message': 'Site Changed!'})

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
@access_api.login_required
def home():
    access_api.update_session_user()
    sites = [site[1] for site in main.get_sites(session['user']['sites'])]
    session['selected_site'] = sites[0]
    return redirect("/items")

app.run(host="0.0.0.0", port=5811, debug=True)