# Waitrose web scraper

__author__ = 'robdobsn'

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import selenium.webdriver.support.ui as webdriverui
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, WebDriverException, TimeoutException
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import logging
import json
import re

class WaitroseScraper():

    def __init__(self):
        logging.info("Waitrose scraper starting")
        self.isInitalized = False
        self.isLoggedIn = False

    # Start the web driver (runs the browser)
    def startWebDriver(self):

        # Clear current session file info
        with open('browserSession.json', 'w') as outfile:
            json.dump({}, outfile)

        # Create WebDriver
        try:
            self.webDriver = webdriver.Firefox()
        except WebDriverException:
            logging.error("startWebDriver() Failed to start")
            return False

        # Save session info
        url = self.webDriver.command_executor._url
        session_id = self.webDriver.session_id
        with open('browserSession.json', 'w') as outfile:
            json.dump({"url": url, "session_id": session_id}, outfile)

        return True

    def websiteLogin(self, username, password):
        try:
            elemLoginBtn = self.webDriver.find_element_by_id('headerSignInRegister')
            elemLoginBtn.click()

            try:
                elemLoginId = self.webDriver.find_element_by_id('logon-email')
                elemLoginId.send_keys(username + Keys.RETURN)

                try:
                    webdriverui.WebDriverWait(self.webDriver, 10)\
                            .until(EC.visibility_of_element_located((By.ID, "logon-password")))

                    try:
                        elemLoginId = self.webDriver.find_element_by_id('logon-password')
                        elemLoginId.send_keys(password + Keys.RETURN)
                        webdriverui.WebDriverWait(self.webDriver, 20)\
                            .until(EC.visibility_of_element_located((By.CLASS_NAME, "trolley-total")))
                        elem2 = self.webDriver.find_element_by_class_name('trolley-total')
                        if elem2:
                            logging.info("waitroseLogin() Basket found")
                        else:
                            logging.info("waitroseLogin() basket not found")

                        return True

                    except NoSuchElementException:
                        logging.error("waitroseLogin() Cannot find Continue button")

                except NoSuchElementException:
                    logging.error("waitroseLogin() Cannot find Continue button")

            except NoSuchElementException:
                logging.error("waitroseLogin() Cannot find logon-email field")

        except NoSuchElementException:
            logging.error("waitroseLogin() Cannot find sign-in-register button")

        return False

    def getBasketSummary(self):

        basketSummary = {}

        # Ensure we wait until the trolley-total is visible
        try:
            webdriverui.WebDriverWait(self.webDriver, 20)\
                .until(EC.visibility_of_element_located((By.CLASS_NAME, "trolley-total")))
        except TimeoutException:
            logging.error("Get basket summary timeout exception")
            return None
        except WebDriverException:
            logging.error("Get basket summary webdriver element exception")
            return None

        # Get basket total price
        try:
            totalElem = self.webDriver.find_element_by_class_name('trolley-total')
            if totalElem:
                reTotalElem = re.search("([0-9]{1,4}\.[0-9]{2})", totalElem.text)
                if reTotalElem:
                    basketSummary["totalPrice"] = reTotalElem.group(1)
                    logging.info("waitrose: Basket: total=£" + str(basketSummary["totalPrice"]))

            # Get number of basket items
            summaryElem = self.webDriver.find_element_by_class_name('trolley-summary')
            if summaryElem:
                reSummaryElem = re.search("([0-9]{1,4}) items", summaryElem.text)
                if reSummaryElem:
                    basketSummary["numItems"] = reSummaryElem.group(1)
                    logging.info("waitrose: Basket: num items=" + str(basketSummary["numItems"]))
        except WebDriverException:
            logging.error("waitrose: Get basket summary webdriver element exception")
            return None

        # Return info found
        return basketSummary

    def getElemAttrIfPresent(self, soup, elemName, className, subElem, attrName, regexReplace, destDict=None, dictName=None):
        rslt = ""
        try:
            el = soup.find(elemName, class_=className)
            if subElem is not "":
                el = el.find(subElem)
            if attrName == "text":
                rslt = el.get_text()
            else:
                rslt = el[attrName]
            if regexReplace is not "":
                rslt = re.sub(regexReplace, "", rslt)
            if destDict is not None:
                destDict[dictName] = rslt
        except:
            logging.error("waitrose: Error extracting element " + elemName + " " + className)
        return rslt

    def getShoppingItems(self, isTrolleyPage):

        # Make sure all items on the page are loaded - lazy loader
        try:
            webdriverui.WebDriverWait(self.webDriver, 10)\
                .until(EC.visibility_of_element_located((By.CLASS_NAME, "m-product")))
        except WebDriverException:
            logging.error("Wait for m-product webdriver element exception")
            return False
        
        productsFound = self.webDriver.find_elements_by_class_name("m-product")
        print("waitrose: Lazy loading products - currently " + str(len(productsFound)) + " found")
        numRepeats = 0
        if len(productsFound) > 10:
            while True:
                prevFound = len(productsFound)
                self.webDriver.execute_script("window.scrollBy(0,window.innerHeight)")
                productsFound = self.webDriver.find_elements_by_class_name("m-product")
                print("Loading products - currently " + str(len(productsFound)) + " found")
                if len(productsFound) <= prevFound:
                    numRepeats += 1
                    if numRepeats > 20:
                        break
                else:
                    numRepeats = 0

        print("Done lazy loading products " + str(len(productsFound)) + " found")

        # Go through items in the list on the current page
        shoppingItems = []
        for product in productsFound:

            # Get HTML for this product
            basketIt = {}
            el = product.get_attribute("innerHTML")
            productSoup = BeautifulSoup(el, "html.parser")

            # Extract some common details
            self.getElemAttrIfPresent(productSoup, "a", "m-product-open-details", "", "href", "", basketIt, "detailsHref")
            self.getElemAttrIfPresent(productSoup, "a", "m-product-open-details", "img", "src", "", basketIt, "imageSrc")
            self.getElemAttrIfPresent(productSoup, "div", "m-product-volume", "", "text", r"\W", basketIt, "productVolume")

            # Check if we are doing the trolley page - which has extra info like number of items ordered
            if isTrolleyPage:
                self.getElemAttrIfPresent(productSoup, "div", "m-product-title", "a", "text", "", basketIt, "productTitle")
                if not "productTitle" in basketIt or basketIt["productTitle"] == "":
                    self.getElemAttrIfPresent(productSoup, "a", "m-product-open-details", "img", "title", "", basketIt,
                                         "productTitle")
                self.getElemAttrIfPresent(productSoup, "div", "quantity-append", "input", "value", "", basketIt,
                                     "trolleyQuantity")
                self.getElemAttrIfPresent(productSoup, "p", "m-product-details", "span", "text", "", basketIt,
                                     "trolleyPrice")
                self.getElemAttrIfPresent(productSoup, "div", "m-product-details-container", "div", "data-price", "",
                                     basketIt,
                                     "price")
                self.getElemAttrIfPresent(productSoup, "div", "m-product-details-container", "div", "data-priceperkg",
                                     "", basketIt, "pricePerKg")
                self.getElemAttrIfPresent(productSoup, "div", "m-product-details-container", "div", "data-orderitemid",
                                     "", basketIt, "orderItemId")
                self.getElemAttrIfPresent(productSoup, "div", "m-product-details-container", "div", "data-producttype",
                                     "", basketIt, "productType")
                self.getElemAttrIfPresent(productSoup, "div", "m-product-details-container", "div", "data-productid",
                                     "", basketIt, "productId")
                self.getElemAttrIfPresent(productSoup, "div", "m-product-details-container", "div", "data-uom", "", basketIt,
                                     "UOM")
                self.getElemAttrIfPresent(productSoup, "div", "m-product-details-container", "div", "data-weighttype",
                                     "", basketIt, "weightType")
                self.getElemAttrIfPresent(productSoup, "div", "m-product-details-container", "div", "data-substitute",
                                     "", basketIt, "substitute")
            else:
                self.getElemAttrIfPresent(productSoup, "div", "m-product-price-container", "span", "text", "\W", basketIt,
                                     "price")
                self.getElemAttrIfPresent(productSoup, "a", "m-product-open-details", "", "text", "", basketIt,
                                     "productTitle")
                if not "productTitle" in basketIt or basketIt["productTitle"] == "":
                    self.getElemAttrIfPresent(productSoup, "a", "m-product-open-details", "img", "title", "", basketIt,
                                         "productTitle")

            # Check if the product at least has a title and only add to list if it does
            if not "productTitle" in basketIt or basketIt["productTitle"] == "":
                logging.error("Extract Shopping List: Failed to extract product name")
            else:
                shoppingItems.append(basketIt)

        return shoppingItems

    def getTrolleyContents(self):

        # Ensure we wait until the trolley-total is visible
        try:
            webdriverui.WebDriverWait(self.webDriver, 20)\
                .until(EC.visibility_of_element_located((By.CLASS_NAME, "trolley-total")))
        except WebDriverException:
            logging.error("Wait for Trolley-Total webdriver element exception")
            return None

        # Navigate to the basket contents
        try:
            BASKET_BUTTON_XPATH = '//div[@class="mini-trolley"]//a'
            elemBasketBtn = self.webDriver.find_element_by_xpath(BASKET_BUTTON_XPATH)
            elemBasketBtn.click()
            webdriverui.WebDriverWait(self.webDriver, 30)\
                .until(EC.visibility_of_element_located((By.ID, "my-trolley")))
        except NoSuchElementException:
            logging.error("Press view trolley button no such element")
            return None
        except WebDriverException:
            logging.error("Press view trolley button webdriver element exception")
            return None

        # Get the shopping items on the current page
        return self.getShoppingItems(True)

    def getFavourites(self):

        # Ensure we wait until the favourites is visible
        try:
            webdriverui.WebDriverWait(self.webDriver, 20)\
                .until(EC.visibility_of_element_located((By.CLASS_NAME, "js-navbar-favourites")))
        except WebDriverException:
            logging.error("Wait for favourites button webdriver element exception")
            return None

        # Navigate to the favourites
        try:
            FAVOURITES_BUTTON_XPATH = '//a[@class="js-navbar-favourites"]'
            elemBasketBtn = self.webDriver.find_element_by_xpath(FAVOURITES_BUTTON_XPATH)
            print(elemBasketBtn)
            elemBasketBtn.click()
            webdriverui.WebDriverWait(self.webDriver, 60)\
                .until(EC.visibility_of_element_located((By.CLASS_NAME, "products-grid")))
        except NoSuchElementException:
            logging.error("Press view favourites button no such element")
            return None
        except WebDriverException:
            logging.error("Press view favourites button webdriver element exception")
            return None

        # Get the shopping items on the current page
        return self.getShoppingItems(False)

    # Handle site login
    def siteLogin(self, siteUrl, username, password, titleMustContainStr):

        # Start webDriver
        if not self.startWebDriver():
            logging.error("Unable to start webdriver")
            return False
        self.isInitalized = True

        # Go to URL
        logging.info("Webdriver going to " + siteUrl)
        self.webDriver.get(siteUrl)
        logging.info("Webdriver site title = " + self.webDriver.title)
        if not titleMustContainStr in self.webDriver.title:
            logging.error("Site " + siteUrl + " title doesn't contain " + titleMustContainStr)
            return False

        # Handle login
        self.isLoggedIn = self.websiteLogin(username, password)

        # Succeeded so far
        return self.isLoggedIn

    # Ensure that we are logged in
    def ensureLoggedIn(self, username, password):
        # Ensure we are initialised
        if not self.isInitalized:
            self.siteLogin("http://www.waitrose.com", username, password, "Waitrose")

        # Try to login again if not currently logged in
        if self.isInitalized:
            if not self.isLoggedIn:
                self.isLoggedIn = self.websiteLogin(username, password)

        return self.isLoggedIn