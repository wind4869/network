# -*- coding: utf-8 -*-

import re
import json
from utils.db_read import *
from utils.global_consts import *
from urllib2 import urlopen

# get db object
appDetails = getAppDetails()


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


# get content from file
def content(path):
    f = open(path)
    lines = f.readlines()
    f.close()
    return eval(lines[0]) if lines else None


# get raw intents, process, return (explicits, implicits)
def get_intents(app):
    commons, systems = [], []  # two kinds of explict intents
    implicits = []  # implicit intents

    # raw string of intents
    raw_intents = content(INTENT_PATH % app)
    # pattern for removing self-calling intents
    self_pattern = re.compile(packageName(app))
    # pattern for recognizing system-app-calling intents
    sys_pattern = re.compile('com.android')

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
                                    if sys_pattern.match(class_name):  # system-app-calling intents
                                        systems.append(class_name)
                                    else:
                                        commons.append(class_name)
                        else:
                            intent.pop('explicit')  # implicit intents
                            if intent:
                                implicits.append(intent)
    return commons, systems, implicits


# get intent-filters: [{...}, {...}, ..., {...}]
def get_intent_filters(app):
    return content(INTENT_FILTER_PATH % app)


# store intents and intent-filters to mongodb
def store_intents():
    for app in load_apps():
        commons, systems, implicits = get_intents(app)
        explicits = {'commons': commons, 'systems': systems}

        appDetails.update(
            {'title': app},
            {'$set': {
                'explicits': explicits,
                'implicits': implicits,
                'filters': get_intent_filters(app)}})


if __name__ == '__main__':
    store_intents()