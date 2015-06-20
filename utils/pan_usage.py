# -*- coding: utf-8 -*-

import time
from utils.funcs_rw import *
from itertools import combinations


# create time object from string
def maketime(s):
    return time.mktime(time.strptime(s, DATE_PATTERN_DT))


# create uan from usages records
def create_uan(uid):
    records, sessions = [], []
    f = open_in_utf8('/Users/wind/Desktop/usages.csv')
    for line in f.readlines():
        temp = line.split(',')
        if temp[7].strip() == uid:
            records.append([maketime(temp[0]), temp[1]])
    records = sorted(records, key=lambda x: x[0])

    apps = set([])
    session = []
    prev = records[0][0]
    for record in records:
        if record[0] - prev < INTERVAL_DT:
            session.append(record[1])
        else:
            sessions.append(session)
            session = [record[1]]
        prev = record[0]
        apps.add(record[1])

    if session:
        sessions.append(session)

    uan = nx.Graph()
    uan.add_nodes_from(apps)

    for session in sessions:
        temp = set(session)
        for app_from, app_to in combinations(temp, 2):
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
    pan1, pan2 = [load_uan(UAN_PICKLE % u) for u in u1, u2]
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
    for uid in ['1001', '1002']:
        create_uan(uid)
    for app, fitness in topk(recommend('1001', '1002'), 10):
        print app, fitness
