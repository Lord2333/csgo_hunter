import time
from flask import Flask, request, jsonify, render_template
from deta import Deta
import function as Fun

deta = Deta('a04ifk5k_vuieU7mtYmzPpczutxNDXn4RJbpujQsi')  # configure your Deta project
db = deta.Base('Skin_DB')  # access your DB
app = Flask(__name__)


@app.route('/', methods=["POST", "GET"])
def add_skin():
	if request.method == 'POST':
		url = request.form.get('url')
		price = 0
		creat_time = time.time()

		content = Fun.DealUrl(url)
		db.put({
			"url": url,
			"price_on_mark": content['price'],
			"now_price": content['price'],
			"update_time": creat_time,
			"creat_time": creat_time,
			"isSold": 0,
			"name":content['name']
		})
		return render_template('result.html', **content, bq=content['biaoqian'])
	else:
		return render_template('index.html')


if __name__ == '__main__':
	app.run(host='127.0.0.1', port=8848)
