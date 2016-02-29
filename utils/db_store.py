# -*- coding: utf-8 -*-

import json
from time import strftime, localtime
from BeautifulSoup import BeautifulSoup

from utils.parser_desc import *
from utils.parser_apk import *


# get db object
appDetails = getAppDetails()
usageRecords = getUsageRecords()


# download detail and home page of app
def download_details_htmls(app):

    if url_exists(DETAIL_URL % app) and \
            url_exists(HTML_URL % app):
        [run(cmd) for cmd in
         DETAIL_CMD % (app, app),
         HTML_CMD % (app, app)]
    else:
        print 'information not exists: %s' % app


# get similar apps from home page of app
def get_sims(app):
    sims = []
    soup = BeautifulSoup(open(HTML_PATH % app))
    for ul in soup.findAll(attrs={'class': 'side-list'}):
        for li in ul.findAll('li'):
            sims.append(li.a['href'].split('/')[2])
    return sims


# store app details from wandoujia to mongodb
def store_app_details(app):
    raw_details = json.loads(open(DETAIL_PATH % app).read())

    details = {}  # processed details for app

    # get common string and integer attributes
    [details.setdefault(attr, raw_details[attr]) for attr in STRING_ATTRS]
    [details.setdefault(attr, int(raw_details[attr])) for attr in INTEGER_ATTRS]

    # get categories
    categories = []
    for c in raw_details['categories']:
        categories.append(c['name'])
    details['categories'] = categories

    # get tags
    tags = []
    for t in raw_details['tags']:
        tags.append(t['tag'])
    details['tags'] = tags

    # get updatedDate
    details['updatedDate'] = strftime(
        TIME_FORMAT, localtime(int(str(raw_details['updatedDate'])[:10]))) \
        if raw_details['updatedDate'] else ''

    # get version (may be modified according to the API)
    details['version'] = {
        'versionCode': raw_details['apks'][0]['versionCode'],
        'versionName': raw_details['apks'][0]['versionName'],
    }

    # get developer
    details['developer'] = {
        'id': raw_details['developer']['id'],
        'name': raw_details['developer']['name'],
        'email': raw_details['developer']['email'],
    }

    # get sims
    details['sims'] = get_sims(app)

    # update or add details for app
    if appDetails.find_one({'packageName': app}):
        appDetails.update(
            {
                'packageName': app
            },
            {
                '$set': details
            })
    else:
        appDetails.insert(details)


# store intents, intent-filters and permissions to mongodb
def store_intents_filters_permissions(app):
    explicits, implicits = get_intents(app)
    filters, permissions = get_filters(app)

    appDetails.update(
        {
            'packageName': app
        },
        {
            '$set': {
                'explicits': explicits,
                'implicits': implicits,
                'filters': filters,
                'permissions': permissions,
            }
        })


# store inputs, outputs and refs to mongodb
def store_inputs_outputs_refs(app):
    update_appdict()  # update appdict.txt
    inputs, outputs = get_inputs_outputs(app)

    appDetails.update(
        {
            'packageName': app
        },
        {
            '$set': {
                'inputs': inputs,
                'outputs': outputs,
                'refs': get_refs(app),
            }
        })


# store all attributes of all apps
def store():
    for app in load_capps():
        store_app_details(app)
        store_intents_filters_permissions(app)

    for app in load_capps():
        store_inputs_outputs_refs(app)


if __name__ == '__main__':
    pass
