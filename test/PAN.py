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


# get the apps in the network
def app_in_network(network):
    apps = set([])
    for app_from, app_tos in network.iteritems():
        apps.add(app_from)
        for app_to in app_tos:
            apps.add(app_to)
    return apps


# filter the network to get the common part between pan and gan
def filter_network(network, apps_in_common):
    new_network = {}
    for app_from, app_tos in network.iteritems():
        if app_from in apps_in_common:
            new_network[app_from] = set([])
            for app_to in app_tos:
                if app_to in apps_in_common:
                    new_network[app_from].add(app_to)
    return new_network


def draw(edges, path):
    graph = Graph()
    graph.add_edges(edges)
    graph.draw(path)


# test how many app in PAN covered by GAN
def cover_test(uid):
    gan = load_gan()
    pan = load_pan(uid)

    print '\n'.join([app for app in app_in_network(pan) if app not in app_in_network(gan)])
    # apps_in_common = app_in_network(gan) & app_in_network(pan)
    # gan = filter_network(gan, apps_in_common)
    # pan = filter_network(pan, apps_in_common)

    # draw(gan, 'gan.jpg')
    # draw(pan, 'pan.jpg')


if __name__ == '__main__':
    # for uid in USER_IDS:
    create_pan('F02')
    # cover_test('F02')
