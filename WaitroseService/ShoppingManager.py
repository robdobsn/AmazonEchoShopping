# Online shopping site handling

__author__ = 'robdobsn'

from WaitroseManager import WaitroseManager
from AccountCoding import AccountCoding
import json
import time
import logging

class ShoppingManager():

    def __init__(self):
        self.shopAccounts = {}
        self.secsBetweenTrolleyRefreshes = 600

    def getTrolleyInfo(self, accountUniq):
        # Create account if not already present info
        if not (accountUniq in self.shopAccounts):
            storeName = AccountCoding.getStoreName(accountUniq)
            if storeName == "Waitrose":
                userandpw = AccountCoding.getUserNameAndPw(accountUniq)
                if userandpw is not None:
                    newAccount = WaitroseManager(userandpw["username"], userandpw["password"])
                self.shopAccounts[accountUniq] = newAccount
        logging.info("About to get trolley info")
        trolleyInfo = self.shopAccounts[accountUniq].getTrolleyInfo()
        if not ("timestamp" in trolleyInfo) or \
                (time.time() - trolleyInfo["timestamp"] > self.secsBetweenTrolleyRefreshes):
            logging.info("Requesting trolley info update")
            self.shopAccounts[accountUniq].requestTrolleyInfo()
        logging.info("Returning trolley info")
        return json.dumps(trolleyInfo)
