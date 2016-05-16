# -*- coding: utf-8 -*-

from itertools import combinations
from collections import defaultdict

from utils.lan_stats import *
from utils.parser_apk import *
from utils.gan_rels_intent import *


def intent_match(app_from, app_to):

    explicits, implicits = get_intents(*app_from)
    filters = get_filters(*app_to)[0]

    weight = 0
    if explicits:
        pattern = re.compile('^' + app_to[0].replace('.', '\.'))
        for intent in explicits:
            if pattern.match(intent):
                weight += 2
                break

    if implicits and filters:
        for i in implicits:
            for f in filters:
                if implicit_match_one(i, f):
                    weight += 1
                    return weight

    return weight


def network_create():

    for point in get_points('2012-1-1', '2016-3-1'):

        print '> ' + point

        apps = []
        t = maketime(point)

        for app in load_eapps():
            version_date = get_version_date(app)
            versions = sorted([int(v) for v in version_date])

            prev = -1
            for v in versions:
                if maketime(version_date[str(v)]) > t or v == versions[-1]:
                    if prev != -1:
                        apps.append((app, prev))
                    break
                prev = v

        network = nx.DiGraph()
        network.add_nodes_from([t[0] for t in apps])

        for app_pair in combinations(apps, 2):
            for i in xrange(2):
                app_from, app_to = app_pair[i], app_pair[1 - i]
                w = intent_match(app_from, app_to)
                if w:
                    network.add_edge(app_from[0], app_to[0], weight=w)

        for app in apps:
            n, v = app
            if network.has_node(n):
                network.node[n]['version'] = v

        pickle_dump(network, NETWORK_PATH % point)


def version_distribution():

    # first_date = []
    # for app in load_eapps():
    #     version_date = get_version_date(app)
    #     versions = sorted([int(v) for v in version_date])
    #     first_date.append(version_date[str(versions[0])])

    # print sorted(first_date, key=lambda t: maketime(t))

    apps = load_eapps()
    points = get_points('2009-1-1', '2016-3-1')
    xlabels = [str(y) for y in xrange(2009, 2017)]
    plt.figure(figsize=(16, 9))

    ylabels1 = [
        'WeChat', 'Alipay', 'Taobao', 'QQi', 'QuickPic', 'Chrome', 'MTGif', 'Maxthon', 'UCMobile', 'Facebook',
        'BOCMobile', 'SogouInput', 'JustPiano', 'BaiduNavi', 'Baozoumanhua', 'LizhiFM', 'Fyzb3', 'Oupeng', 'SinaWeibo', 'AdobeReader',
        'Twitter', 'BankComm', 'OfficeSuite', 'SogouMap', 'ICBCMobile', 'QQ', 'Meituan', 'Hao123', 'QQmail', 'Dayima',
        'BaiduInput', 'Sledog', 'BaiduBrowser', 'CleanMaster', 'Youni', 'QQlite', 'BaiduMap', 'UCHD', 'Ucamera', 'CTClient',
        'MeituPic', 'SFReader', 'AppSearch', 'BloveStorm', 'ESFile', 'Editor', 'Zaker', 'PPTVHD', 'When', 'PPlive'
    ]

    ylabels2 = []
    for app in apps:
        ylabels2.append(len(get_versions(app)))

    ylabels = ['%s(%d)' % x for x in zip(ylabels1, ylabels2)]

    temp, apps = parallel_sort(ylabels2, apps)
    ylabels2, ylabels = parallel_sort(ylabels2, ylabels)

    count = 0
    for app in apps:
        version_date = get_version_date(app)
        versions = sorted([int(v) for v in version_date])

        x = []
        for v in versions:
            t = version_date[str(v)]
            x.append(maketime(t))

        y = [count for i in xrange(len(versions))]
        count += 1

        plt.plot(x, y, 'r-', linewidth=5)

    plt.grid()
    plt.xticks([maketime(y + '-1-1') for y in xlabels], xlabels)
    plt.yticks(xrange(len(apps)), ylabels)

    plt.xlabel('Time Line (2009.1~2016.3)')

    plt.savefig(FIGURE_PATH % 'version_distribution', format='pdf')
    plt.show()


def scale_and_density():

    points = get_points('2012-1-1', '2016-3-1')

    x = xrange(len(points))
    yn, ye, yd = [], [], []

    for point in points:
        network = pickle_load(NETWORK_PATH % point)
        n, e = network.number_of_nodes(), network.number_of_edges()
        yn.append(n)
        ye.append(e)
        yd.append(float(e) / (n * n))

    f, (ax1, ax2, ax3) = plt.subplots(3, 1, sharex=True)

    plt.xticks(xrange(0, 49, 12), [str(y) for y in xrange(2012, 2017)])

    ax1.plot(x, yn, 'ro-', label='Number of Nodes')
    ax2.plot(x, ye, 'go-', label='Number of Edges')
    ax3.plot(x, yd, 'bo-', label='Density')

    ax1.grid()
    ax2.grid()
    ax3.grid()

    ax1.legend(loc=0)
    ax2.legend(loc=0)
    ax3.legend(loc=0)

    plt.xlabel('Time Line (2012.1~2016.3)')
    plt.savefig(FIGURE_PATH % 'scale_and_density', format='pdf')
    plt.show()


