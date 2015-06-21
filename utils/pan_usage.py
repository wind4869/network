# -*- coding: utf-8 -*-

import time
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
    records = get_records_dt(uid)  # PAY ATTENTION!!!

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
    # the weight of edge rx->ry is (then expand 100 times):
    # Σ(1 - (ry['startTime'] - rx['startTime']) ÷ INTERVAL_DT) ÷ len(records)
    for session in sessions:
        for rec_from, rec_to in combinations(session, 2):
            app_from, app_to = [rec['appName'] for rec in rec_from, rec_to]
            if app_from == app_to:
                continue

            app_from, app_to = [mapname(app) for app in app_from, app_to]
            time_from, time_to = [rec['startTime'] for rec in rec_from, rec_to]

            if not uan.has_edge(app_from, app_to):
                uan.add_edge(app_from, app_to,
                             weights=[0 for i in xrange(NUM_EDGETYPE)])
                uan[app_from][app_to]['weights'][INDEX.USG] += \
                    1 - (time_to - time_from) / INTERVAL_DT

    # remove edges whose weight less than USG_THRESHOLD
    for u, v in uan.edges():
        ws = uan[u][v]['weights']
        w = round(ws[INDEX.USG] / len(records) * 100, 2)
        if w:
            ws[INDEX.USG] = w
        else:
            uan.remove_edge(u, v)

    # dump uan to pickle file
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


# get neighbors of node in directed graph
def neighbors(g, node):
    return g.successors(node) + g.predecessors(node)


# use u2 to recommend for u1
def recommend(u1, u2):
    result = {}

    # SHOULD USE PAN, USE UAN FOR TEST NOW!!!
    pan1, pan2 = [load_uan(u) for u in u1, u2]
    apps1, apps2 = [pan.nodes() for pan in pan1, pan2]
    apps = set(apps1) & set(apps2)
    if not apps:
        return {}

    sim = g_sim(pan1, pan2)
    if not sim:
        return {}

    # the score is: Σ(sim * weight)
    for app in apps:
        for neighbor in neighbors(pan2, app):
            if neighbor not in apps1:
                result.setdefault(neighbor, 0)
                if pan2.has_edge(app, neighbor):
                    result[neighbor] += sim * pan2[app][neighbor]['weights'][INDEX.USG]
                if pan2.has_edge(neighbor, app):
                    result[neighbor] += sim * pan2[neighbor][app]['weights'][INDEX.USG]

    for app, score in result.iteritems():
        result[app] = round(score, 2)

    return result


# get topk from result
def topk(result, k):
    temp = []
    for app, fitness in result.iteritems():
        temp.append([app, fitness])

    return sorted(temp, key=lambda x: x[1], reverse=True)[:k]


if __name__ == '__main__':
    pass
    # for uid in USER_IDS_US:
    #     create_uan(uid)
    # for uid in USER_IDS_DT:
    #     create_uan(uid)
    # for app, fitness in topk(recommend('1001', '1002'), 10):
    #     print app, fitness
