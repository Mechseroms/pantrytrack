from flask import Flask, render_template, session, request, redirect
import api, config, external_devices, user_api, psycopg2, main, admin
from user_api import login_required

app = Flask(__name__)
app.secret_key = '11gs22h2h1a4h6ah8e413a45'
app.register_blueprint(api.database_api)
app.register_blueprint(external_devices.external_api)
app.register_blueprint(user_api.login_app)
app.register_blueprint(admin.admin)


@app.context_processor
def inject_user():
    if 'user_id' in session.keys() and session['user_id'] is not None:
        database_config = config.config()
        with psycopg2.connect(**database_config) as conn:
            try:
                with conn.cursor() as cur:
                    sql = f"SELECT * FROM logins WHERE id=%s;"
                    cur.execute(sql, (session['user_id'],))
                    user = cur.fetchone()
                    session['user'] = user
            except (Exception, psycopg2.DatabaseError) as error:
                print(error)
                conn.rollback()
                return dict(username="")

        return dict(
            user_id=session.get('user')[0], 
            username=session.get('user')[1],
            system_admin=session.get('user')[15]
            )
    
    return dict(username="")


@app.route("/group/<id>")
@login_required
def group(id):
    sites = [site[1] for site in main.get_sites(session['user'][13])]
    return render_template("groups/group.html", id=id, current_site=session['selected_site'], sites=sites)

@app.route("/transactions/<id>")
@login_required
def transactions(id):
    sites = [site[1] for site in main.get_sites(session['user'][13])]
    return render_template("items/transactions.html", id=id, current_site=session['selected_site'], sites=sites)


@app.route("/item/<id>")
@login_required
def item(id):
    sites = [site[1] for site in main.get_sites(session['user'][13])]
    return render_template("items/item.html", id=id, current_site=session['selected_site'], sites=sites)

@app.route("/itemlink/<id>")
@login_required
def itemLink(id):
    sites = [site[1] for site in main.get_sites(session['user'][13])]
    return render_template("items/itemlink.html", current_site=session['selected_site'], sites=sites, proto={'referrer': request.referrer}, id=id)

@app.route("/transaction")
@login_required
def transaction():
    sites = [site[1] for site in main.get_sites(session['user'][13])]
    return render_template("transaction.html", current_site=session['selected_site'], sites=sites, proto={'referrer': request.referrer})

@app.route("/admin")
@login_required
def workshop():
    sites = [site[1] for site in main.get_sites(session['user'][13])]
    if not session.get('user')[15]:
        return redirect('/logout')
    return render_template("admin.html", current_site=session['selected_site'], sites=sites)

@app.route("/shopping-list/view/<id>")
@login_required
def shopping_lists_view(id):
    sites = [site[1] for site in main.get_sites(session['user'][13])]
    return render_template("shopping-lists/view.html", id=id, current_site=session['selected_site'], sites=sites)

@app.route("/shopping-list/edit/<id>")
@login_required
def shopping_lists_edit(id):
    sites = [site[1] for site in main.get_sites(session['user'][13])]
    return render_template("shopping-lists/edit.html", id=id, current_site=session['selected_site'], sites=sites)

@app.route("/shopping-lists")
@login_required
def shopping_lists():
    sites = [site[1] for site in main.get_sites(session['user'][13])]
    return render_template("shopping-lists/index.html", current_site=session['selected_site'], sites=sites)

@app.route("/receipt/<id>")
@login_required
def receipt(id):
    sites = [site[1] for site in main.get_sites(session['user'][13])]
    return render_template("receipts/receipt.html", id=id, current_site=session['selected_site'], sites=sites)


@app.route("/receipts")
@login_required
def receipts():
    sites = [site[1] for site in main.get_sites(session['user'][13])]
    return render_template("receipts/index.html", current_site=session['selected_site'], sites=sites)


@app.route("/groups")
@login_required
def groups():
    sites = [site[1] for site in main.get_sites(session['user'][13])]
    return render_template("groups/index.html", 
                           current_site=session['selected_site'], 
                           sites=sites)

@app.route("/items")
@login_required
def items():
    sites = [site[1] for site in main.get_sites(session['user'][13])]
    return render_template("items/index.html", 
                           current_site=session['selected_site'], 
                           sites=sites)

@app.route("/")
@login_required
def home():
    print(session['user'][12])
    sites = [site[1] for site in main.get_sites(session['user'][13])]
    session['selected_site'] = sites[0]
    return redirect("/items")
    return render_template("items/index.html", current_site=session['selected_site'], sites=sites)

app.run(host="0.0.0.0", port=5810, debug=True)