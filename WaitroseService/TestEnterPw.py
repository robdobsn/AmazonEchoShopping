import sys
import os
from datetime import datetime
from os.path import expanduser
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, WebDriverException, TimeoutException
import logging

def startWebDriver(webDriverType):
    # Create WebDriver
    webDriver = None
    if webDriverType == "Chrome":
        try:
            webDriver = webdriver.Chrome()
        except WebDriverException as excp:
            logging.error("startWebDriver() Chrome Failed to start", format(excp))
            return False
    elif webDriverType == "Firefox":
        try:
            webDriver = webdriver.Firefox()
        except WebDriverException as excp:
            logging.error("startWebDriver() Firefox Failed to start", format(excp))
            return False
    elif webDriverType == "PhantomJS":
        # Get home folder
        home = expanduser("~")
        try:
            webDriver = webdriver.PhantomJS()  # or add to your PATH
        except WebDriverException as excp:
            try:
                webDriver = webdriver.PhantomJS(
                    executable_path='/usr/local/lib/node_modules/phantomjs/lib/phantom/bin/phantomjs')
            except WebDriverException as excp:
                try:
                    webDriver = webdriver.PhantomJS(
                        executable_path=home + r'\AppData\Roaming\npm\node_modules\phantomjs\lib\phantom\bin\phantomjs.exe')
                except WebDriverException as excp:
                    logging.error("Failed to load the PhantomJS webdriver", format(excp))
                    return False

    # Set the window size (seems to be needed in phantomJS particularly
    # This is probably because the website responds in mobile mode?
    if webDriver is not None:
        webDriver.set_window_size(1280, 1024)
    return webDriver

#driver = startWebDriver("PhantomJS")

# def is_exe(fpath):
#     return os.path.isfile(fpath) and os.access(fpath, os.X_OK)
#
# print(os.environ["PATH"])
# for path in os.environ["PATH"].split(os.pathsep):
#     path = path.strip('"')
#     exe_file = os.path.join(path, "phantomjs.exe")
# #    fpath, fname = os.path.split("phantomjs.exe")
# def is_exe(fpath):
#     return os.path.isfile(fpath) and os.access(fpath, os.X_OK)

#print(os.path)

driver = webdriver.PhantomJS()
driver.set_window_size(1280, 1024)

def debugDumpPageSource(fileName):
    with open(fileName, "w") as debugDumpFile:
        debugDumpFile.write(driver.page_source)

def formXpathStr(srchStr="", by="xpath", elemType=""):
    xpStr = srchStr
    if by == "id":
        xpStr = "//" + elemType + "[@id='" + srchStr + "']"
    elif by == "class":
        xpStr = "//" + elemType + "[contains(concat(' ', normalize-space(@class), ' '), ' " + srchStr + " ')]"
    return xpStr

def checkElementPresent(srchStr="", by="xpath", elemType=""):
    xpStr = formXpathStr(srchStr, by, elemType)
    try:
        elem = driver.find_element_by_xpath(xpStr)
        print(elem)
        print("checkElementPresent " + xpStr + " returning TRUE")
        return True
    except:
        print("checkElementPresent - element not found " + xpStr)
    return False

def waitForElement(srchStr="", by="xpath", elemType="", thingToWaitFor="visible", waitTime = 10):
    xpStr = formXpathStr(srchStr, by, elemType)
    print("waitForElement " + thingToWaitFor + ", " + xpStr)
    try:
        wait = WebDriverWait(driver, waitTime)
        if thingToWaitFor == "visible":
            wait.until(EC.visibility_of_element_located((By.XPATH, xpStr)))
        elif thingToWaitFor == "clickable":
            wait.until(EC.element_to_be_clickable((By.XPATH, xpStr)))
        return True
    except:
        print("waitForElement timed out waiting for " + thingToWaitFor + ", " + srchStr + " by " + by + " elemType " + elemType)
        return False

