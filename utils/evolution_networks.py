# -*- coding: utf-8 -*-

from itertools import combinations
from collections import defaultdict

from utils.parser_apk import *
from utils.gan_rels_intent import *


def date_distribution():
    # first_date = []
    # for app in load_eapps():
    #     version_date = get_version_date(app)
    #     versions = sorted([int(v) for v in version_date])
    #     first_date.append(version_date[str(versions[0])])

    # print sorted(first_date, key=lambda t: maketime(t))

    dates = []
    for year in xrange(2009, 2016):
        for month in ['1', '7']:
            dates.append('-'.join([str(year), month, '1']))
    dates.extend(['2016-1-1', '2016-7-1'])

    xlabels = [date[2:-2] for date in dates]

    count = 0
    for app in load_eapps():
        version_date = get_version_date(app)
        versions = sorted([int(v) for v in version_date])

        x = []
        for v in versions:
            t = version_date[str(v)]
            x.append(maketime(t))

        y = [count for i in xrange(len(versions))]
        count += 1

        plt.plot(x, y, 'r-', linewidth=4)

    plt.grid()
    plt.xticks([maketime(t) for t in dates], xlabels)
    plt.savefig(FIGURE_PATH % 'version_date', format='pdf')
    plt.show()


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


def get_points(start, end):

    points = []
    for year in xrange(2012, 2017):
        for month in xrange(1, 13):
            points.append('-'.join([str(year), str(month), '1']))

    return filter(
        lambda t: maketime(start) <= maketime(t) <= maketime(end),
        points
    )


def network_create(points):

    for point in points:

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


def get_commons(points):
    apps = []
    for point in points:
        network = pickle_load(NETWORK_PATH % point)
        apps.append(network.nodes())

    return reduce(lambda a, b: set(a) & set(b), apps)


def scale_stats(points):

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
    # plt.xticks(
    #     xrange(0, len(points), 2),
    #     [points[i][2:-2] for i in xrange(0, len(points), 2)]
    # )
    plt.savefig(FIGURE_PATH % 'scale_stats_common', format='pdf')
    plt.show()


def get_matches(points):

    point_apps = {}
    common_apps = get_commons(points)
    matches, m_intents, m_filters = {}, [], []

    for point in points:
        match = defaultdict(list)
        network = pickle_load(NETWORK_PATH % point).subgraph(common_apps)
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

    return matches, m_intents, m_filters, point_apps


def intent_evolution(points):

    matches, m_intents, m_filters, point_apps = get_matches(points)

    # data = []
    # for point in points:
    #     temp = []
    #     apps = point_apps[point]
    #     for app in apps:
    #         temp.append(np.array([1 if i in get_intents(*app)[1] else 0 for i in m_intents]))
    #         temp.append(np.array([1 if i in get_filters(*app)[0] else 0 for i in m_filters]))
    #     data.append(reduce(lambda a, b: a + b, temp))
    #
    # heat_map(map(list, zip(*data)), 'Time Line (2015.1~2015.12)', 'Intent Labels', 'Intent_evolution')
    # heat_map(map(list, zip(*data)), 'Time Line (2015.1~2015.12)', 'Filter Labels', 'filter_evolution')

    # find intents and filters that exist all the time
    intent_count = [[0 for j in xrange(len(points))] for i in xrange(len(m_intents))]
    filter_count = [[0 for j in xrange(len(points))] for i in xrange(len(m_filters))]

    for index in xrange(len(points)):
        for app in point_apps[points[index]]:
            for i in xrange(len(m_intents)):
                if m_intents[i] in get_intents(*app)[1]:
                    intent_count[i][index] += 1
            for i in xrange(len(m_filters)):
                if m_filters[i] in get_filters(*app)[0]:
                    filter_count[i][index] += 1

    m_intents = filter(lambda i: all(intent_count[m_intents.index(i)]), m_intents)
    m_filters = filter(lambda f: all(filter_count[m_filters.index(f)]), m_filters)

    # evolution analysis for stable intents and filters
    intent_data = [[set([]) for j in xrange(len(points))] for i in xrange(len(m_intents))]
    filter_data = [[set([]) for j in xrange(len(points))] for i in xrange(len(m_filters))]

    for index in xrange(len(points)):
        for e, t in matches[points[index]].items():
            [intent_data[m_intents.index(i)][index].add(e[1]) for i, f in t if i in m_intents]
            [filter_data[m_filters.index(f)][index].add(e[0]) for i, f in t if f in m_filters]

    intent_data = [[len(intent_data[i][j]) for j in xrange(len(points))] for i in xrange(len(m_intents))]
    filter_data = [[len(filter_data[i][j]) for j in xrange(len(points))] for i in xrange(len(m_filters))]

    heat_map(intent_data, 'Time Line (2015.1~2015.12)', 'Intent Labels', 'intent_evolution')
    heat_map(filter_data, 'Time Line (2015.1~2015.12)', 'Filter Labels', 'filter_evolution')

    # print '> intent:'
    # for i in xrange(len(intent_data)):
    #     print intent_data[i], m_intents[i]
    #
    # print '> filter:'
    # for i in xrange(len(filter_data)):
    #     print filter_data[i], m_filters[i]


if __name__ == '__main__':
    # date_distribution()
    points = get_points('2015-1-1', '2015-12-1')
    # network_create(points)
    # scale_stats(points)
    # intent_evolution(points)
    network = pickle_load(NETWORK_PATH % '2015-12-1')
    print network.number_of_nodes(), network.number_of_edges()
    degree_rank = []
    idict, odict = network.in_degree(), network.out_degree()
    for app in network.nodes():
        degree_rank.append((app, idict[app] + odict[app]))
    degree_rank = sorted(degree_rank, key=lambda x: x[1], reverse=True)
    print degree_rank
