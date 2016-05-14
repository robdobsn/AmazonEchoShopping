# Waitrose online shopping webservice

__author__ = 'robdobsn'

from flask import Flask
from ShoppingManager import ShoppingManager
import logging
import time

app = Flask(__name__)

@app.route('/')
def index():
    return appName

@app.route('/waitrose/api/v1.0/<accountCode>/trolleyinfo')
def getTrolleyInfo(accountCode):
    return shoppingManager.getTrolleyInfo(accountCode)

if __name__ == '__main__':

    # Set logging level
    logging.basicConfig(level=logging.INFO)

    # App name
    appName = "Waitrose Service 0.1"
    logging.info(appName + " Starting")

    # Start WaitroseManager
    shoppingManager = ShoppingManager()

    # Start server
    # use_reloader=False avoids initialising objects twice
    # note that server is single-threaded - and it doesn't seem to help to turn theading on - maybe due to GIL
    # so every request has to return quickly and not block
    app.run(debug=True, use_reloader=False)

