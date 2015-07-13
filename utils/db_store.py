# -*- coding: utf-8 -*-

import json
import pandas
import urllib2

from utils.parser_desc import *
from utils.parser_apk import *


# get db object
appDetails = getAppDetails()
usageRecords = getUsageRecords()


# store app details from wandoujia to mongodb
def store_app_details(app):
    try:
        details = json.loads(urllib2.urlopen(DETAILS_URL % app).read())
    except urllib2.HTTPError:
        print '[store_app_details][urllib2.HTTPError]: %s' % app
        return

    record = {}

    for attr in STRING_ATTRS:
        record[attr] = details[attr]
    for attr in INTEGER_ATTRS:
        record[attr] = int(details[attr])

    cats = []
    for c in details['categories']:
        cats.append(c['name'])
    record['categories'] = cats

    tags = []
    for t in details['tags']:
        tags.append(t['tag'])
    record['tag'] = tags

    # the desc of permissions
    record['permissions'] = details['apks'][0]['permissions']

    # store to mongodb
    appDetails.insert(record)


# store intents, intent-filters and permissions to mongodb
def store_intents_filters_perms(app):
    commons, natives, implicits = get_intents(app)
    explicits = {'commons': commons, 'natives': natives}
    filters, perms = get_filters(app)

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
# use update_appdict() to update appdict.txt
def store_vectors_refs_nats(app):
    # update_appdict()

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


# store user usages to mongodb
def store_usage_records():
    f1 = pandas.read_csv(USAGES_CSV, sep="\t")
    f2 = pandas.read_csv(APPMETA_CSV, sep="\t")
    f = f1.merge(f2, on='item')

    records = []
    for i in xrange(NUM_RECORDS):
        record = {}
        raw = dict(f.iloc[i])
        if int(raw['user']) in USG_USRS and int(raw['item']) in USG_APPS:
            raw['item'] = raw['package']
            raw['user'] = USG_USRS.index(raw['user'])  # fix the index of users
            [record.setdefault(attr, raw[attr]) for attr in USG_ATTRS]
            records.append(record)

    # store to mongodb
    usageRecords.insert(records)


if __name__ == '__main__':
    pass
