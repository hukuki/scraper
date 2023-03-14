from abc import ABC, abstractmethod
from time import sleep
import grequests
import requests, os, json
import urllib.parse
import random
from pathlib import Path
from bs4 import BeautifulSoup

class AbstractAsyncScraper(ABC):
    """
    Abstract class for scraping documents from a website asynchronously. The concrete class must implement the following methods:
    get_max_page_count: returns the maximum number of pages to scrape. It is usually specified samewhere in the website html.
    parse_page: parses the html of a page and returns a list of documents. Each document is a python dictionary with metadata about the document. The 'href' is a must-to-have key.
    parse_doc_name: parses the document and returns a string that will be used as the name of the file.
                    e.g. (doc["karar_sayisi"] + "_" + doc["esas_sayisi"]).replace("/", "-") => 2019-123_2019-45
    get_next_page: returns the next page to scrape. This method is usually implemented by incrementing a counter. Due to possible variation, this method is not implemented in the abstract class.
    parse_url_from_page: parses the URLs to be extracted from the given page.


    Here a few notes:
    -page is the html of a page, returned by the pagination method of the website. For parsing, we use the BeautifulSoup library.
    -dic is a python dictionary with metadata about the document. The 'href' is a must-to-have key.
    -doc_name is the name of the file that will be saved. Due to variation in naming convention (e.g karar sayisi, esas sayisi, etc.), this method is not implemented in the abstract class. The child class must implement this method.
    -content is the text of the document. Don't worry about the different structures and encodings (like .docs and .pdfs). We will handle them in the preprocessing step.
    -The child class can override the request_doc method if the default approach does not work.


    """
    #Constants
    INITIAL_ERROR_WAIT_TIME = 15


    def __init__(self, base_url, starting_page_count, output_dir, headers={}):
        self.base_url = base_url
        self.current_page_count = starting_page_count
        self.consec_up_to_date_docs = 0
        self.output_dir = output_dir
        self.headers = headers
        self.urls_list = []
        self.dict = {}

    @abstractmethod
    def get_max_page_count(self):
        """
        Should return the maximum number of pages to scrape.
        Pages can be different paginations of the website or different sections of the website.
        """
        pass

    @abstractmethod
    def parse_page(self, page):
        """
        Parse page method should extract the URLs from the given page and return a list of dictionaries.
        The dictionary should contain the important metadata information.
        "href" is a must-to-have key.
        """
        pass

    @abstractmethod
    def doc_name(self, doc):
        """
        Returns the name of the file to be stored.
        :param doc: dictionary with metadata about the document. "href" is a must-to-have key in the dictionary.
        """
        pass

    @abstractmethod
    def get_all_pages(self):
        """
        Returns a list of Request objects for all pages to be scraped.
        Requests are not sent but stored to be sent asynchronously later.
        """
        pass

    def add_url(self, url):
        """
        Adds a new URL string to the list of URLs to be requested.
        :param url: URL string
        """
        self.urls_list.append(url)

    def add_to_dict(self, doc):
        """
        Stores the information about the document in a dictionary.
        Keys: URL of the document
        Values: Dictionary with metadata about the document
        """
        self.dict[doc["href"]] = doc

    def on_error(self, url):
        """
        This method is called when an error occurs. It waits for a while and then tries again.
        :param url: URL string that caused the error
        """
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
                if consecutive_errors == 10:
                    break
                sleep_time = (self.INITIAL_ERROR_WAIT_TIME*consecutive_errors) + random.random()*5
                self.print_message("Retrying... Wait "+str(sleep_time)+" seconds")
                sleep(sleep_time)
        log_file_name = url.replace("/", "_") + "_error_log.txt"
        with open(os.path.join(self.output_dir, log_file_name), "w") as f:
            f.write("Error at page: " + url)

    def save_html(self, doc):
        """
        Saves the HTML content as an HTML file in the html folder under the output directory.
        i.e. output file directory is output_dir/html/doc_name.html

        :param doc dictionary with metadata about the document. "html" is a must-to-have key in the dictionary.
        """
        doc_name = self.doc_name(doc)
        html_folder_dir = self.output_dir + "/html"
        Path(html_folder_dir).mkdir(parents=True, exist_ok=True)
        with open(os.path.join(html_folder_dir, doc_name) + ".html", "w") as f:
            f.write(doc["html"])

    def save_json(self, doc):
        """
        Saves the document to the output directory.
        The naming convention is specified by the child class.

        :param doc dictionary with metadata about the document.
        """
        doc_name = self.doc_name(doc)
        json_folder_dir = self.output_dir + "/json"
        Path(json_folder_dir).mkdir(parents=True, exist_ok=True)
        with open(os.path.join(json_folder_dir, doc_name) + ".json", "w") as f:
            json.dump(doc, f)

    def json_file_exists(self, doc):
        """
        Checks if the file with the JSON extension for the given doc exists in the output directory.
        """
        doc_name = self.doc_name(doc)
        return os.path.exists(os.path.join(self.output_dir, doc_name) + ".json")

    def html_file_exists(self, doc):
        """
        Checks if the file with the HTML extension for the given doc exists in the output directory.
        """
        doc_name = self.doc_name(doc)
        return os.path.exists(os.path.join(self.output_dir, doc_name) + ".html")

    def print_message(self, message):
        print('[' + self.__class__.__name__  + '] ' + message)

    def get_next_doc(self):
        """"
        Yields the next document by iterating pages and documents. Here, doc is a python dictionary with metadata about the document.
        The 'href' is a must-to-have key.
        """
        for page in self.get_next_page():
            self.print_message("Current page: " + str(self.current_page_count))
            for doc in self.parse_page(page):
                yield doc

    def get_all_urls(self):
        """
        From the yielded pages, it extracts the URLs to be requested.
        Stores them in self.urls_list.
        To carry the information of the page, the important information is stored in self.dict.
        """
        page_requests = self.get_all_pages()
        page_responses = grequests.map(page_requests, size=10)
        for page_response in page_responses:
            soup = BeautifulSoup(page_response.content, 'html.parser')
            docs = self.parse_page(soup)
            for doc in docs:
                self.add_url(doc["href"])
                self.add_to_dict(doc)

    def scrape(self):
        """
        Scrapes all documents from the base url by iterating through URL requests.
        """
        self.get_all_urls()
        request_list = []
        for url in self.urls_list:
            request = grequests.get(url)
            request_list.append(request)
        response_list = grequests.map(request_list, size=10)
        for response in response_list:
            url = response.url
            doc = self.dict[url]
            doc["html"] = response.text
            self.save_html(self.dict[url])
            self.save_json(self.dict[url])


    def check_if_up_to_date(self):
        return self.consec_up_to_date_docs >= float("inf") #Since we are scraping from scratch, we can set this to infinity. Later, it should be set to a smaller number.
