# -*- coding: utf-8 -*-

import time
from utils.graph import *
from utils.stat_funcs import *
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


# get usage edges for each user by uid
def get_usage_edges(uid):
    graph = Graph()
    records = []
    usage_edges = {}

    for r in getUsageRecords().find({'userID': uid}):
        records.append(r)

    for i in xrange(len(records)):
        app1, end1 = map_name(records[i]['appName']), records[i]['endTime']
        if not end1: continue
        usage_edges.setdefault(app1, set([]))

        for j in xrange(i + 1, len(records)):
            app2, start2 = map_name(records[j]['appName']), records[j]['startTime']
            if app1 == app2 or not start2: continue
            try:
                t1, t2 = [makeTime(t) for t in [end1, start2]]
                if t2 < t1 or t2 - t1 < 30:
                    usage_edges[app1].add(app2)
            except:
                continue

    dump_network(usage_edges, USAGE_TXT % uid)
    graph.add_edges(usage_edges)
    graph.draw(USAGE_JPG % uid)


def pan_gan_test(pan_diff_gan):
    natives = load_natives()
    a = edges_count(pan_diff_gan)
    count_from_native = 0
    for app in pan_diff_gan:
        if app in natives:
            count_from_native += len(pan_diff_gan[app])
    b = count_from_native
    # print a, b, b * 1.0 / a

    in_degrees = {}
    app_in_this = apps_in_network(pan_diff_gan)
    [in_degrees.setdefault(app, 0) for app in app_in_this]
    for app in pan_diff_gan:
        for app_to in pan_diff_gan[app]:
            in_degrees[app_to] += 1

    in_degrees_list = []
    for key, value in in_degrees.iteritems():
        in_degrees_list.append((key, value))
    in_degrees_list.sort(lambda a, b: a[1] - b[1])

    for app, in_degree in in_degrees_list[-5:]:
        print app, in_degree


# test PAN and GAN
def cover_test(uid):
    print ' - Test of user <%s> - ' % uid

    gan = load_gan()
    usage_edges = load_usage_edges(uid)

    all_apps = loaa_all_apps()
    app_in_usage = apps_in_network(usage_edges)
    apps_ingored = app_in_usage - set(all_apps)
    apps_in_common = app_in_usage & set(all_apps)

    sub_gan = filter_network(gan, apps_in_common)
    pan = filter_network(usage_edges, apps_in_common)
    merge_edges(pan, sub_gan)

    # pickle.dump(pan, open(PAN_TXT % uid, 'w'))

    # the ingored ratio:
    # (apps in pan but not in all_apps) / (apps in pan)
    n_igored, n_usage = len(apps_ingored), len(app_in_usage)
    print '<1> Ignored Ratio is: %.3f (%d / %d)' % (n_igored * 1.0 / n_usage, n_igored, n_usage)

    gan_diff_pan = edges_diff(gan, pan)
    pan_diff_gan = edges_diff(pan, gan)
    edges_in_common = edges_common(pan, gan)

    pan_gan_test(edges_diff(pan, gan))

    # gan common ratio
    a, b, c = edges_count(edges_in_common), edges_count(gan), edges_count(pan)
    print '<2> GAN Common Ratio: %.3f (%d / %d)' % \
          (a * 1.0 / b, a, b)
    # pan common ratio
    print '<3> PAN Common Ratio: %.3f (%d / %d)' % \
          (a * 1.0 / c, a, c)


def component_test(network):
    counts = [0 for i in xrange(5)]
    gans = [load_gan(i) for i in (1, 2, 4, 8, 16)]

    for app in network:
        for app_to in network[app]:
            for i in xrange(5):
                if app in gans[i] and app_to in gans[i][app]:
                    counts[i] += 1
    print counts, edges_count(network), counts[3] * 1.0 / edges_count(network)


def pan_contrast():
    apps = load_apps()
    natives = set(load_natives())
    pans = [pickle.load(open(PAN_TXT % uid)) for uid in USER_IDS]

    apps_in_pans = [apps_in_network(pan) for pan in pans]
    natives_in_pans = [natives & i for i in apps_in_pans]
    others_in_pans = [i - natives for i in apps_in_pans]

    print [len(i) for i in apps_in_pans]
    print [len(i) for i in natives_in_pans]
    print [len(i) for i in others_in_pans]

    for k in xrange(6):
        in_degrees = {}
        [in_degrees.setdefault(i, 0) for i in others_in_pans[k]]
        for app in pans[k]:
            for app_to in pans[k][app]:
                if app_to in others_in_pans[k]:
                    in_degrees[app_to] += 1

        x, y = [], []
        for app in in_degrees:
            x.append(in_degrees[app])
            y.append(likesCount(app))
            # y.append(apps.index(app))
        draw_plot(x, y, '', '', '', 'ro')
        print linregress(x, y)

    print [[apps.index(i) for i in j] for j in others_in_pans]
    print '\n'.join(reduce(lambda a, b: a & b, apps_in_pans))


if __name__ == '__main__':
    # for uid in USER_IDS:
    # create_pan(uid)
    #     cover_test(uid)
    pan_contrast()