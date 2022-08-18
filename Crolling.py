from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
import pymysql
import pandas as pd
from bs4 import BeautifulSoup
import warnings # 경고창 무시
warnings.filterwarnings('ignore')
class Crolling:
	def __init__(self):
		self.conn = pymysql.connect(user    = 'stocks',
									passwd  = '',
									host    = "",
									port    =  3306,
									db      = 'Data',
									charset = 'utf8')

		self.cur = self.conn.cursor()

		self.driver = webdriver.Chrome(ChromeDriverManager().install())
		self.driver.implicitly_wait(3)
		self.driver.maximize_window()
	def Stock_ID(self):
		for i in range(1, 21):
			url = f'https://finance.naver.com/sise/entryJongmok.naver?&page={i}'
			self.driver.get(url)
			self.driver.implicitly_wait(5)
			html = self.driver.page_source 
			soup = BeautifulSoup(html, 'html.parser')
			for j in range(3, 13):
				id = [i['href'].split("=")[1] for i in soup.select(f'body > div > table.type_1 > tbody > tr:nth-child({j}) > td.ctg > a')]
				name = [i.text for i in soup.select(f'body > div > table.type_1 > tbody > tr:nth-child({j}) > td.ctg > a')]
				sql = (id, name)
				self.cur.execute('INSERT IGNORE INTO Stock_ID (id, name) VALUES (%s ,%s)', sql)
				self.conn.commit()
			print(f'{i}/20 페이지 완료')
		self.driver.quit()
	
	def Stock_Price(self):
		self.cur.execute('SELECT id FROM Stock_ID;')
		stock_id = self.cur.fetchall()
		for id in stock_id:
			for i in range(1, 21):
				url = f'https://finance.naver.com/item/sise_day.naver?code={id[0]}&page={i}'
				self.driver.get(url)
				self.driver.implicitly_wait(5)
				html = self.driver.page_source 
				soup = BeautifulSoup(html, 'html.parser')
				for j in [3,4,5,6,7,11,12,13,14,15]:
					date = soup.select_one(f'body > table.type2 > tbody > tr:nth-child({j}) > td:nth-child(1) > span').text
					closing_price = soup.select_one(f'body > table.type2 > tbody > tr:nth-child({j}) > td:nth-child(2) > span').text.replace(',','')
					market_price = soup.select_one(f'body > table.type2 > tbody > tr:nth-child({j}) > td:nth-child(4) > span').text.replace(',','')
					high_price = soup.select_one(f'body > table.type2 > tbody > tr:nth-child({j}) > td:nth-child(5) > span').text.replace(',','')
					low_price = soup.select_one(f'body > table.type2 > tbody > tr:nth-child({j}) > td:nth-child(6) > span').text.replace(',','')
					sql = (id[0], date, closing_price, market_price, high_price, low_price)
					self.cur.execute('INSERT IGNORE INTO Stock_Price (stock_id , date, closing_price, market_price, high_price, low_price) VALUES (%s ,%s ,%s ,%s ,%s ,%s)', sql)
					self.conn.commit()
					break	
				else:
					continue				
				if date == '2022.04.01':
					break
		self.conn.close()
		self.driver.quit()
	def News(self):
		self.cur.execute('SELECT id FROM Stock_ID;')
		stock_id = self.cur.fetchall()
		for idx,id in enumerate(stock_id):
			for i in range(1, 500):
				url = f'https://finance.naver.com/item/news_news.naver?code={id[0]}&page={i}&sm=entity_id.basic&clusterId='
				self.driver.get(url)
				self.driver.implicitly_wait(5)
				html = self.driver.page_source 
				soup = BeautifulSoup(html, 'html.parser')
				date = [i.text for i in self.driver.find_elements_by_class_name("date")]
				for j in soup.select('body > div > table.type5 > tbody'):
					data = j.find_all("a")
					data = [i["href"] for i in data if i["href"] != "#"]
					for da,de in zip(data,date):
						if de == '':
							continue
						if de < '2022.04.01':
							break
						try:
							url = "https://finance.naver.com"+da
							self.driver.get(url)
							sql = (id[0], self.driver.find_element_by_id('news_read').text, de)
							self.cur.execute('INSERT IGNORE INTO Stock_News_2 (stock_id, text, date) VALUES (%s ,%s, %s)', sql)
							self.conn.commit()
						except:
							continue
				if de == '':
					continue
				if de < '2022.04.01':
					break
			print(f'{idx+1}/{len(stock_id)}')
		self.conn.close()
		self.driver.quit()


Crolling().Stock_Price()