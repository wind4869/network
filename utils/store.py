# -*- coding: utf-8 -*-

import json
from utils.connect import *
from utils.constants import *
from urllib2 import urlopen

# data to store
allAppDetails = []
# get db object
appDetails = getAppDetails()

for i in xrange(COUNT + 1):
    apps = urlopen(DETAIL_URL % (MAX_ONCE, START)).read()
    START += MAX_ONCE

    tidyApp = {}
    apps = json.loads(apps)
    for app in apps:
        for attr in DIRECT_ATTR:
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
appDetails.insert(allAppDetails)
print len(allAppDetails)