from flask import Flask, render_template
import api
app = Flask(__name__)

app.register_blueprint(api.database_api)

@app.route("/workshop")
def workshop():
    return render_template("workshop.html")

@app.route("/")
def home():
    return render_template("home.html")

app.run(host="0.0.0.0", port=5002, debug=True)