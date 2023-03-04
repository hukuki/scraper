from abc import ABC, abstractmethod
from time import sleep
import requests, os, json
import urllib.parse

ERROR_WAIT_TIME = 10

class AbstractScraper(ABC):

	def __init__(self, url, page_size, page_path, headers={}, page_range=None):
		self.url = url
		self.page_size = page_size
		self.page_path = page_path
		self.current_page = 1

		self.headers = headers

		self._encoded_url = urllib.parse.quote(self.url, safe='')

		if not os.path.exists(self.page_path):
			os.makedirs(self.page_path)

		if page_range != None:
			self.current_page = page_range[0]
			self.page_count = page_range[1]

	@abstractmethod
	def send_request(self):
		pass

	@abstractmethod
	def get_page_count(self):
		pass

	def print_message(self, message):
		print('[' + self.__class__.__name__  + '] ' + message)

	def on_error(self):
		self.print_message("error at page: " + str(self.current_page))

		res = self.send_request()

		while res == None:
			self.print_message("Retrying... Wait "+str(ERROR_WAIT_TIME)+" seconds")
			sleep(ERROR_WAIT_TIME)

			res = self.send_request()

		return res

	def save_page(self, data):
		self.print_message("at page: " + str(self.current_page))

		page_file = open( self.page_path + "/page-" + str(self.current_page) +
						"-"+self._encoded_url + ".txt", "w")

		json_data = json.dumps(data, ensure_ascii=False)
		page_file.write(json_data)
		
		page_file.close()

	def scrape(self):
		
		if not hasattr(self, 'page_count'): self.page_count = self.get_page_count()

		self.print_message("total page count: " + str(self.page_count))

		while self.current_page < self.page_count:
			res = self.send_request()

			if res == None: res = self.on_error()
			
			self.save_page(res)

			self.current_page += 1

class CommonXScraper(AbstractScraper):
	
	def __init__(self, url, page_path, page_range=None):
		super().__init__(url, 100, page_path, headers = {
			"accept": "application/json, text/javascript, */*; q=0.01",
			"accept-language": "en-US,en;q=0.9,pt;q=0.8,tr;q=0.7,it;q=0.6",
			"cache-control": "no-cache",
			"content-type": "application/json; charset=UTF-8",
			"pragma": "no-cache",
			"sec-ch-ua": "\"Chromium\";v=\"110\", \"Not A(Brand\";v=\"24\", \"Google Chrome\";v=\"110\"",
			"sec-ch-ua-mobile": "?1",
			"sec-ch-ua-platform": "\"Android\"",
			"sec-fetch-dest": "empty",
			"sec-fetch-mode": "cors",
			"sec-fetch-site": "same-origin",
			"x-requested-with": "XMLHttpRequest"
		}, page_range=page_range)

	def send_request(self):
		body = {"data":{"aranan":"***","arananKelime":"***","pageSize": self.page_size, "pageNumber": self.current_page}}

		res = requests.post(self.url, headers=self.headers, data=json.dumps(body))
		
		dct = json.loads(res.content)
		
		if (dct == None) or (dct["data"] == None) or (dct["data"]["data"] == None): return None
        
		return dct["data"]["data"]

	def get_page_count(self):
		body = {"data":{"aranan":"***","arananKelime":"***","pageSize": self.page_size, "pageNumber": 1}}

		res = requests.post(self.url, headers=self.headers, data=json.dumps(body))
		json_data = json.loads(res.content)

		while json_data["data"] == None or json_data["data"]["recordsFiltered"] == None:
			res = requests.post(self.url, headers=self.headers, data=json.dumps(body))
			json_data = json.loads(res.content)

		return json_data["data"]["recordsFiltered"]

class EmsalTuyapScraper(CommonXScraper):
	
	def __init__(self, page_range=None):
		super().__init__('https://emsal.uyap.gov.tr/aramalist', 'emsal-tuyap-pages', page_range=page_range)

class KararAramaYargitayScraper(CommonXScraper):

	def __init__(self, page_range=None):
		super().__init__('https://karararama.yargitay.gov.tr/aramalist', 'karararama-yargitay-pages', page_range=page_range)

class KararAramaDanistayScraper(CommonXScraper):

	def __init__(self, page_range=None):
		super().__init__('https://karararama.danistay.gov.tr/aramalist', 'karararama-danistay-pages', page_range=page_range)