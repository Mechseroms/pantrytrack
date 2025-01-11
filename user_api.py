from flask import Blueprint, request, render_template, redirect, session, url_for
import hashlib, psycopg2
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

        username = request.form['username']
        email = request.form['email']
        password = hashlib.sha256(request.form['password'].encode()).hexdigest()
        
        site_name = request.form['site_name']
        site_description = request.form['site_description']
        site_default_zone = request.form['site_default_zone']
        site_default_location = request.form['site_default_location']

        print(email, site_description)

        create(site_name, username, site_default_zone, site_default_location, email=email)
        create_site(site_name, (username, password, email), site_default_zone, site_default_location, site_default_location, site_description)
        setFirstSetupDone()
        user = getUser(username, password)
        setSystemAdmin(user_id=user[0])
        

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
    print(instance_config["first_setup"])

    if instance_config['first_setup']:
        return redirect('/setup')

    if request.method == "POST":
        username = request.form['username']
        password = hashlib.sha256(request.form['password'].encode()).hexdigest()
        database_config = config()
        with psycopg2.connect(**database_config) as conn:
            try:
                with conn.cursor() as cur:
                    sql = f"SELECT * FROM logins WHERE username=%s;"
                    cur.execute(sql, (username,))
                    user = cur.fetchone()
            except (Exception, psycopg2.DatabaseError) as error:
             print(error)
             conn.rollback()
         
        if user and user[2] == password:
            session['user_id'] = user[0]
            session['user'] = user
            return redirect('/')
    
    if 'user' not in session.keys():
        session['user'] = None

    return render_template("login.html")

@login_app.route('/signup', methods=['POST', 'GET'])
def signup():

    instance_config = sites_config()
    print(instance_config["signup_enabled"])

    if not instance_config['signup_enabled']:
        return redirect('/login')

    if request.method == "POST":
        username = request.form['username']
        password = hashlib.sha256(request.form['password'].encode()).hexdigest()
        database_config = config()
        with psycopg2.connect(**database_config) as conn:
            try:
                with conn.cursor() as cur:
                    sql = f"INSERT INTO logins(username, password) VALUES(%s, %s);"
                    cur.execute(sql, (username, password))
            except (Exception, psycopg2.DatabaseError) as error:
             print(error)
             conn.rollback()

        return redirect("/login")
    
    return render_template("signup.html")