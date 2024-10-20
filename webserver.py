from flask import Flask, render_template, session
import api, config
app = Flask(__name__)
app.secret_key = '11gs22h2h1a4h6ah8e413a45'
app.register_blueprint(api.database_api)

@app.route("/group/<id>")
def group(id):
    sites = config.sites_config()
    return render_template("groups/group.html", id=id, current_site=session['selected_site'], sites=sites['sites'])

@app.route("/workshop")
def workshop():
    sites = config.sites_config()
    return render_template("workshop.html", current_site=session['selected_site'], sites=sites['sites'])

@app.route("/shopping-list/view/<id>")
def shopping_lists_view(id):
    sites = config.sites_config()
    return render_template("shopping-lists/view.html", id=id, current_site=session['selected_site'], sites=sites['sites'])

@app.route("/shopping-list/edit/<id>")
def shopping_lists_edit(id):
    sites = config.sites_config()
    return render_template("shopping-lists/edit.html", id=id, current_site=session['selected_site'], sites=sites['sites'])

@app.route("/shopping-lists")
def shopping_lists():
    sites = config.sites_config()
    return render_template("shopping-lists/index.html", current_site=session['selected_site'], sites=sites['sites'])

@app.route("/groups")
def groups():
    sites = config.sites_config()
    return render_template("groups/index.html", current_site=session['selected_site'], sites=sites['sites'])

@app.route("/items")
def items():
    sites = config.sites_config()
    return render_template("items/index.html", current_site=session['selected_site'], sites=sites['sites'])

@app.route("/")
def home():
    session['selected_site'] = 'main'
    return render_template("items/index.html")

app.run(host="0.0.0.0", port=5002, debug=True)