import time
from flask import Flask, request, jsonify
from deta import Deta


deta = Deta('a04ifk5k_vuieU7mtYmzPpczutxNDXn4RJbpujQsi') # configure your Deta project
db = deta.Base('Skin_DB')  # access your DB
app = Flask(__name__)


@app.route('/', methods=["POST", "GET"])
def add_skin():
    if request.method == 'POST':
        url = request.json.get("url")
        price = 0
        creat_time = time.time()
        update_time = 0

        user = db.put({
            "url": url,
            "price": price,
            "update_time": update_time,
            "creat_time": creat_time,
        })
        return jsonify(user, 201)