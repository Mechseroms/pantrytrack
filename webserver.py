from flask import Flask, render_template
import api
app = Flask(__name__)

app.register_blueprint(api.database_api)


@app.route("/")
def home():
    return render_template("home.html")

app.run(host="127.0.0.1", debug=True)