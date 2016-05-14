# Account codes are used to hash the account info

__author__ = 'robdobsn'

import json

class AccountCoding():

    @staticmethod
    def getStoreName(accountCode):
        splitAc = accountCode.split("_")
        return splitAc[0] if len(splitAc) > 0 else ""

    @staticmethod
    def getUserNameAndPw(accountCode):
        splitAc = accountCode.split("_")
        if len(splitAc) <= 1:
            return None
        acname = splitAc[1]
        with open('config.json') as configData:
            config = json.load(configData)
            if not acname in config:
                return None
            if not "username" in config[acname]:
                return None
            if not "password" in config[acname]:
                return None
            return config[acname]
        return None
