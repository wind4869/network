# -*- coding: utf-8 -*-

import time
from math import sqrt
from itertools import combinations

from utils.funcs_rw import *


# get the func which creates time object from string
def get_mktime(pattern):
    return lambda s: time.mktime(time.strptime(s, pattern))


# get the func which maps pan' app name to gan' app name
def get_mapfunc():
    apps = load_capps()
    appmap = load_appmap()

    def mapname(app):
        if app in apps:
            return app
        if app.strip() in apps:
            return app.strip()
        if app in appmap:
            return appmap[app]
        if app.strip() in appmap:
            return appmap[app.strip()]
        return '[%s]' % app.strip()

    return mapname


# get usage records from mongodb
def get_records_us(uid):
    records = []
    maketime = get_mktime(DATE_PATTERN_US)
    for r in getUsageRecords().find({'userID': uid}):
        try:
            r['startTime'] = maketime(r['startTime'])
            records.append(r)
        except:
            print '[get_records_us][ValueError]: %s' % uid
    return sorted(records, key=lambda x: x['startTime'])


# get usage records from csv file
def get_records_dt(uid):
    records = []
    maketime = get_mktime(DATE_PATTERN_DT)
    f = open_in_utf8('/Users/wind/Desktop/usages.csv')
    for line in f.readlines():
        temp = line.split(',')
        if temp[7].strip() == uid:
            records.append(
                {
                    'startTime': maketime(temp[0]),
                    'appName': temp[1]
                })
    return sorted(records, key=lambda x: x['startTime'])


# create uan from usages records
def create_uan(uid):
    sessions = []
    mapname = get_mapfunc()
    records = get_records_us(uid)  # PAY ATTENTION!!!

    apps_uan = {}
    session = []  # [[r0, r1, r2, ... ], [rx, ry, rz, ... ], ... ]
    prev = records[0]['startTime']
    for record in records:
        app = record['appName']
        stime = record['startTime']

        if stime - prev < INTERVAL_DT:
            session.append(record)
        else:
            sessions.append(session)
            session = [record]
        prev = stime

        # calculate the weight of each app
        apps_uan.setdefault(app, 0)
        apps_uan[app] += 1

    if session:
        sessions.append(session)

    uan = nx.DiGraph()
    for app, weight in apps_uan.iteritems():
        uan.add_node(mapname(app), weight=round(float(weight) / len(records), 2))

    # create the edge: r0->r1, r0->r2, r1->r2, ...
    # the weight of edge rx->ry is:
    # Σ(1 - r_interval ÷ s_interval) ÷ len(records)
    for session in sessions:
        s_interval = session[-1]['startTime'] - session[0]['startTime']
        for rec_from, rec_to in combinations(session, 2):
            app_from, app_to = [rec['appName'] for rec in rec_from, rec_to]
            if app_from == app_to:
                continue

            app_from, app_to = [mapname(app) for app in app_from, app_to]
            time_from, time_to = [rec['startTime'] for rec in rec_from, rec_to]
            r_interval = time_to - time_from

            weights = get_weights(uan, app_from, app_to)
            weights[INDEX.USG] += 1 - r_interval / (s_interval + 1)  # plus 1 to avoid 0

    # find the max weight and use sqrt to "smooth"
    mw = 0
    for u, v in uan.edges():
        ws = uan[u][v]['weights']
        w = sqrt(ws[INDEX.USG] / len(records))
        if w > mw:
            mw = w
        ws[INDEX.USG] = w

    # divide max weight to normalize
    for u, v in uan.edges():
        ws = uan[u][v]['weights']
        ws[INDEX.USG] /= mw

    # dump uan to pickle file
    dump_uan(uid, uan)


if __name__ == '__main__':
    # pass
    for uid in USER_IDS_US:
        create_uan(uid)
    # for uid in USER_IDS_DT:
    #     create_uan(uid)