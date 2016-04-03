# -*- coding: utf-8 -*-

from itertools import combinations

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
    for year in ['2009', '2010', '2011', '2012', '2013', '2014', '2015']:
        for month in ['1', '7']:
            dates.append('-'.join([year, month, '1']))
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
    months = [str(i) for i in xrange(1, 13)]
    for year in ['2014', '2015', '2016']:
        for month in months:
            points.append('-'.join([year, month, '1']))

    return filter(
        lambda t: maketime(start) <= maketime(t) < maketime(end),
        points
    )


def network_create(points):

    for point in points:
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

        pickle_dump(network, NETWORK_PATH % point)


def scale_stats(points):

    x = xrange(len(points))
    yn, ye = [], []

    apps = []
    for point in points:
        network = pickle_load(NETWORK_PATH % point)
        apps.append(network.nodes())

    common_apps = reduce(lambda a, b: set(a) & set(b), apps)
    print len(common_apps), common_apps

    edges = []
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
        ya.append(len(cur - prev))
        yr.append(len(prev - cur))

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


if __name__ == '__main__':
    # date_distribution()
    points = get_points('2015-1-1', '2015-12-1')
    # network_create(points)
    scale_stats(points)