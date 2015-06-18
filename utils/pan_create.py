import time
from utils.class_graph import *
from utils.funcs_stats import *
from utils.funcs_rw import *

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


# get usages edges for each user by uid
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
    # graph.draw(USAGE_JPG % uid)


# create pans by uid
def create_pan(uid):
    gan = load_gan()
    usage_edges = load_usage_edges(uid)

    all_apps = load_all_apps()
    app_in_usage = apps_in_network(usage_edges)
    apps_in_common = app_in_usage & set(all_apps)

    sub_gan = filter_network(gan, apps_in_common)
    pan = filter_network(usage_edges, apps_in_common)
    merge_edges(pan, sub_gan)

    dump_network(pan, PAN_TXT % uid)


if __name__ == '__main__':
    for uid in USER_IDS:
        create_pan(uid)
