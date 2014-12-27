from pymongo import MongoClient


def getAppDetails():
    client = MongoClient()
    appInfo = client['appInfo']
    appDetails = appInfo['appDetails']

    return appDetails
