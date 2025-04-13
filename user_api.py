from flask import Blueprint, request, render_template, redirect, session, url_for, jsonify
import hashlib, psycopg2, process, MyDataclasses
from config import config, sites_config, setFirstSetupDone
from functools import wraps
from manage import create
from main import create_site, getUser, setSystemAdmin

login_app = Blueprint('login', __name__)

def login_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if 'user' not in session or session['user'] == None:
            return redirect(url_for('login.login'))
        return func(*args, **kwargs)
    return wrapper


@login_app.route('/setup', methods=['GET', 'POST'])
def first_time_setup():
    if request.method == "POST":
        database_address = request.form['database_address']
        database_port = request.form['database_port']
        database_name = request.form['database_name']
        database_user = request.form['database_user']
        database_password = request.form['database_address']

        site_manager = MyDataclasses.SiteManager(
            site_name=request.form['site_name'],
            admin_user=(request.form['username'], hashlib.sha256(request.form['password'].encode()).hexdigest(), request.form['email']),
            default_zone=request.form['site_default_zone'],
            default_location=request.form['site_default_location'],
            description=request.form['site_description']
        )

        process.addSite(site_manager)

        setFirstSetupDone()

        return redirect("/login")
    
    return render_template("setup.html")



@login_app.route('/logout', methods=['GET'])
def logout():
    if 'user' in session.keys():
        session['user'] = None
    return redirect('/login')

@login_app.route('/login', methods=['POST', 'GET'])
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
            return jsonify({'error': False, 'message': 'Logged In Sucessfully!'})
        else:
            return jsonify({'error': True, 'message': 'Username or Password was incorrect!'})

    
    if 'user' not in session.keys():
        session['user'] = None

    return render_template("other/login.html")

@login_app.route('/signup', methods=['POST', 'GET'])
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
