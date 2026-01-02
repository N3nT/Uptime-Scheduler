from flask import Flask
import json
app = Flask(__name__)


@app.route("/")
def results():
    with open("../data.json", "r", encoding="utf-8") as data:
        return json.load(data)
