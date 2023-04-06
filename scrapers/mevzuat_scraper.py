from scrapers.abstract_scaper import AbstractScraper
import requests
import json
from bs4 import BeautifulSoup
from pathlib import Path
from urllib.parse import urlparse, parse_qs

class MevzuatScraper(AbstractScraper):
    def __init__(self, output_path, log_file=None):
        self.body = {"draw":1,"columns":[{"data":None,"name":"","searchable":True,"orderable":False,"search":{"value":"","regex":False}},{"data":None,"name":"","searchable":True,"orderable":False,"search":{"value":"","regex":False}},{"data":None,"name":"","searchable":True,"orderable":False,"search":{"value":"","regex":False}}],"order":[],"start":0,"length":100,"search":{"value":"","regex":False},"parameters":{"AranacakIfade":"Kg==","AranacakYer":"Baslik","TamCumle":False,"MevzuatTur":0,"GenelArama":True}}
        self.headers = {
            "Content-Type": "application/json; charset=UTF-8",
            "Accept": "application/json, text/javascript, */*; q=0.01",
            "Accept-Language": "en-US,en;q=0.9,pt;q=0.8,tr;q=0.7,it;q=0.6",
        }

        super().__init__("https://www.mevzuat.gov.tr/", 1, output_path, headers=self.headers, log_file=log_file)
        Path(output_path).mkdir(parents=True, exist_ok=True)

    def get_next_page(self):
        """A generator of pages, returning the soup object of the next page."""

        search_url = 'anasayfa/MevzuatDatatable'

        while self.current_page_count <= self.max_page_count:
            response = requests.post(self.base_url + search_url,
                                data=json.dumps(self.body),
                                headers=self.headers)
            
            json_data = json.loads(response.text)
            yield json_data

            self.current_page_count += 1
            self.body["draw"] += 1
            self.body["start"] += 100

    def get_max_page_count(self):
        response = requests.post(self.base_url + 'anasayfa/MevzuatDatatable', data=json.dumps(self.body), headers=(self.headers))

        json_data = json.loads(response.text)

        return json_data['recordsTotal'] // 100

    def parse_doc_name(self, single_doc):
        # return single_doc["mevzuatNo"] + "_" + single_doc["kabulTarih"]
        return f'{single_doc["mevzuatTur"]}_{single_doc["mevzuatTertip"]}_{single_doc["mevzuatNo"]}'
    
    def request_doc(self, url):
        """Sends a request to get the document. Note that this approach might not work for all websites. In this case, the child class should override this method."""
        result = requests.get(self.base_url + url)

        if result.status_code == 200:
            if result.headers['Content-Type'] == 'application/msword':
                return result.content
            else:
                self.log(f'Couldn\'t download: {url}')
                print(f'Couldn\'t download: {url}')
                return None
        else:
            return self.on_error(url)

    def parse_page(self, page):
        """
        In http://mevzuat.gov.tr, there are two different href in document metadata.
        One is for plaintext (in html), and others are for binary files (like pdf's).

        * For plaintext, url field in the metadata is the part after the origin, meaning .....gov.tr/"<JUST HERE>". 
        * For binary files, it is the entire url: "http:/mevzuat.gov.tr/a23423.23423.pdf"
        
        http://mevzuat.gov.tr/mevzuat?..... is the url to display a mevzuat,
        but it the webpage itself. 

        To retrieve mevzuat's content ONLY, there is an endpoint 'anasayfa/MevzuatFihristDetayIframe?',
        which we use in this script. This endpoint saves us the trouble of parsing html.
        """

        for item in page["data"]:
            if item["url"].startswith('http'):
                # Binary file
                item["href"] = item["url"]
            else:
                # Plaintext html
                # item["href"] =  "anasayfa/MevzuatFihristDetayIframe?" + item["url"].replace('mevzuat?', '')
                # As doc (MS Word file) :
                parsed_url = urlparse(item["url"])
                parsed_query = parse_qs(parsed_url.query)

                item["href"] = "MevzuatMetin/"+ parsed_query["MevzuatTur"][0] + "." + parsed_query["MevzuatTertip"][0] + "." + parsed_query["MevzuatNo"][0] + ".doc"

            yield item