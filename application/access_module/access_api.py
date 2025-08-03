from flask import Blueprint, request, render_template, redirect, session, url_for, jsonify
from authlib.integrations.flask_client import OAuth
import hashlib, psycopg2
from config import config, sites_config
from functools import wraps
import postsqldb
import requests

from application.access_module import access_database
from outh import oauth

access_api = Blueprint('access_api', __name__, template_folder="templates", static_folder="static")




def update_session_user():
    database_config = config()
    with psycopg2.connect(**database_config) as conn:
        user = postsqldb.LoginsTable.get_washed_tuple(conn, (session['user_id'],))
        session['user'] = user

def login_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if 'user' not in session or session['user'] == None:
            return redirect(url_for('access_api.login'))
        return func(*args, **kwargs)
    return wrapper

@access_api.route('/logout', methods=['GET'])
@login_required
def logout():
    if 'user' in session.keys():
        session['user'] = None
    return redirect('/access/login')

@access_api.route('/auth')
def auth():
    token = oauth.authentik.authorize_access_token()
    access_token = token['access_token']
    userinfo_endpoint="https://auth.treehousefullofstars.com/application/o/userinfo/"
    headers = {
        'Authorization': f'Bearer {access_token}',
    }
    response = requests.get(userinfo_endpoint, headers=headers)
    if response.status_code == 200:
        user_email = response.json()['email']
        user = access_database.selectUserByEmail((user_email,))
        user = access_database.washUserDictionary(user)
        session['user_id'] = user['id']
        session['user'] = user
        session['login_type'] = 'External'
        return redirect('/')
    else:
        print("Failed to fetch user info:", response.status_code, response.text)
        return redirect('/access/login')

@access_api.route('/login/oidc')
def oidc_login():
    redirect_uri = url_for('access_api.auth', _external=True)
    return oauth.authentik.authorize_redirect(redirect_uri)

@access_api.route('/login', methods=['POST', 'GET'])
def login():
    session.clear()
    instance_config = sites_config()

    if instance_config['first_setup']:
        return redirect('/setup')

    if request.method == "POST":
        username = request.get_json()['username']
        password = request.get_json()['password']

        password = hashlib.sha256(password.encode()).hexdigest()
        database_config = config()
        with psycopg2.connect(**database_config) as conn:
            try:
                with conn.cursor() as cur:
                    sql = f"SELECT * FROM logins WHERE username=%s;"
                    cur.execute(sql, (username,))
                    user = cur.fetchone()
            except (Exception, psycopg2.DatabaseError) as error:
                conn.rollback()
                return jsonify({'error': True, 'message': str(error)})
        
        if user and user[2] == password:
            session['user_id'] = user[0]
            session['user'] = {'id': user[0], 'username': user[1], 'sites': user[13], 'site_roles': user[14], 'system_admin': user[15], 'flags': user[16]}
            session['login_type'] = 'Internal'
            return jsonify({'error': False, 'message': 'Logged In Sucessfully!'})
        else:
            return jsonify({'error': True, 'message': 'Username or Password was incorrect!'})

    
    if 'user' not in session.keys():
        session['user'] = None

    return render_template("login.html")

@access_api.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect('/')
    return f"Hello, {session['user']['name']}! <a href='/logout'>Logout</a>"

@access_api.route('/signup', methods=['POST', 'GET'])
def signup():
    instance_config = sites_config()
    if not instance_config['signup_enabled']:
        return jsonify({'error': True, 'message': 'It seems that Sign Ups are disabled by the server admin!'})

    if request.method == "POST":
        username = request.get_json()['username']
        password = request.get_json()['password']
        email = request.get_json()['email']
        password = hashlib.sha256(password.encode()).hexdigest()
        database_config = config()
        with psycopg2.connect(**database_config) as conn:
            try:
                with conn.cursor() as cur:
                    sql = f"INSERT INTO logins(username, password, email, row_type) VALUES(%s, %s, %s, %s);"
                    cur.execute(sql, (username, password, email, 'user'))
            except (Exception, psycopg2.DatabaseError) as error:
                conn.rollback()
                return jsonify({'error': True, 'message': str(error)})
        return jsonify({'error': False, 'message': 'You have been signed up successfully, you will have to wait until the server admin finishes your onboarding!'})
    return jsonify({'error': True, 'message': 'There was a problem with this POST request!'})