def distribution_quality_test():

    points = get_points('2015-1-1', '2015-12-1')
    common_apps = get_commons(points)

    x = xrange(len(points))
    yi, yo = [], []

    for p in points:
        i, o = power_law_distribution(pickle_load(NETWORK_PATH % p).subgraph(common_apps))
        yi.append(-i)
        yo.append(-o)

    plt.plot(x, yi, 'ro-', label='In Degree')
    plt.plot(x, yo, 'bs-', label='Out Degree')

    plt.xlabel('Time Line (2015.1~2015.12)')
    plt.ylabel('Distribution Quality')

    plt.grid()
    plt.legend(loc=0)
    # plt.xticks(xrange(0, 49, 12), [str(y) for y in xrange(2012, 2017)])

    plt.savefig(FIGURE_PATH % 'distribution_quality', format='pdf')
    plt.show()


def community_each(gan):
    graph = ig.Graph(directed=True)
    graph.add_vertices(load_apps())

    elist = []
    for e in gan.edges():
        u, v = e
        w = float(gan[u][v]['weight'])
        elist.append((u, v, w))

    # write networkx to file
    graph = nx.DiGraph()
    graph.add_weighted_edges_from(elist)
    nx.write_graphml(graph, GRAPHML_PATH)

    # read file to construct igraph
    graph = ig.Graph.Read_GraphML(GRAPHML_PATH)
    graph.vs['size'] = [10 for i in xrange(len(graph.vs))]

    clusters = graph.community_spinglass()
    membership = clusters.membership
    vc = ig.VertexClustering(graph, membership)

    print vc

    result = []
    for c in vc:
        result.append(set([graph.vs[i]['id'] for i in c]))

    ig.plot(vc, bbox=(2400, 1400))
    return result, clusters.modularity


def community_test():

    result = []

    points = get_points('2015-1-1', '2015-12-1')
    common_apps = get_commons(points)

    for p in points:
        result.append(community_each(pickle_load(NETWORK_PATH % p).subgraph(common_apps))[0])

    for r in result:
        print len(r)


def get_commons(points):
    apps = []
    for point in points:
        network = pickle_load(NETWORK_PATH % point)
        apps.append(network.nodes())

    return reduce(lambda a, b: set(a) & set(b), apps)


def scale_stats_common(points):

    x = xrange(len(points))
    yn, ye = [], []

    edges = []
    common_apps = get_commons(points)

    for point in points:
        network = pickle_load(NETWORK_PATH % point).subgraph(common_apps)
        n, e = network.number_of_nodes(), network.number_of_edges()
        edges.append(network.edges())
        yn.append(n)
        ye.append(e)

    x = xrange(len(edges))
    ya, yr = [0], [0]
    for i in xrange(1, len(edges)):
        cur, prev = set(edges[i]), set(edges[i - 1])
        added_edges, removed_edges = cur - prev, prev - cur

        print 'add(%d)' % len(added_edges), added_edges
        print 'rem(%d)' % len(removed_edges), removed_edges

        ya.append(len(added_edges))
        yr.append(len(removed_edges))

    plt.plot(x, ye, 'ro-')
    plt.plot(x, ya, 'bs-')
    plt.plot(x, yr, 'ys-')

    plt.xticks(x, [date[2:-2] for date in points])
    plt.savefig(FIGURE_PATH % 'scale_stats_common', format='pdf')
    plt.show()


def get_matches(points, common=False):

    point_apps = {}
    common_apps = get_commons(points)
    matches, m_intents, m_filters = {}, [], []

    for point in points:
        match = defaultdict(list)
        network = pickle_load(NETWORK_PATH % point)
        if common:
            network = network.subgraph(common_apps)
        point_apps[point] = [(app, network.node[app]['version']) for app in network.nodes()]

        for app_from, app_to in network.edges():
            intents = get_intents(app_from, network.node[app_from]['version'])[1]
            filters = get_filters(app_to, network.node[app_to]['version'])[0]
            for i in intents:
                for f in filters:
                    if implicit_match_one(i, f):
                        match[(app_from, app_to)].append((i, f))
                        if i not in m_intents:
                            m_intents.append(i)
                        if f not in m_filters:
                            m_filters.append(f)

        matches[point] = match

    # data = []
    # for i in m_intents:
    #     data.append([1 if implicit_match_one(i, f) else 0 for f in m_filters])
    #
    # heat_map_intent(data, 'match_result')

    return matches, m_intents, m_filters, point_apps


