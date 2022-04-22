import requests
import json
import re
from bs4 import BeautifulSoup as bs


def get_uu(good_id):
	UU_header = {
		'content-type': 'application/json;charset=UTF-8',
		'origin': 'https://www.youpin898.com',
		'referer': 'https://www.youpin898.com/goodInfo?id=' + good_id,
		'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.82 Safari/537.36',
	}
	API = 'https://api.youpin898.com/api/homepage/es/commodity/GetCsGoPagedList'
	data = {
		"templateId": good_id,
		"pageSize": 30,
		"pageIndex": 1,
		"sortType": 0,
		"listSortType": 4,
		"listType": 30
	}
	res = requests.post(API, json=data, headers=UU_header).text
	res_json = json.loads(res)
	List_0 = res_json['Data']['CommodityList'][0]
	name = List_0['CommodityName']
	mosun = List_0['Abrade']
	yajin = List_0['LeaseDeposit']
	maxday = List_0['LeaseMaxDays']
	duan = List_0['LeaseUnitPrice']
	chang = List_0['LongLeaseUnitPrice']
	dataset = {
		'Market': 'YYYP',
		'Good': name,
		'Mosun': mosun,
		'Yajin': yajin,
		'Maxday': maxday,
		'Duanzu': duan,
		'Changzu': chang
	}
	return dataset


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
		'name': name,
		'muban': muban,
		'bianhao': bianhao,
		'mosun': mosun,
		'price': price,
		'img': img,
		'biaoqian': biaoqian
	}
	return data


def get_ig(url):
	print(url)


def DealUrl(url):
	site = re.findall(r'\.(.*)\.c', url)[0]
	if site == '163':
		return get_buff(url)
	elif site == 'igxe':
		return get_ig(url)
	elif site == 'youpin898':
		return get_uu(url)
	else:
		return '<h1>无法找到该饰品</h1>'


if __name__ == '__main__':
	url1 = 'https://buff.163.com/market/m/item_detail?classid=4428828851&instanceid=188530139&game=csgo&assetid=25440222281&sell_order_id=220422T1799485665'
	url2 = 'https://h5.youpin898.com/goodsInfo.html?id=4956638'  # 已出售
	url2_2 = 'https://h5.youpin898.com/goodsInfo.html?id=4747732'  # 未出售
	url3 = 'https://www.igxe.cn/share/trade/254436254?app_id=730'
	DealUrl(url1)
# DealUrl(url2)
# DealUrl(url3)
