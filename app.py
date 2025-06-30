from flask import Flask, render_template
from connection_mongo import get_mongo_connection

app = Flask(__name__)

@app.route("/")
def index():
    db = get_mongo_connection()
    catequizados = list(db["catequizados"].find())
    return render_template("index.html", catequizados=catequizados)
