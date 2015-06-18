# -*- coding: utf-8 -*-

from pymongo import MongoClient

client = MongoClient()
appInfo = client['appInfo']


def getAppDetails():
    return appInfo['appDetails']


def getUsageRecords():
    return appInfo['usageRecords']