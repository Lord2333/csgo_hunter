import time
from flask import Flask, request, render_template
import function as Fun

app = Flask(__name__)


@app.route('/', methods=["POST", "GET"])
def add_skin():
	if request.method == 'POST':
		if request.form:
			url = request.form.get('url')
			price = 0
			creat_time = time.time()

			content = Fun.DealUrl(url)
			if content:
				return render_template('result.html', **content, bq=content['biaoqian'])
			else:
				return '<h1>分享链接错误！</h1>'
		else:
			return render_template('list.html')
	else:
		return render_template('index.html')

@app.route('/watch', methods=["GET"])
def wacth_skin():
	return Fun.Get_list()

if __name__ == '__main__':
	app.run(host='127.0.0.1', port=8848)
