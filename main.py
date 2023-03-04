from scraper import KararAramaDanistayScraper, KararAramaYargitayScraper, EmsalTuyapScraper
from threading import Thread

if __name__ == '__main__':

	yargitay_range = None # e.g. (1, 100)
	danistay_range = None # e.g. (1, 100)
	emsal_turyap_range = None # e.g. (1, 100)
	
	scrapers = [
		KararAramaDanistayScraper(danistay_range), 
		KararAramaYargitayScraper(yargitay_range), 
		EmsalTuyapScraper(emsal_turyap_range)
	]

	threads = [Thread(target=scraper.scrape) for scraper in scrapers]

	for thread in threads:
		thread.start()
