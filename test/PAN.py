import time
from utils.graph import *
from utils.network_rs import *


def makeTime(strTime):
    return time.mktime(time.strptime(strTime, DATE_PATTERN))


def create_pan(uid):
    graph = Graph()
    records = []
    edges = {}

    for r in getUsageRecords().find({'userID': uid}):
        records.append(r)

    for i in xrange(len(records)):
        app1, end1 = records[i]['appName'], records[i]['endTime']
        if not end1: continue
        edges.setdefault(app1, set([]))

        for j in xrange(i + 1, len(records)):
            app2, start2 = records[j]['appName'], records[j]['startTime']
            if app1 == app2 or not start2: continue
            try:
                t1, t2 = [makeTime(t) for t in [end1, start2]]
                if t2 < t1 or t2 - t1 < 30:
                    edges[app1].add(app2)
            except:
                continue

    store_network(edges, PICKLE_PATH % uid)
    graph.add_edges(edges)
    graph.draw(GRAPH_PATH % uid)


if __name__ == '__main__':
    for uid in USER_IDS:
        if uid != 'F02':
            create_pan(uid)