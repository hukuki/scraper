from scapers.abstract_scaper import AbstractScraper

class Master(): 
    """ Master class to start and control fetching of URLs. 
        Supports IP rotating if a list of IP proxies is given
        :param ip_proxies: List of proxy IPs for IP rotating
        :param fetcherrs: List of Fetcher objects
    """
    def __init__(self, ip_proxies=None, fetchers=None, *args, **kwargs):

        self.ip_proxies = ip_proxies or []
        self.fetchers = fetchers or []

    def add_fetcher(self, fetchers, *args, **kwargs):
        """
            Adding new fetchers to master fetcher
            :param fetcher: An object or a list of objects to add to the fetchers list
        """
        if (type(fetchers) == list):
            for fetcher in fetchers:
                if not isinstance(fetcher, AbstractScraper):
                    raise ValueError("Added fetchers should be of type AbstractFetcher.")
                else:
                    self.fetchers.append(fetcher)
        elif isinstance(fetchers, AbstractScraper):
            self.fetchers.append(fetcher)
        else:
            raise ValueError("Unrecognized value type for fetchers")
    
    def add_proxy(self, proxies, *args, **kwargs):
        """
            Adding new proxy IPs for IP rotating
            :param proxies: Single 
        """

    
