import time
from igraph import *
from itertools import combinations


DATE_PATTERN = r'%Y/%m/%d %H:%M'
GRAPH_PATH = '%s.pickle'
INTERVAL = 30 * 60


def maketime(s):
    return time.mktime(time.strptime(s, DATE_PATTERN))


# create graph from usages records
def create(uid):
    records, sessions = [], []
    f = file('usages.csv')
    for line in f.readlines():
        temp = line.split(',')
        if temp[7].strip() == uid:
            records.append([maketime(temp[0]), temp[1]])
    records = sorted(records, key=lambda x: x[0])

    apps = set([])
    session = []
    prev = records[0][0]
    for record in records:
        if record[0] - prev < INTERVAL:
            session.append(record[1])
        else:
            sessions.append(session)
            session = [record[1]]
        prev = record[0]
        apps.add(record[1])

    if session:
        sessions.append(session)

    g = Graph()
    g.add_vertices(list(apps))
    g.vs['weight'] = [0 for i in xrange(len(g.vs))]

    for session in sessions:
        temp = set(session)

        for app in temp:
            g.vs.find(name=app)['weight'] += 1

        for f, t in combinations(temp, 2):
            try:
                g.es[g.get_eid(f, t)]['weight'] += 1
            except:
                g.add_edge(f, t)
                g.es[g.get_eid(f, t)]['weight'] = 1

    g.vs['label'] = g.vs['name']
    g.vs['size'] = g.vs['weight']
    g.es['label'] = g.es['weight']
    g.es['width'] = g.es['weight']

    g.save(GRAPH_PATH % uid)


# plot(g, bbox=(1000, 1000))


# compute similarity of g1 and g2
def sim(g1, g2):
    mnodes = max(len(g1.vs), len(g2.vs))
    mcs = 0

    for edge in g1.get_edgelist():
        fn, tn = [g1.vs[i]['name'] for i in edge]
        try:
            eid1, eid2 = [g.get_eid(fn, tn) for g in g1, g2]
            mcs += g1.es[eid1]['weight'] + g2.es[eid2]['weight']
        except:
            pass

    return mcs * 1.0 / mnodes


# use u2 to recommend for u1
def recommend(u1, u2):
    result = {}

    g1, g2 = [load(GRAPH_PATH % u) for u in u1, u2]
    apps1, apps2 = [g.vs['name'] for g in g1, g2]
    apps = set(apps1) & set(apps2)
    if not apps:
        return []

    s = sim(g1, g2)
    if not s:
        return []

    for app in apps:
        for neighbor in g2.neighbors(app):
            nname = g2.vs[neighbor]['name']
            if nname not in apps1:
                result.setdefault(nname, 0)
                result[nname] += s * g2.es[g2.get_eid(app, nname)]['weight']

    return result


# get topk from result
def topk(result, k):
    temp = []
    for app, fitness in result.iteritems():
        temp.append([app, fitness])

    return sorted(temp, key=lambda x: x[1], reverse=True)[:k]


if __name__ == '__main__':
    for app, fitness in topk(recommend('1001', '1002'), 10):
        print app, fitness