def clickButton(srchStr="", by="xpath", elemType="", useJs=False):
    xpStr = formXpathStr(srchStr, by, elemType)
    debugMethodName = "clickButton"
    try:
        print("clickButton " + xpStr)
        if useJs:
            scriptToExec = "return document.evaluate(\"" \
                       + xpStr \
                       + "\", document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue.click();"
            scriptToExec = "return document.getElementsByClassName('button-continue')[0];"
        # print("El")
        # print(driver.execute_script(scriptToExec));
        # scriptToExec = "document.evaluate(\"" \
        #                + xpStr \
        #                + "\", document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue" \
        #                + ".click();"
            print("PRESSING")
            driver.save_screenshot('debug__2_1.png')
            print(driver.execute_script(scriptToExec))
            elem = driver.find_element_by_xpath(xpStr)
            print(elem)
        else:
            driver.save_screenshot('debug__2_2.png')
            elem = driver.find_element_by_xpath(xpStr)
            elem.click()
            print(elem)
        return True
    except NoSuchElementException as ex:
        print(debugMethodName + " NoSuchElementException " + xpStr + " error " + "{0}".format(ex) )
    except TimeoutException as ex:
        print(debugMethodName + " TimeoutException " + xpStr + " error " + "{0}".format(ex) )
    except WebDriverException as ex:
        print(debugMethodName + " WebDriverException " + xpStr + " error " + "{0}".format(ex) )
    return False

def sendKeys(fieldStr, srchStr="", by="xpath", elemType="", useJs=False):
    xpStr = formXpathStr(srchStr, by, elemType)
    debugMethodName = "sendKeys"
    try:
        print("sendKeys " + xpStr)
        if useJs:
            scriptToExec = "document.evaluate(\"" \
                        + xpStr \
                        + "\", document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue" \
                        + ".setAttribute('value',\"" \
                        + fieldStr \
                        + "\");"
            driver.execute_script(scriptToExec)
        else:
           elem = driver.find_element_by_xpath(xpStr)
           print(elem)
           elem.send_keys(fieldStr)
#        print(elem)
        return True
    except NoSuchElementException as ex:
        print(debugMethodName + " NoSuchElementException " + xpStr + " error " + "{0}".format(ex))
    except TimeoutException as ex:
        print(debugMethodName + " TimeoutException " + xpStr + " error " + "{0}".format(ex))
    except WebDriverException as ex:
        print(debugMethodName + " WebDriverException " + xpStr + " error " + "{0}".format(ex))
    return False

driver.get("http://www.waitrose.com")
driver.save_screenshot('debug__1.png')
ok = True
if ok:
    if not checkElementPresent(elemType="button", srchStr='js-sign-in-register', by="class"):
        print("sign in not visible")
        ok = False
if ok:
    if not clickButton("//div[@id='headerSignInRegister']/button"):
        print("failed to click sign-in")
        ok = False

if ok:
    if not waitForElement("//input[@id='logon-email']"):
        print("failed to see logon-email")
        ok = False

if ok:
    if not sendKeys("judyw@marketry.co.uk", "//input[@id='logon-email']"):
        print("failed to enter logon-email")
        ok = False

# if ok:
#     if not checkVisible("//input[@id='logon-password']"):
#         if not waitForElement("//input[@type, 'button' and text()='Continue']"):
#             print("failed to see continue button or logon-password")
#             ok = False
if ok:
    # if not clickButton("//input[@type, 'button' and text()='Continue']", useJs=True):
    if not clickButton("//input[@value='Continue']", useJs=True):
        print("failed to click continue button")
        ok = False

if ok:
    # if not clickButton("//input[@type, 'button' and text()='Continue']", useJs=True):
    if not clickButton("//input[@value='Continue']"):
        print("failed to click continue button")
        ok = False

if ok:
    if not waitForElement("//input[@value='Sign in']", thingToWaitFor="clickable"):
        print("failed to see sign-in button")
        ok = False

if ok:
    if not sendKeys("minder01", "//input[@id='logon-password']"):
        print("failed to enter logon-password")
        ok = False

if ok:
#    if not clickButton("//input[@type, 'button' and text()='Sign In']", useJs=True):
    if not clickButton("//input[@value='Sign in']"):
        print("failed to click sign in ")
        ok = False

if ok:
    if not waitForElement("//span[@class='trolley-total']", thingToWaitFor="clickable"):
        print("failed to see headerMiniTrolley")
        ok = False

driver.save_screenshot('debug__2.png')
debugDumpPageSource("debug__2.html")

# elem = driver.find_element_by_name("q")
# elem.clear()
# elem.send_keys("python")
# elem.send_keys(Keys.RETURN)
# button = driver.find_element_by_id('submit')
# button.click()



#clickButtonByXPath("//input[@type, 'button' and text()='Continue']")


#print(driver.title)
#print(driver.page_source)
driver.close()