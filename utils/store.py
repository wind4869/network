# -*- coding: utf-8 -*-

import json
from urllib2 import urlopen
from pymongo import MongoClient

# connect to mongodb
client = MongoClient()
appInfo = client['appInfo']
appDetails = appInfo['appDetails']


url = 'http://apps.wandoujia.com/api/v1/apps?type=top&max=%d&start=%d&\
opt_fields=packageName,title,description,editorComment,changelog,categories.*.name,tags.*,apks.permissions'
directAttr = ['packageName', 'title', 'description', 'editorComment', 'changelog']

total = 1000
maxOnce = 60
start = 0
count = total / maxOnce

allAppDetails = []
for i in xrange(count + 1):
    apps = urlopen(url % (maxOnce, start)).read()
    start += maxOnce

    tidyApp = {}
    apps = json.loads(apps)
    for app in apps:
        for attr in directAttr:
            tidyApp[attr] = app[attr]
        categories = []
        for c in app['categories']:
            categories.append(c['name'])
        tidyApp['categories'] = categories
        tags = []
        for t in app['tags']:
            tags.append(t['tag'])
        tidyApp['tag'] = tags
        tidyApp['permissions'] = app['apks'][0]['permissions']

        allAppDetails.append(tidyApp)

# store to mongodb
# appDetails.insert(allAppDetails)
print len(allAppDetails)