def intent_cover_test(points, common=False):

    matches, m_intents, m_filters, point_apps = get_matches(points, common)

    # intent_count = [[0 for j in xrange(len(points))] for i in xrange(len(m_intents))]
    # filter_count = [[0 for j in xrange(len(points))] for i in xrange(len(m_filters))]
    #
    # for index in xrange(len(points)):
    #
    #     print '>', index
    #
    #     for app in point_apps[points[index]]:
    #         for i in xrange(len(m_intents)):
    #             if m_intents[i] in get_intents(*app)[1]:
    #                 intent_count[i][index] += 1
    #         for i in xrange(len(m_filters)):
    #             if m_filters[i] in get_filters(*app)[0]:
    #                 filter_count[i][index] += 1

    # pickle_dump(intent_count, FIGURE_DIR + 'intent_count.pickle')
    # pickle_dump(filter_count, FIGURE_DIR + 'filter_count.pickle')

    intent_count = pickle_load(FIGURE_DIR + 'intent_count.pickle')
    # filter_count = pickle_load(FIGURE_DIR + 'filter_count.pickle')

    heat_map_intent(intent_count, 'intent_cover')
    # heat_map(intent_count, 'Time Line (2015.1~2015.12)', 'Intent Labels', 'intent_cover')
    # heat_map(filter_count, 'Time Line (2015.1~2015.12)', 'Filter Labels', 'filter_cover')


def intent_match_test(points, common=False):

    matches, m_intents, m_filters, point_apps = get_matches(points, common)

    intent_data = [[set([]) for j in xrange(len(points))] for i in xrange(len(m_intents))]
    filter_data = [[set([]) for j in xrange(len(points))] for i in xrange(len(m_filters))]

    for index in xrange(len(points)):
        for e, t in matches[points[index]].items():
            [intent_data[m_intents.index(i)][index].add(e[1]) for i, f in t if i in m_intents]
            [filter_data[m_filters.index(f)][index].add(e[0]) for i, f in t if f in m_filters]

    intent_data = [[len(intent_data[i][j]) for j in xrange(len(points))] for i in xrange(len(m_intents))]
    filter_data = [[len(filter_data[i][j]) for j in xrange(len(points))] for i in xrange(len(m_filters))]

    heat_map_intent(intent_data, 'intent_match')
    # heat_map(intent_data, 'Time Line (2015.1~2015.12)', 'Intent Labels', 'intent_match')
    # heat_map(filter_data, 'Time Line (2015.1~2015.12)', 'Filter Labels', 'filter_match')


def heat_map_intent(data, fname):

    # yticks = [
    #     'VIEW application/pdf', 'VIEW www.sogou.com', 'SEND text/plain', 'VIEW sinaweibo://shake', 'VIEW nearbypeople',
    #     'VIEW http://www.', 'VIEW alipaydt', 'SEND image/*', 'SEND text/*', 'VIEW http://', 'VIEW m.baidu.com',
    #     'VIEW text/html', 'SEND image/jpeg', 'GET_CONTENT */*', 'VIEW application/apk'
    # ]

    yticks = [
        'VIEW text/html', 'SEND text/plain', 'VIEW http://', 'VIEW sinaweibo://shake', 'VIEW nearbypeople',
        'VIEW application/pdf', 'VIEW nearbyweibo', 'SEND image/*', 'SEND text/*', 'VIEW wap.uc.cn',
        'VIEW wap.ucweb.com', 'VIEW www.sogou.com', 'VIEW http://www.', 'SEND image/jpeg', 'VIEW alipaydt',
        'VIEW m.baidu.com', 'GET_CONTENT */*', 'VIEW weixin.qq.com', 'VIEW wap.amap.com', 'VIEW www.google.com',
        'VIEW image/*', 'GET_CONTENT image/*', 'VIEW www.lizhi.fm', 'VIEW www.google.com', 'VIEW www.cmcm.com',
        'VIEW application/apk'
    ]

    plt.figure(figsize=(16, 9))
    im = plt.imshow(data, cmap=plt.cm.Greys, interpolation='nearest')

    plt.xticks(xrange(len(data[0])))
    plt.xticks(xrange(0, 49, 12), [str(y) for y in xrange(2012, 2017)])
    # plt.yticks(xrange(len(data)), yticks)

    plt.xlabel('Time Line (2015.1~2015.12)')
    plt.ylabel('Intents')

    plt.grid()
    plt.colorbar(im, orientation='horizontal')

    plt.savefig(FIGURE_PATH % fname, format='pdf')
    # plt.show()


if __name__ == '__main__':

    # version_distribution()
    # network_create()
    scale_and_density()
    # distribution_quality_test()
    # community_test()

    # points = get_points('2012-1-1', '2016-3-1')
    # points = get_points('2015-1-1', '2015-12-1')
    # matches, m_intents, m_filters, point_apps = get_matches(points)

    # scale_stats_common(points)
    # intent_cover_test(points)
    # intent_match_test(points)
