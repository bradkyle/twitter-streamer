import os
from flask import Flask, Response
from pymongo import MongoClient
from bson.json_util import dumps

app = Flask(__name__)

client = MongoClient("mongodb://mongo:27017")
db = client.twitterdb


@app.route('/')
def api():

    cursor = db.twitter_search.find()
    resp = Response(dumps(cursor, indent=4, sort_keys=True), status=200, mimetype='application/json')
    return resp


if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)