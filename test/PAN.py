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


# get edges in set a but not in set b
def edges_diff(a, b):
    result = {}
    diff_keys = [k for k in a.keys() if k not in b.keys()]
    for k in a:
        tmp = set([]) if k in diff_keys else b[k]
        result[k] = a[k] - tmp
    return result


# get edges both in set a and set b
def edges_common(a, b):
    result = {}
    common_keys = [k for k in a.keys() if k in b.keys()]
    for k in common_keys:
        result[k] = a[k] & b[k]
    return result


# count the number of edges in set a
def edges_count(a):
    result = 0
    for key in a:
        result += len(a[key])
    return result


def draw(edges, path):
    graph = Graph()
    graph.add_edges(edges)
    graph.draw(path)


# test PAN and GAN
def cover_test(uid):
    print ' - Test of user <%s> - ' % uid

    gan = load_gan()
    pan = load_pan(uid)

    all_apps = loaa_all_apps()
    app_in_pan = app_in_network(pan)
    apps_ingored = app_in_pan - set(all_apps)
    apps_in_common = app_in_pan & set(all_apps)

    new_gan = filter_network(gan, apps_in_common)
    new_pan = filter_network(pan, apps_in_common)

    # the ingored ratio:
    # (apps in pan but not in all_apps) / (apps in pan)
    ingored_ratio = len(apps_ingored) * 1.0 / len(app_in_pan)
    print '<1> Ignored Ration is: %.2f' % ingored_ratio

    gan_diff_pan = edges_diff(new_gan, new_pan)
    pan_diff_gan = edges_diff(new_pan, new_gan)
    edges_in_common = edges_common(new_pan, new_gan)

    # gan common ratio
    print '<2> GAN Common Ratio: %.2f' % \
          (edges_count(edges_in_common) * 1.0 / edges_count(new_gan))
    # pan common ratio
    print '<3> PAN Common Ratio: %.2f' % \
          (edges_count(edges_in_common) * 1.0 / edges_count(new_pan))

    # draw, draw, draw ...
    draw(new_gan, GAN % uid)
    draw(new_pan, PAN % uid)
    draw(edges_in_common, COMMON % uid)
    draw(gan_diff_pan, GAN_DIFF_PAN % uid)
    draw(pan_diff_gan, PAN_DIFF_GAN % uid)


if __name__ == '__main__':
    pass
    # for uid in USER_IDS:
    # create_pan(uid)
    # cover_test(uid)
