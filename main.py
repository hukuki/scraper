from scraper import KararAramaDanistayScraper, KararAramaYargitayScraper, EmsalTuyapScraper
from threading import Thread

if __name__ == '__main__':
    scrapers = [
				KararAramaDanistayScraper(), 
				KararAramaYargitayScraper(), 
				EmsalTuyapScraper()
				]
    threads = [Thread(target=scraper.scrape) for scraper in scrapers]

    for thread in threads:
        thread.start()
