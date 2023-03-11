from scrapers.abstract_scaper import AbstractScraper
import requests
from bs4 import BeautifulSoup
from pathlib import Path


class UyusmazlikScaper(AbstractScraper):
    def __init__(self, output_path):
        super().__init__("https://kararlar.uyusmazlik.gov.tr/", 1, output_path)

        Path(output_path).mkdir(parents=True, exist_ok=True)

        
    def get_next_page(self):
        """A generator of pages, returning the soup object of the next page."""        

        search_url = "Arama/_Grid?ExcludeGerekce=False&OrderCol=KararSayisi&OrderAsc=False&WordsOnly=False&page="

        while self.current_page_count <= self.max_page_count:
            page = requests.get(self.base_url + search_url + str(self.current_page_count), verify=False)
            soup = BeautifulSoup(page.content, 'html.parser')
            yield soup
            self.current_page_count += 1

    def get_max_page_count(self):
        page = requests.get(self.base_url, verify=False)
        soup = BeautifulSoup(page.content, 'html.parser')
        input_tag = soup.find('input', {'class': 'pageInput'})
        return input_tag.get('data-max')
    
    def parse_doc_name(self, single_doc):
        """Accepts a single document (a dictionary) and returns the name of the document."""
        return (single_doc["karar_sayisi"] + "_" + single_doc["esas_sayisi"]).replace("/", "-")
    
    def parse_page(self, page):
        """Accepts the return value of get_next_page function (BeautifulSoup object). Parses it into the metadata and 
        document urls.
        
        Note: href is a must have field. If it is not present, the document will be skipped."""
        results = []

        docs = page.findAll("div", {"data-content": True})
        i = 0

        while i < len(docs):
            single_doc = {}
            single_doc["data_content"] = docs[i]['data-content'].strip()
            single_doc["href"] = docs[i].find('a')['href']
            single_doc["karar_sayisi"] = docs[i].find('a').string

            i += 1
            single_doc["esas_sayisi"] = docs[i].find('a').string

            i += 1
            single_doc["bolum"] = docs[i].find('a').string

            i += 1
            single_doc["uyusmazlik"] = docs[i].find('a').string

            i+= 1
            single_doc["karar_sonucu"] = docs[i].find('a').string

            i+= 1
            results.append(single_doc)
        return results
    

#what is a page?
#Page is the html object, extracted from pagination.

#what is a doc?
#Doc is a python dictionary contraining any possible metadata, url of the document and content of the document.              
