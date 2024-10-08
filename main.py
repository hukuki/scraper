from scraper import KararAramaDanistayScraper, KararAramaYargitayScraper, EmsalTuyapScraper
from scrapers.mevzuat_scraper import MevzuatScraper
from scrapers.uyusmazlik_scraper import UyusmazlikScaper
from threading import Thread
from util import partition

if __name__ == '__main__':
	# num_thread_for_each = 10
	
	# # Get ranges for each thread to scrape
	# yargitay_range = partition(44203, 58937, num_thread_for_each)
	# danistay_range = partition(913, 1217, num_thread_for_each)
	# emsal_tuyap_range = partition(2518, 3357, num_thread_for_each)
	
	# scrapers = [
	# 	*[KararAramaDanistayScraper(r) for r in danistay_range], 
	# 	*[KararAramaYargitayScraper(r) for r in yargitay_range], 
	# 	#*[EmsalTuyapScraper(r) for emsal_tuyap_range in emsal_tuyap_range]
	# ]

	# threads = [Thread(target=scraper.scrape) for scraper in scrapers]

	# for thread in threads:
	# 	thread.start()
	
	scraper = MevzuatScraper("output/mevzuat", log_file="output/mevzuat.log")
	#scraper = UyusmazlikScaper("output/uyusmazlik")
	scraper.scrape()