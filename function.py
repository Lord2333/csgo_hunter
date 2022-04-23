import time
from deta import Deta
import requests
import json
import re
from bs4 import BeautifulSoup as bs

Skey = 'Skey'
Send_url = 'https://sctapi.ftqq.com/' + Skey + '.send'
global deta_key
deta_key = 'deta_key'


def get_uu(good_id):
	return 1


def get_buff(url):
	res = requests.get(url).text
	soup = bs(res, 'html.parser')
	footer = soup.find('div', class_='good-detail-footer')
	h_6 = footer.find('h6')
	span = h_6.find('span').text
	price = span.split(' ')[1]
	img = soup.find('img', class_='show_inspect_img').get('src')
	info = soup.find('div', class_='title-info-wrapper')
	name = info.find('h3').text
	Ps = info.find_all('p')
	biaoqian = info.find('p', class_='name_tag')
	if biaoqian == None:
		muban = Ps[0].text
		bianhao = Ps[1].text
		mosun = Ps[2].text
	else:
		biaoqian = biaoqian.text
		muban = Ps[1].text
		bianhao = Ps[2].text
		mosun = Ps[3].text
	data = {
		"name": name,
		"muban": muban,
		"bianhao": bianhao,
		"mosun": mosun,
		"price": price,
		"img": img,
		"biaoqian": biaoqian
	}
	return data


def get_ig(url):
	return 1


def Put_data(url, content, deta_key, m):
	deta = Deta(deta_key)
	db = deta.Base('Skin_DB')
	creat_time = time.time()
	Data = {
		"market": m,
		"url": url,
		"price_on_mark": content['price'],
		"now_price": content['price'],
		"update_time": creat_time,
		"creat_time": creat_time,
		"isSold": 0,
		"name": content['name']
	}
	db.put(Data)


def DealUrl(url):
	try:
		site = re.findall(r'\.(.*)\.c', url)[0]
		if site == '163':
			content = get_buff(url)
			Put_data(url, content, deta_key, '8F')
			return content
		elif site == 'igxe':
			content = get_ig(url)
			Put_data(url, content, deta_key, 'IG')
			return content
		elif site == 'youpin898':
			content = get_uu(url)
			Put_data(url, content, deta_key, 'UU')
			return content
		else:
			return None
	except IndexError:
		return None


def Get_list():
	deta = Deta(deta_key)
	db = deta.Base('Skin_DB')
	res = db.fetch()
	all_items = res.items
	resp = {
		"code": 0,
		"data": 0
	}
	while res.last:
		res = db.fetch(last=res.last)
		all_items += res.items
	resp["data"] = all_items
	return json.dumps(obj=resp)


def Wx_push(content):
	if not content['isSold']:
		sold = '在售'
		bian = float(content['price_on_mark']) - float(content['now_price'])
		if bian < 0:
			Info = '饰品:' + content['name'] + ' ' + sold+'\n平台：' + content['market'] + '\n比收藏时跌了{:.2f}元。\n火速购买，不要让等待成为遗憾！\n直达链接：[8F]('.format(-bian) + content['url'] + ')'
			requests.post(Send_url, {
				'title': '王守義拾叁香饰品监控',
				'desp': Info
			})
		elif bian > 0:
			Info = '饰品:' + content['name'] + ' ' + sold+'\n平台：' + content['market'] + '\n比收藏时涨了{:.2f}元。\n疑似倒狗入场提价，请谨慎购买！'.format(bian)
			requests.post(Send_url, {
				'title': '王守義拾叁香饰品监控',
				'desp': Info
			})
	else:
		sold = '已出售或下架'
		Info = '饰品:' + content['name'] + ' ' + sold
		requests.post(Send_url, {
			'title': '王守義拾叁香饰品监控',
			'desp': Info
		})
	print('已处理')


def GetUrlPrice(url):
	try:
		site = re.findall(r'\.(.*)\.c', url)[0]
		if site == '163':
			content = get_buff(url)
			return content
		elif site == 'igxe':
			content = get_ig(url)
			return content
		elif site == 'youpin898':
			content = get_uu(url)
			return content
		else:
			return None
	except IndexError:
		return None


# @app.lib.cron()
# def cron_task(event):
# 	deta = Deta(deta_key)
# 	db = deta.Base('Skin_DB')
# 	List = Get_list()['data']
# 	url_list = []
# 	for row in List:
# 		url_list.append([row['key'], row['price_on_mark'], row['now_price'], row['url']])
# 	for item in url_list:
# 		Data = GetUrlPrice(item['url'])
# 		if not Data['isSold']:
# 			now_price = Data['price']


if __name__ == '__main__':
	List = json.loads(Get_list())['data']
	deta = Deta(deta_key)
	db = deta.Base('Skin_DB')
	for row in List:
		skin_url = row['url']
		now_price = GetUrlPrice(skin_url)['price']
		up_time = time.time()
		Data = {
			"market": row['market'],
			"url": skin_url,
			"price_on_mark": row['price_on_mark'],
			"now_price": now_price,
			"update_time": up_time,
			"creat_time": row['creat_time'],
			"isSold": 0,
			"name": row['name']
		}
		db.put(Data, key=row['key'])
	List = json.loads(Get_list())['data']
	for content in List:
		Wx_push(content)
