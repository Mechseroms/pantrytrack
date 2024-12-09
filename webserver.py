from flask import Flask, render_template, session, request
import api, config, external_devices
app = Flask(__name__)
app.secret_key = '11gs22h2h1a4h6ah8e413a45'
app.register_blueprint(api.database_api)
app.register_blueprint(external_devices.external_api)


@app.route("/group/<id>")
def group(id):
    sites = config.sites_config()
    return render_template("groups/group.html", id=id, current_site=session['selected_site'], sites=sites['sites'])

@app.route("/transactions/<id>")
def transactions(id):
    sites = config.sites_config()
    return render_template("items/transactions.html", id=id, current_site=session['selected_site'], sites=sites['sites'])


@app.route("/item/<id>")
def item(id):
    sites = config.sites_config()
    return render_template("items/item.html", id=id, current_site=session['selected_site'], sites=sites['sites'])

@app.route("/itemlink/<id>")
def itemLink(id):
    sites = config.sites_config()
    return render_template("items/itemlink.html", current_site=session['selected_site'], sites=sites['sites'], proto={'referrer': request.referrer}, id=id)

@app.route("/transaction")
def transaction():
    print(request.referrer)
    sites = config.sites_config()
    return render_template("transaction.html", current_site=session['selected_site'], sites=sites['sites'], proto={'referrer': request.referrer})

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

@app.route("/receipt/<id>")
def receipt(id):
    sites = config.sites_config()
    return render_template("receipts/receipt.html", id=id, current_site=session['selected_site'], sites=sites['sites'])


@app.route("/receipts")
def receipts():
    sites = config.sites_config()
    return render_template("receipts/index.html", current_site=session['selected_site'], sites=sites['sites'])


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
    sites = config.sites_config()
    return render_template("items/index.html", current_site=session['selected_site'], sites=sites['sites'])

app.run(host="0.0.0.0", port=5810, debug=True)