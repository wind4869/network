# -*- coding: utf-8 -*-

import igraph as ig
import matplotlib.pyplot as plt
from BeautifulSoup import BeautifulSoup

from utils.parser_apk import *


def unique(c):
    return reduce(lambda a, b: a if b in a else a + [b], [[], ] + c)


def get_components_each(app, v):
    components = list(get_intents(app, v))
    components.append(get_filters(app, v)[0])
    return components


def get_components_all(app):

    eintents, iintents, filters = [], [], []

    for v in VERSIONS[app]:
        components = get_components_each(app, v)

        eintents.extend(components[COMPONENT.E_INTENT])
        iintents.extend(components[COMPONENT.I_INTENT])
        filters.extend(components[COMPONENT.I_FILTER])

    return [unique(c) for c in [eintents, iintents, filters]]


def get_data(app, ctype, direction=DIRECTION.VERSION):

    data = []
    components_all = get_components_all(app)[ctype]

    for v in VERSIONS[app]:
        components = get_components_each(app, v)[ctype]
        if not components:
            continue

        data.append([1 if i in components else 0 for i in components_all])

    if direction == DIRECTION.COMPONENT:
        return map(list, zip(*data))
    elif direction == DIRECTION.VERSION:
        return data


def existence_type(v):
    length = len(v)
    if v[-1] == 0:
        return EXISTENCE.DISAPPEAR
    elif sum(v) == length:
        return EXISTENCE.ENTIRE
    else:
        start = 0
        while True:
            if v[start] == 1:
                break
            start += 1
        if sum(v) == length - start:
            return EXISTENCE.PERSIST
        else:
            return EXISTENCE.INTERRUPT


def existence_test(app, ctype):

    result = {}
    data = get_data(app, ctype, DIRECTION.COMPONENT)

    for v in data:
        t = existence_type(v)
        result.setdefault(t, 0)
        result[t] += 1

    print result


def cover_test(app, ctype):
    result = []
    data = get_data(app, ctype, DIRECTION.COMPONENT)
    length = len(data[0])

    for v in data:

        start = 0
        while True:
            if v[start] == 1:
                break
            start += 1
        end = length - 1
        while True:
            if v[end] == 1:
                break
            end -= 1

        result.append(
            (sum(v) / float(length), sum(v) / float(end - start + 1))
        )

    yp, yc = [], []
    x = xrange(len(data))

    for t in sorted(result, key=lambda x: x[0]):
        yp.append(t[0])
        yc.append(t[1])

    plt.plot(x, yp, 'ro-')
    plt.plot(x, yc, 'bs-')
    plt.show()


def version_test(app, ctype):
    y = []
    data = get_data(app, ctype)
    for i in xrange(1, len(data)):
        y.append(sim_cosine(data[i - 1], data[i]))

    x = xrange(len(data) - 1)
    plt.plot(x, y, 'ro-')
    plt.show()


def get_part(t1=100, t2=700):
    gan = load_gan()

    c0 = set([])
    for u, v in gan.edges():
        if gan[u][v]['weights'][INDEX.E_INTENT] or gan[u][v]['weights'][INDEX.I_INTENT]:
            [c0.add(i) for i in u, v]
        else:
            gan.remove_edge(u, v)

    # c1 = set([])
    # for app in c0:
    #     if url_exists('http://apk.hiapk.com/appinfo/' + app):
    #         c1.append(app)

    # apps = load_content(APPSC1_TXT)
    # gan = gan.subgraph(apps)
    #
    # degree_rank = []
    # idict, odict = gan.in_degree(), gan.out_degree()
    # for app in apps:
    #     degree_rank.append((app, idict[app] + odict[app]))
    # degree_rank = sorted(degree_rank, key=lambda x: x[1], reverse=True)
    #
    # download_rank = []
    # for app in load_capps():
    #     download_rank.append((app, downloadCount(app)))
    # download_rank = sorted(download_rank, key=lambda x: x[1], reverse=True)
    #
    # c2 = set([x[0] for x in degree_rank][:t1]) & \
    #      set([x[0] for x in download_rank][:t2])
    #
    # # store c2 to txt file
    # f = open(APPSC2_TXT, 'w')
    # for app in c2:
    #     f.write(app + '\n')
    # f.close()

    apps = load_content(APPSC2_TXT)
    gan = gan.subgraph(apps)

    print gan.number_of_nodes(), gan.number_of_edges()

    elist = []
    for e in gan.edges():
        u, v = e
        weights = gan[u][v]['weights']
        we, wi = weights[INDEX.E_INTENT], weights[INDEX.I_INTENT]
        w = we if we else wi
        elist.append((u, v, w))

    # write networkx to file
    part = nx.DiGraph()
    part.add_weighted_edges_from(elist)
    nx.write_graphml(part, GRAPHML_PATH)

    # read file to construct igraph
    graph = ig.Graph.Read_GraphML(GRAPHML_PATH)
    graph.vs['size'] = [15 for i in xrange(len(graph.vs))]

    # draw the graph
    ig.plot(graph, bbox=(2400, 1400))

    return part

if __name__ == '__main__':
    # app = APPS[1]
    # existence_test(app, COMPONENT.I_INTENT)
    # cover_test(app, COMPONENT.I_INTENT)
    # version_test(app, COMPONENT.I_INTENT)
    # print len(get_components_all(app)[1])
    gan = get_part()
    for u, v in gan.edges():
        print gan[u][v]['weight'], u, v
