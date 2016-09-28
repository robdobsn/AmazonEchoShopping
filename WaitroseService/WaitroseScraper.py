# Waitrose web scraper

__author__ = 'robdobsn'

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import selenium.webdriver.support.ui as webdriverui
from selenium.webdriver.support.wait import WebDriverWait
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
        self.webDriverType = "PhantomJS"
        self.execUsingJS = False

    def clickButtonByClassName(self, className):
        if self.execUsingJS:
            self.webDriver.execute_script("document.getElementsByClassName('" + className + "')[0].click()")
        else:
            btn = self.webDriver.find_element_by_class_name(className)
            btn.click()

    def clickButtonByXPath(self, xpath):
        if self.execUsingJS:
            self.webDriver.execute_script("return document.evaluate('" + xpath + "', document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue.click()")
        else:
            btn = self.webDriver.find_element_by_xpath(xpath)
            btn.click()

    def clickButtonByCSSSelector(self, cssSelector):
        btn = self.webDriver.find_element_by_css_selector(cssSelector)
        btn.click()

    def checkButtonEnabledByCSSSelector(self, cssSelector):
        btn = self.webDriver.find_element_by_css_selector(cssSelector)
        return btn.is_enabled() and btn.is_displayed()

    def sendKeysToFieldById(self, elemId, strToSend, pressEnterAfter, clearFirst):
