# -*- coding: utf-8 -*-

import time
from utils.graph import *
from utils.data_read_store import *

apps = load_apps()
map_dict = load_map_dict()


# carry out the mapping
def map_name(app):
    if app in apps:
        return app
    if app.strip() in apps:
        return app.strip()
    if app in map_dict:
        return map_dict[app]
    if app.strip() in map_dict:
        return map_dict[app.strip()]
    return '[%s]' % app.strip()


# make time from time string
def makeTime(strTime):
    return time.mktime(time.strptime(strTime, DATE_PATTERN))


# create personal app network(PAN) for each user by uid
def create_pan(uid):
    graph = Graph()
    records = []
    edges = {}

    for r in getUsageRecords().find({'userID': uid}):
        records.append(r)

    for i in xrange(len(records)):
        app1, end1 = map_name(records[i]['appName']), records[i]['endTime']
        if not end1: continue
        edges.setdefault(app1, set([]))

        for j in xrange(i + 1, len(records)):
            app2, start2 = map_name(records[j]['appName']), records[j]['startTime']
            if app1 == app2 or not start2: continue
            try:
                t1, t2 = [makeTime(t) for t in [end1, start2]]
                if t2 < t1 or t2 - t1 < 30:
                    edges[app1].add(app2)
            except:
                continue

    store_network(edges, PAN_TXT % uid)
    graph.add_edges(edges)
    graph.draw(PAN_JPG % uid)


# test how many app in PAN covered by GAN
def cover_test(uid):
    gan = load_gan()[0]
    pan = load_pan(uid)[0]

    print len(pan)

if __name__ == '__main__':
    for uid in USER_IDS:
        create_pan(uid)
    # cover_test('F01')
    # for app in load_apps():
    #     if u'美团团购' == app: print app
