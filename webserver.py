from flask import Flask, render_template, session, request, redirect, jsonify, send_from_directory
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
from application.meal_planner import meal_planner_api
from application.database_postgres.UsersModel import UsersModel
from application.database_postgres.SitesModel import SitesModel
from flasgger import Swagger
from outh import oauth

psycopg2.extras.register_uuid()

def create_app():
    app = Flask(__name__, instance_relative_config=True)
    oauth.init_app(app)
    swagger = Swagger(app)
    app.config.from_pyfile('application.cfg.py')

    oauth.register(
        name=app.config['OAUTH_NAME'],
        client_id=app.config['OAUTH_CLIENT_ID'],
        client_secret=app.config['OAUTH_CLIENT_SECRET'],
        access_token_url=app.config['OAUTH_ACCESS_TOKEN_URL'],
        authorize_url=app.config['OAUTH_AUTHORIZE_URL'],
        userinfo_endpoint=app.config['OAUTH_USERINFO_ENDPOINT'],
        api_base_url=app.config['OAUTH_API_BASE_URL'],
        jwks_uri=app.config['OAUTH_JWKS_URI'],
        client_kwargs=app.config['OAUTH_CLIENT_KWARGS'],
    )


    assets = Environment(app)
    app.secret_key = app.config['APP_SECRET']
    app.register_blueprint(access_api.access_api, url_prefix="/access")
    app.register_blueprint(administration_api.admin_api, url_prefix='/administration')
    app.register_blueprint(items_API.items_api, url_prefix='/items')
    app.register_blueprint(poe_api.point_of_ease, url_prefix='/poe')
    app.register_blueprint(site_management_api.site_management_api, url_prefix="/site-management")
    app.register_blueprint(receipts_api.receipt_api, url_prefix='/receipts')
    app.register_blueprint(shoplist_api.shopping_list_api, url_prefix="/shopping-lists")
    app.register_blueprint(recipes_api.recipes_api, url_prefix='/recipes')
    app.register_blueprint(meal_planner_api.meal_planner_api, url_prefix='/planner')

    js = Bundle('js/uikit.min.js', 'js/uikit-icons.min.js', output='gen/main.js')
    assets.register('js_all', js)

    assets.init_app(app)
    return app

app = create_app()


@app.context_processor
def inject_user():
    if 'user_uuid' in session.keys() and session['user_uuid'] is not None:
        user = UsersModel.select_tuple('', {'key': session['user_uuid']})
        session['user'] = user
        if user:
            return dict(
                user_uuid=session.get('user')['user_uuid'], 
                username=session.get('user')['user_name'],
                system_admin=session.get('user')['user_is_system_admin']
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

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(
        app.static_folder, 'pictures/favicon.ico', mimetype='image/vnd.microsoft.icon'
    )

@app.route("/")
@access_api.login_required
def home():
    sites = [SitesModel.select_tuple('', {'key': site})['site_name'] for site in session['user'].get('user_sites', [])]
    session['selected_site'] = sites[0]
    access_api.update_session_user()
    return redirect("/items")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5811, debug=True)