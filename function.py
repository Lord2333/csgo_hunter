import time
from deta import Deta
import requests
import json
import re
from bs4 import BeautifulSoup as bs

Skey = 'Skey'  # 这里填写Server酱的SendKey
Send_url = 'https://sctapi.ftqq.com/' + Skey + '.send'
global deta_key
deta_key = 'deta_key'  # 这里填写deta的ProjectKey


def main_run():
	List = json.loads(Get_list())['data']
	deta = Deta(deta_key)
	db = deta.Base('Skin_DB')
	for row in List:
		skin_url = row['url']
		now_price = GetUrlPrice(skin_url)['price']
		if now_price == row['now_price']:
			continue
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
		Wx_push(Data)


def get_uu(url):
	good_id = re.findall(r'=(.*)', url)[0]
	API = 'https://h5.youpin898.com/api/commodity/Commodity/Detail?Id=' + str(good_id)
	res = requests.get(API).json()
	res = res["Data"]
	data = {
		"name": res['CommodityName'],
		"biaoqian": res['NameTags'][0],
		"muban": "图案模版(paint seed): " + str(res['PaintSeed']),
		"bianhao": "皮肤编号(paint index):" + str(res['PaintIndex']),
		"mosun": res['Abrade'],
		"price": res['Price'],
		"img": 'https://youpin.img898.com/' + res['Images'].split(',')[0]
	}
	return data


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
	good_id = re.findall(r'trade/(.*)\?', url)[0]
	API = 'https://www.igxe.cn/app-h5/data/730/' + good_id + '?type=1'
	res = requests.get(API).json()['data']
	biaoqian = res['fraudwarnings']
	if biaoqian:
		biaoqian = biaoqian[0]
	else:
		biaoqian = None
	data = {
		"name": res['market_name'],
		"biaoqian": biaoqian,
		"muban": "图案模版(paint seed): " + str(res['paint_seed']),
		"bianhao": "皮肤编号(paint index):" + str(res['paint_index']),
		"mosun": res['wear'],
		"price": res['unit_price'],
		"img": res['inspect_img_large']
	}
	return data


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
		if bian > 0:
			Info = '饰品:' + content['name'] + ' ' + sold + '\n\n平台：' + content[
				'market'] + '\n\n比收藏时跌了{:.2f}元。\n\n火速购买，不要让等待成为遗憾！\n\n直达链接：[8F]('.format(bian) + content['url'] + ')'
			requests.post(Send_url, {
				'title': '王守義拾叁香饰品监控',
				'desp': Info
			})
		elif bian < 0:
			Info = '饰品:' + content['name'] + ' ' + sold + '\n\n平台：' + content[
				'market'] + '\n\n比收藏时涨了{:.2f}元。\n\n饰品有分享，请谨慎购买！'.format(bian)
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


if __name__ == '__main__':
	url = 'https://www.igxe.cn/share/trade/254436254?app_id=730'
	print(get_ig(url))
