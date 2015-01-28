# -*- coding: utf-8 -*-

import json
import urllib2
from utils.data_read_store import *
from utils.global_consts import *
from utils.xml_parse import *
from urllib2 import urlopen

# get db object
appDetails = getAppDetails()
usageRecords = getUsageRecords()


def store_top_info():
    # data to store
    app_details = []

    for i in xrange(COUNT + 1):
        apps = urlopen(TOP_INFO_URL % (MAX_ONCE, START)).read()
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


# e.g. ['likesCount', 'likesRate', 'dislikesCount', 'downloadCount', 'installedCount', 'commentsCount'])
def get_other_info(attrs):
    for app in load_apps():
        other_dict = {}
        for attr in attrs:
            other_dict[attr] = 0
        try:
            info = json.loads(urlopen(INFO_BY_PACKAGE_NAME % (packageName(app), ','.join(attrs))).read())
            for attr in attrs:
                other_dict[attr] = int(info[attr])
            print other_dict
        except urllib2.HTTPError:
            print 'error in getting info of <%s>' % app
        appDetails.update({'title': app}, {'$set': other_dict})


# get content from file
def content(path):
    f = open(path)
    lines = f.readlines()
    f.close()
    return eval(lines[0]) if lines else None


# get raw intents, process, return (explicits, implicits)
def get_intents(app):
    commons, natives = [], []  # two kinds of explict intents
    implicits = []  # implicit intents

    # raw string of intents
    raw_intents = content(INTENT_PATH % app)
    # pattern for removing self-calling intents
    self_pattern = re.compile(packageName(app))
    # pattern for recognizing native-app-calling intents
    native_pattern = re.compile('com.android')

    if raw_intents:
        for typed_intents in [raw_intents.get(i) for i in ['called', 'queried']]:
            if typed_intents:
                for key in typed_intents:
                    for intent in typed_intents[key]:
                        if 'explicit' not in intent:
                            continue
                        if intent['explicit'] == 'true':  # explicit intents
                            class_name = intent.get('class')
                            if class_name:
                                class_name = class_name.replace(r'/', r'.')  # remove self-calling intents
                                if not self_pattern.match(class_name):
                                    if native_pattern.match(class_name):  # native-app-calling intents
                                        natives.append(class_name)
                                    else:
                                        commons.append(class_name)
                        else:
                            intent.pop('explicit')  # implicit intents
                            if intent:
                                implicits.append(intent)

    return commons, natives, implicits


# store intents, intent-filters and permissions to mongodb
def store_intents_filters_perms():
    for app in load_apps():
        commons, natives, implicits = get_intents(app)
        explicits = {'commons': commons, 'natives': natives}
        filters, perms = parer(XML_PATH % app)

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


# store personal usage records to mongodb
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
    #     print r