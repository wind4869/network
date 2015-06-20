# -*- coding: utf-8 -*-

import time
from utils.funcs_rw import *
from itertools import combinations


# get the func which creates time object from string
def get_mktime(pattern):
    return lambda s: time.mktime(time.strptime(s, pattern))


# get the func which maps pan' appname to gan' appname
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
            print '[get_records_us][ValueError]: %s' % r['startTime']
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
    records = get_records_us(uid)

    apps = set([])
    session = []
    prev = records[0]['startTime']
    for record in records:
        if record['startTime'] - prev < INTERVAL_DT:
            session.append(record['appName'])
        else:
            sessions.append(session)
            session = [record['appName']]
        prev = record['startTime']
        apps.add(record['appName'])

    if session:
        sessions.append(session)

    uan = nx.Graph()
    uan.add_nodes_from([mapname(app) for app in apps])

    for session in sessions:
        temp = set(session)
        for app_from, app_to in combinations(temp, 2):
            app_from, app_to = [mapname(app) for app in app_from, app_to]
            if not uan.has_edge(app_from, app_to):
                uan.add_edge(app_from, app_to,
                             weights=[0 for i in xrange(NUM_EDGETYPE)])
            uan[app_from][app_to]['weights'][INDEX.USG] += 1

    dump_uan(uid, uan)


# compute similarity of two graphs
def g_sim(pan1, pan2):
    mnodes = max(len(pan1.nodes()), len(pan2.nodes()))
    mcs = 0

    for app_from, app_to in pan1.edges():
        if pan2.has_edge(app_from, app_to):
            mcs += pan1[app_from][app_to]['weights'][INDEX.USG] + \
                pan2[app_from][app_to]['weights'][INDEX.USG]

    return mcs * 1.0 / mnodes


# use u2 to recommend for u1
def recommend(u1, u2):
    result = {}

    # should use pan!!! use uan for tests!!!
    pan1, pan2 = [load_uan(u) for u in u1, u2]
    apps1, apps2 = [pan.nodes() for pan in pan1, pan2]
    apps = set(apps1) & set(apps2)
    if not apps:
        return {}

    sim = g_sim(pan1, pan2)
    if not sim:
        return {}

    for app in apps:
        for neighbor in pan2.neighbors(app):
            if neighbor not in apps1:
                result.setdefault(neighbor, 0)
                result[neighbor] += sim * pan2[app][neighbor]['weights'][INDEX.USG]

    return result


# get topk from result
def topk(result, k):
    temp = []
    for app, fitness in result.iteritems():
        temp.append([app, fitness])

    return sorted(temp, key=lambda x: x[1], reverse=True)[:k]


if __name__ == '__main__':
    for uid in USER_IDS_US:
        create_uan(uid)
    # for app, fitness in topk(recommend('1001', '1002'), 10):
    #     print app, fitness