#       if self.execUsingJS:
#            self.webDriver.execute_script("document.getElementsByClassName('" + elemId + "').value = '" + strToSend)
#        else:
        print("Sending keys to elemId " + elemId + " keys = " + strToSend)
        field = self.webDriver.find_element_by_id(elemId)
        print(field)
        if (clearFirst):
            field.send_keys(Keys.CONTROL + "a")
            field.send_keys(Keys.DELETE)
        field.send_keys(strToSend + (Keys.RETURN if pressEnterAfter else ""))

    def debugDumpPageSource(self, filenameExtra=""):
        with open("debugPageSource" + filenameExtra + ".html", "w") as debugDumpFile:
           debugDumpFile.write(self.webDriver.page_source)
        self.webDriver.save_screenshot('debugPageImage.png')

    # Start the web driver (runs the browser)
    def startWebDriver(self):

        # Clear current session file info
        with open('browserSession.json', 'w') as outfile:
            json.dump({}, outfile)

        # Create WebDriver
        if self.webDriverType == "Chrome":
            try:
                self.webDriver = webdriver.Chrome()
            except WebDriverException:
                logging.error("startWebDriver() Chrome Failed to start")
                return False
        elif self.webDriverType == "Firefox":
            try:
                self.webDriver = webdriver.Firefox()
            except WebDriverException:
                logging.error("startWebDriver() Firefox Failed to start")
                return False
        elif self.webDriverType == "PhantomJS":
            try:
                self.webDriver = webdriver.PhantomJS()  # or add to your PATH
            except:
                try:
                    self.webDriver = webdriver.PhantomJS(
                        executable_path='C:\ProgramData\PhantomJS\bin')
                except:
                    try:
                        self.webDriver = webdriver.PhantomJS(
                            executable_path='/usr/local/lib/node_modules/phantomjs/lib/phantom/bin/phantomjs')
                    except:
                        try:
                            self.webDriver = webdriver.PhantomJS(
                                executable_path=r'C:\Users\rob_2\AppData\Roaming\npm\node_modules\phantomjs\lib\phantom\bin\phantomjs.exe')
                        except:
                            logging.error("Failed to load the PhantomJS webdriver")
                            return False

        # Set the window size (seems to be needed in phantomJS particularly
        # This is probably because the website responds in mobile mode?
        self.webDriver.set_window_size(1280,1024)

        # Save session info
        url = self.webDriver.command_executor._url
        session_id = self.webDriver.session_id
        with open('browserSession.json', 'w') as outfile:
            json.dump({"url": url, "session_id": session_id}, outfile)

        return True

    def websiteLogin(self, username, password, attemptIdx):
        try:
            self.webDriver.save_screenshot('debug1_'+str(attemptIdx)+'.png')
            logging.info("Waiting for signInRegister button")
            wait = WebDriverWait(self.webDriver, 30)
            wait.until(EC.visibility_of_element_located((By.CLASS_NAME, "js-sign-in-register")))
            logging.info("waitroseLogin() pressing signInRegister button")
            self.clickButtonByClassName('js-sign-in-register')
            self.webDriver.save_screenshot('debug2_'+str(attemptIdx)+'.png')

            try:
                print("Starting to wait for logon-email")
                wait = WebDriverWait(self.webDriver, 30)
                wait.until(EC.visibility_of_element_located((By.ID, "logon-email")))
                print("Finished waiting for logon-email")
                self.webDriver.save_screenshot('debug3_' + str(attemptIdx) + '.png')

                try:
                    logging.info("waitroseLogin() entering username")
                    self.debugDumpPageSource("contbutton")
                    self.sendKeysToFieldById('logon-email', username, False, True)
                    self.webDriver.save_screenshot('debug4_' + str(attemptIdx) + '.png')
                    # self.clickButtonByXPath("//input[@type='button' and @value='Continue']")
                    if (self.checkButtonEnabledByCSSSelector("input[value='Continue'][type='button']")):
                        self.clickButtonByCSSSelector("input[value='Continue'][type='button']")

                    try:
                        logging.info("waitroseLogin() waiting for logon-password visible")
                        wait = WebDriverWait(self.webDriver, 60)
                        wait.until(EC.visibility_of_element_located((By.ID, "logon-password")))
                        self.webDriver.save_screenshot('debug5_' + str(attemptIdx) + '.png')

                        try:
                            logging.info("waitroseLogin() entering password")
                            self.sendKeysToFieldById('logon-password', password, False, True)
                            #self.clickButtonById('logon-button-sign-in')
                            self.clickButtonByCSSSelector("input[value='Sign in'][type='button']")
                            self.webDriver.save_screenshot('debug6_' + str(attemptIdx) + '.png')
                            logging.info("waitroseLogin() waiting for trolley-total to be visible")
                            wait = WebDriverWait(self.webDriver, 60)
                            wait.until(EC.visibility_of_element_located((By.CLASS_NAME, "trolley-total")))
                            self.webDriver.save_screenshot('debug7_' + str(attemptIdx) + '.png')
                            elem2 = self.webDriver.find_element_by_class_name('trolley-total')
                            if elem2:
                                logging.info("waitroseLogin() basket found")
                            else:
                                logging.info("waitroseLogin() basket not found")

                            return True

                        except WebDriverException as err:
                            logging.error("waitroseLogin() Cannot find logon-password after wait " + err.msg)
                            self.debugDumpPageSource()

                    except WebDriverException as err:
                        logging.error("waitroseLogin() Cannot find logon-password field" + err.msg)
                        self.debugDumpPageSource()

                except WebDriverException as err:
                    logging.error("waitroseLogin() Error entering logon-email" + err.msg)
                    self.debugDumpPageSource()

            except WebDriverException as err:
                logging.error("waitroseLogin() Cannot find logon-email field" + err.msg)
                self.debugDumpPageSource()

        except WebDriverException as err:
            logging.error("waitroseLogin() Cannot find sign-in-register button" + err.msg)
            self.debugDumpPageSource()

        return False

    def getBasketSummary(self):

        basketSummary = {}

        # Ensure we wait until the trolley-total is visible
        try:
            wait = WebDriverWait(self.webDriver, 20)
            wait.until(EC.visibility_of_element_located((By.CLASS_NAME, "trolley-total")))
        except TimeoutException:
            logging.error("Get basket summary timeout exception")
            self.debugDumpPageSource()
            return None
        except WebDriverException:
            logging.error("Get basket summary webdriver element exception")
            self.debugDumpPageSource()
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
            self.debugDumpPageSource()
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
        except WebDriverException:
            logging.error("waitrose: Error extracting element " + elemName + " " + className)
            self.debugDumpPageSource()
        except:
            logging.error("waitrose: Error (not webdriver) extracting element " + elemName + " " + className)
            self.debugDumpPageSource()
        return rslt

    def getShoppingItems(self, isTrolleyPage):

        # Make sure all items on the page are loaded - lazy loader
        try:
            self.debugDumpPageSource("m-product")
            webdriverui.WebDriverWait(self.webDriver, 10)\
                .until(EC.visibility_of_element_located((By.CLASS_NAME, "m-product")))
        except WebDriverException:
            logging.error("Wait for m-product webdriver element exception")
            return []
        
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
            wait = WebDriverWait(self.webDriver, 20)
            wait.until(EC.visibility_of_element_located((By.CLASS_NAME, "trolley-total")))
        except WebDriverException:
            logging.error("Wait for Trolley-Total webdriver element exception")
            self.debugDumpPageSource()
            return None

        # Navigate to the basket contents
        try:
            self.clickButtonByXPath('//div[@class="mini-trolley"]//a')
            wait = WebDriverWait(self.webDriver, 30)
            wait.until(EC.visibility_of_element_located((By.ID, "my-trolley")))
        except NoSuchElementException:
            logging.error("Press view trolley button no such element")
            self.debugDumpPageSource()
            return None
        except WebDriverException:
            logging.error("Press view trolley button webdriver element exception")
            self.debugDumpPageSource()
            return None

        # Get the shopping items on the current page
        return self.getShoppingItems(True)

    def getFavourites(self):

        # Ensure we wait until the favourites is visible
        try:
            wait = WebDriverWait(self.webDriver, 20)
            wait.until(EC.visibility_of_element_located((By.CLASS_NAME, "js-navbar-favourites")))
        except WebDriverException:
            logging.error("Wait for favourites button webdriver element exception")
            self.debugDumpPageSource()
            return None

        # Navigate to the favourites
        try:
            FAVOURITES_BUTTON_XPATH = '//a[@class="js-navbar-favourites"]'
            elemBasketBtn = self.webDriver.find_element_by_xpath(FAVOURITES_BUTTON_XPATH)
            print(elemBasketBtn)
            elemBasketBtn.click()
            wait = WebDriverWait(self.webDriver, 60)
            wait.until(EC.visibility_of_element_located((By.CLASS_NAME, "products-grid")))
        except NoSuchElementException:
            logging.error("Press view favourites button no such element")
            self.debugDumpPageSource()
            return None
        except WebDriverException:
            logging.error("Press view favourites button webdriver element exception")
            self.debugDumpPageSource()
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
            self.debugDumpPageSource()
            return False

        # Handle login
        self.isLoggedIn = self.websiteLogin(username, password, 1)

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
                self.isLoggedIn = self.websiteLogin(username, password, 2)

        return self.isLoggedIn
