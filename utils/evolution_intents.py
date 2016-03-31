# -*- coding: utf-8 -*-

import numpy as np
from itertools import combinations

from utils.parser_apk import *
from utils.gan_rels_intent import *


def unique(c):
    return reduce(lambda a, b: a if b in a else a + [b], [[], ] + c)


def get_components_each(app, v):
    components = list(get_intents(app, v))
    components.append(get_filters(app, v)[0])
    return components


def get_components_all(app):

    eintents, iintents, filters = [], [], []

    for v in get_versions(app):
        components = get_components_each(app, v)

        eintents.extend(components[COMPONENT.E_INTENT])
        iintents.extend(components[COMPONENT.I_INTENT])
        filters.extend(components[COMPONENT.I_FILTER])

    return [unique(c) for c in [eintents, iintents, filters]]


def components_test(app, index):

    data = []
    components_all = get_components_all(app)[index]
    for i in xrange(len(components_all)):
        print i, components_all[i]

    for v in get_versions(app):
        components = get_components_each(app, v)[index]
        if not components:
            continue

        data.append([1 if i in components else 0 for i in components_all])

    if index == 0:
        heat_map(map(list, zip(*data)), 'Version Labels', 'Explict-intent Labels', 'explict_intents')
    elif index == 1:
        heat_map(map(list, zip(*data)), 'Version Labels', 'Implicit-intent Labels', 'implicit_intents')
    elif index == 2:
        heat_map(map(list, zip(*data)), 'Version Labels', 'Intent-filter Labels', 'intent_filters')


def get_data(app, ctype, direction=DIRECTION.VERSION):

    data = []
    components_all = get_components_all(app)[ctype]

    for v in get_versions(app):
        components = get_components_each(app, v)[ctype]
        if not components:
            continue

        data.append([1 if i in components else 0 for i in components_all])

    if direction == DIRECTION.COMPONENT:
        return map(list, zip(*data))
    elif direction == DIRECTION.VERSION:
        return data


def ordered_apps(ctype):
    temp = []
    for app in load_eapps():
        c = get_components_all(app)[ctype]
        temp.append((app, len(c)))

    return [x[0] for x in sorted(temp, key=lambda x: x[1])]


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


def existence_each(app, ctype):

    result = [0 for i in xrange(4)]
    data = get_data(app, ctype, DIRECTION.COMPONENT)

    for v in data:
        t = existence_type(v)
        result[t] += 1

    return map(lambda x: float(x) / sum(result), result)


def existence_test(ctype):
    apps = ordered_apps(ctype)

    x = xrange(len(apps))
    y = [[], [], [], []]

    for app in apps:
        result = existence_each(app, ctype)
        [y[i].append(result[i]) for i in xrange(4)]

    f, ax = plt.subplots(4, 1, sharex=True)
    shape = ['ro-', 'go-', 'bo-', 'yo-']

    for i in xrange(len(y)):
        ax[i].plot(x, y[i], shape[i])

    if ctype == COMPONENT.I_INTENT:
        plt.savefig(FIGURE_PATH % 'existence_intent', format='pdf')
    elif ctype == COMPONENT.I_FILTER:
        plt.savefig(FIGURE_PATH % 'existence_filter', format='pdf')
    plt.show()

    # print [round(np.mean(i), 2) for i in y]
    # print [round(np.median(i), 2) for i in y]
    # print [round(np.var(i), 2) for i in y]


def cover_each(app, ctype):
    yp, yc = [], []
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

        yp.append((sum(v) / float(length)))
        yc.append(sum(v) / float(end - start + 1))

    return [np.mean(y) for y in yp, yc]


def cover_test_1(ctype):
    apps = ordered_apps(ctype)

    x = xrange(len(apps))
    yp, yc = [], []

    for app in apps:
        p, c = cover_each(app, ctype)
        yp.append(p)
        yc.append(c)

    plt.plot(x, yp, 'ro-')
    plt.plot(x, yc, 'bs-')

    # print pearson(yp, yc)

    if ctype == COMPONENT.I_INTENT:
        plt.savefig(FIGURE_PATH % 'cover_intent', format='pdf')
    elif ctype == COMPONENT.I_FILTER:
        plt.savefig(FIGURE_PATH % 'cover_filter', format='pdf')
    plt.show()


def cover_test_2():
    apps = load_eapps()

    x = xrange(len(apps))
    yp_intent, yp_filter = [], []
    yc_intent, yc_filter = [], []

    for app in apps:
        p, c = cover_each(app, COMPONENT.I_INTENT)
        yp_intent.append(p)
        yc_intent.append(c)

        p, c = cover_each(app, COMPONENT.I_FILTER)
        yp_filter.append(p)
        yc_filter.append(c)

    print pearson(yp_intent, yp_filter)  # 0.62
    print pearson(yc_intent, yc_filter)  # 0.78


def version_test(app, ctype):
    y = []
    data = get_data(app, ctype)
    for i in xrange(1, len(data)):
        y.append(sim_cosine(data[i - 1], data[i]))

    x = xrange(len(data) - 1)
    plt.plot(x, y, 'ro-')
    plt.show()


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
    # existence_test(COMPONENT.I_INTENT)
    # cover_test_1(COMPONENT.I_FILTER)
    cover_test_2()
    # date_distribution()
    # points = get_points('2015-1-1', '2015-12-1')
    # network_create(points)
    # scale_stats(points)
