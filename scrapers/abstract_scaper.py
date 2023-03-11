from abc import ABC, abstractmethod
from time import sleep
import requests, os, json
import urllib.parse
import random

class AbstractScraper(ABC):
    """Abstract class for scraping documents from a website. The child class must implement the following methods:
    get_max_page_count: returns the maximum number of pages to scrape. It is usually specified samewhere in the website html.
    parse_page: parses the html of a page and returns a list of documents. Each document is a python dictionary with metadata about the document. The 'href' is a must-to-have key.
    parse_doc_name: parses the document and returns a string that will be used as the name of the file. 
                    e.g. (doc["karar_sayisi"] + "_" + doc["esas_sayisi"]).replace("/", "-") => 2019-123_2019-45
    get_next_page: returns the next page to scrape. This method is usually implemented by incrementing a counter. Due to possible variation, this method is not implemented in the abstract class.
    
    Here a few notes:
    -page is the html of a page, returned by the pagination method of the website. For parsing, we use the BeautifulSoup library.
    -doc is a python dictionary with metadata about the document. The 'href' is a must-to-have key.
    -doc_name is the name of the file that will be saved. Due to variation in naming convention (e.g karar sayisi, esas sayisi, etc.), this method is not implemented in the abstract class. The child class must implement this method.
    -content is the text of the document. Don't worry about the different structures and encodings (like .docs and .pdfs). We will handle them in the preprocessing step.
    -The child class can override the request_doc method if the default approach does not work.
    
    
    """
    #Constants
    INITIAL_ERROR_WAIT_TIME = 15


    def __init__(self, base_url, starting_page_count, output_dir, headers={}):
        self.base_url = base_url
        self.max_page_count = int(self.get_max_page_count())
        self.current_page_count = starting_page_count
        self.consec_up_to_date_docs = 0
        self.output_dir = output_dir

    @abstractmethod
    def get_max_page_count(self):
        pass
    
    @abstractmethod
    def parse_page(self, page):
        pass

    @abstractmethod
    def parse_doc_name(self, doc):
        pass

    @abstractmethod
    def get_next_page(self):
        pass

    def on_error(self, url):
        """This method is called when an error occurs. It waits for a while and then tries again."""
        self.print_message("error at page: " + str(self.current_page_count))
        sleep_time = self.INITIAL_ERROR_WAIT_TIME + random.random()*5
        self.print_message("Retrying... Wait "+str(sleep_time)+" seconds")
        sleep(sleep_time)

        consecutive_errors = 1

        while True:
            result = requests.get(self.base_url + url, verify=False)
            if result.status_code == 200:
                return result.text
            else:
                consecutive_errors += 1
                sleep_time = (self.INITIAL_ERROR_WAIT_TIME*consecutive_errors) + random.random()*5
                self.print_message("Retrying... Wait "+str(sleep_time)+" seconds")
                sleep(sleep_time)
    
    def save_doc(self, doc):
        """Saves the document to the output directory. The naming convention is specified by the child class."""
        doc_name = self.parse_doc_name(doc)
        with open(os.path.join(self.output_dir, doc_name) + ".json", "w") as f:
            json.dump(doc, f)

    def request_doc(self, url):
        """Sends a request to get the document. Note that this approach might not work for all websites. In this case, the child class should override this method."""
        result = requests.get(self.base_url + url, verify=False)

        if result.status_code == 200:
            return result.text
        else:
            return self.on_error(url)

    def check_if_doc_exists(self, doc):
        """Since we parse_doc_name is an abstract method, we can exactly know how the file is named. This function checks if the file exists."""
        doc_name = self.parse_doc_name(doc)
        return os.path.exists(os.path.join(self.output_dir, doc_name) + ".json")

    def print_message(self, message):
        print('[' + self.__class__.__name__  + '] ' + message)

    def get_next_doc(self):
        """"Yields the next document by iterating pages and documents. Here, doc is a python dictionary with metadata about the document. The 'href' is a must-to-have key."""
        for page in self.get_next_page():
            self.print_message("Current page: " + str(self.current_page_count))
            for doc in self.parse_page(page):
                yield doc

    def scrape(self):
        """Scrapes all documents from the base url by iterating through docs. """
        for doc in self.get_next_doc():
            if not self.check_if_doc_exists(doc) and "href" in doc:
                content = self.request_doc(doc["href"])
                doc["content"] = content
                self.save_doc(doc)
                self.consec_up_to_date_docs = 0
            else:
                print("doc exists", self.parse_doc_name(doc))
                print("skipping")
            
                self.consec_up_to_date_docs += 1
                
                if self.check_if_up_to_date():
                    self.print_message("Up to date")
                    break

    def check_if_up_to_date(self):
        return self.consec_up_to_date_docs >= float("inf") #Since we are scraping from scratch, we can set this to infinity. Later, it should be set to a smaller number.
