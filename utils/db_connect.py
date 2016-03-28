# -*- coding: utf-8 -*-

from pymongo import MongoClient

client = MongoClient()
appInfo = client['appInfo']


def getAppDetails():
    return appInfo['appDetails']


def getUsageRecords():
    return appInfo['usageRecords']


def getAppVersions():
    return appInfo['appVersions']


if __name__ == '__main__':
    pass
