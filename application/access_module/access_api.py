from flask import Blueprint, request, render_template, redirect, session, url_for, jsonify
import hashlib
from config import config, sites_config
from functools import wraps
import requests

from application.access_module import access_database
from application.database_postgres.UsersModel import UsersModel
from outh import oauth

access_api = Blueprint('access_api', __name__, template_folder="templates", static_folder="static")

def update_session_user():
    user = UsersModel.select_tuple(session['selected_site'], {'key': session['user_uuid']})
    user = UsersModel.washUserDictionary(user)
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
    
    if response.status_code != 200:
        print("Failed to fetch user info:", response.status_code, response.text)
        return redirect('/access/login')

    external_user = response.json()
    user = access_database.selectUserByEmail((external_user['email'],))

    if user['login_type'] == "External":
        payload = {
            'id': user['id'],
            'update': {
                'username': external_user['preferred_username'],
                'profile_pic_url': external_user['picture']
            }
        }
        user = access_database.updateLoginsTuple(payload)
        user = access_database.washUserDictionary(user)
        session['user_id'] = user['id']
        session['user'] = user
        return redirect('/')

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
        
        user = UsersModel.select_tuple_by_username({'key': username})
        
        if user and user['user_password'] == password:
            session['user_uuid'] = user['user_uuid']
            session['user'] = UsersModel.washUserDictionary(user)
            session['user_login_type'] = 'Internal'
            return jsonify({'error': False, 'message': 'Logged In Sucessfully!'})
        else:
            return jsonify({'error': True, 'message': 'Username or Password was incorrect!'})

    
    if 'user' not in session.keys():
        session['user'] = None
    
    return render_template("login.html", instance_settings=instance_config)

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

        new_user = UsersModel.Payload(
            user_name=username,
            user_password=password,
            user_email=email
        )

        new_user = UsersModel.insert_tuple('', new_user.payload_dictionary())
        
        return jsonify({'error': False, 'message': 'You have been signed up successfully, you will have to wait until the server admin finishes your onboarding!'})
    return jsonify({'error': True, 'message': 'There was a problem with this POST request!'})
