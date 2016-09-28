# Waitrose online shopping cart handling

__author__ = 'robdobsn'

from WaitroseScraper import WaitroseScraper
import logging
import threading
import time

class WaitroseManager():

    def __init__(self, username, password):
        logging.info("Waitrose manager starting")
        self.favouritesReqd = False
        self.trolleyInfoReqd = False
        self.trolleyInfoLock = threading.Lock()
        self.trolleyInfo = {}
        self.favouritesLock = threading.Lock()
        self.favourites = {}
        self.username = username
        self.password = password
        self.scraperThread = threading.Thread(target=self.scraperThreadFn)
        self.scraperThread.start()

    def scraperThreadFn(self):
        # Create the scraper
        self.waitroseScraper = WaitroseScraper()

        # Stay in here performing operations as requested by external flags
        while True:
            # Information on the current trolley
            if self.trolleyInfoReqd:
                if self.waitroseScraper.ensureLoggedIn(self.username, self.password):
                    basketSummary = self.waitroseScraper.getBasketSummary()
                    trolleyList = []
                    if int(float(basketSummary['numItems'])) > 0:
                        trolleyList = self.waitroseScraper.getTrolleyContents()
                    with self.trolleyInfoLock:
                        self.trolleyInfo = {
                            "items": trolleyList,
                            "numItems": basketSummary["numItems"],
                            "totalPrice": basketSummary["totalPrice"],
                            "timestamp": time.time()
                        }
                        logging.info("Trolley acquired TotalPrice " + str(basketSummary["totalPrice"])\
                                     + " Num Items " + str(basketSummary["numItems"]))
                    self.trolleyInfoReqd = False

            if self.favouritesReqd:
                if self.waitroseScraper.ensureLoggedIn(self.username, self.password):
                    favourites = self.waitroseScraper.getFavourites()
                    with self.favouritesLock:
                        self.favourites = {
                            "items": favourites,
                            "timestamp": time.time()
                        }
                        logging.info("Found " + str(len(favourites)) + " favourites")
                    self.favouritesReqd = False

            # Yield to other threads
            time.sleep(0)

    def requestTrolleyInfo(self):
        self.trolleyInfoReqd = True

    def requestFavourites(self):
        self.favouritesReqd = True

    def getTrolleyInfo(self):
        with self.trolleyInfoLock:
            return self.trolleyInfo

    def getFavourites(self):
        with self.favouritesLock:
            return self.favourites

