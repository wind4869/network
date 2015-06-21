# -*- coding: utf-8 -*-

import json
import urllib2

from utils.parser_desc import *
from utils.parser_apk import *


# get db object
appDetails = getAppDetails()
usageRecords = getUsageRecords()


# get categories, tags, permissions of
# top apps by a crawler using urllib2
def store_main_info():
    # data to store
    app_details = []

    for i in xrange(COUNT + 1):
        apps = urllib2.urlopen(TOP_INFO_URL % (MAX_ONCE, START)).read()
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

            app_details.append(tidyApp)

    # store to mongodb
    appDetails.insert(app_details)


# get other information of all apps using urllib2
# e.g. attrs = ['likesCount', 'likesRate', 'dislikesCount', \
# 'downloadCount', 'installedCount', 'commentsCount'])
def store_other_info(attrs):
    for app in load_capps():
        other_dict = {}
        for attr in attrs:
            other_dict[attr] = 0
        try:
            info = json.loads(urllib2.urlopen(
                INFO_BY_PACKAGE_NAME % (packageName(app), ','.join(attrs))).read())
            for attr in attrs:
                other_dict[attr] = int(info[attr])
            print other_dict
        except urllib2.HTTPError:
            print '[get_other_info][urllib2.HTTPError]: %s' % app
        appDetails.update({'title': app}, {'$set': other_dict})


# store intents, intent-filters and permissions to mongodb
def store_intents_filters_perms():
    for app in load_capps():
        commons, natives, implicits = get_intents(app)
        explicits = {'commons': commons, 'natives': natives}
        filters, perms = get_filters(XML_PATH % app)

        appDetails.update(
            {
                'title': app
            },
            {
                '$set': {
                    'explicits': explicits,
                    'implicits': implicits,
                    'filters': filters,
                    'perms': perms
                }
            })


# store IO vectors, refs and nats of apps
def store_vectors_refs_nats():
    update_appdict()
    for app in load_capps():
        appDetails.update(
            {
                'title': app
            },
            {
                '$set': {
                    'vectors': get_vectors(app),
                    'refs': get_refs(app),
                    'nats': get_nats(app)
                }
            })


# store personal usages records to mongodb
def store_usage_records(uid):
    usage_records = []

    f = open_in_utf8('Dhao.txt')
    attrs = ['startTime', 'endTime', 'appName', 'appID', 'userID']
    for line in f.readlines():
        record = {}
        parts = line.strip().replace(u'\x00', ''). \
            replace(u'\x02', '').split(',')
        parts.append(uid)
        for i in xrange(len(attrs)):
            record.setdefault(attrs[i], parts[i])
        usage_records.append(record)

    f.close()
    usageRecords.insert(usage_records)


if __name__ == '__main__':
    pass
    # store_usage_records('F07')
    # usageRecords.remove({'userID': 'F07'})
    # for r in usageRecords.find({'userID': 'F07'}):
    # print r
