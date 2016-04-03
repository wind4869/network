# -*- coding: utf-8 -*-

import numpy as np

from utils.parser_apk import *
from utils.gan_rels_intent import *


def unique(c):
    return reduce(lambda a, b: a if b in a else a + [b], [[], ] + c)


def parallel_sort(list1, list2):
    data = zip(list1, list2)
    data.sort()
    return map(lambda t: list(t), zip(*data))


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


def ordered_apps(ctype):
    temp = []
    for app in load_eapps():
        c = get_components_all(app)[ctype]
        temp.append((app, len(c)))

    return [x[0] for x in sorted(temp, key=lambda x: x[1])]


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


def components_test(app, ctype):

    data = get_data(app, ctype, DIRECTION.COMPONENT)

    if ctype == COMPONENT.I_INTENT:
        heat_map(data, 'Version Labels', 'Implicit-intent Labels', 'intents_' + app)
    elif ctype == COMPONENT.I_FILTER:
        heat_map(data, 'Version Labels', 'Intent-filter Labels', 'filters_' + app)


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

    x = xrange(length)
    plt.plot(x, yp, 'ro-')
    plt.plot(x, yc, 'bs-')
    plt.show()


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

    yp_intent, yp_filter = parallel_sort(yp_intent, yp_filter)
    yc_intent, yc_filter = parallel_sort(yc_intent, yc_filter)

    plt.plot(x, yp_intent, 'ro-')
    plt.plot(x, yp_filter, 'bs-')
    plt.savefig(FIGURE_PATH % 'percentage', format='pdf')
    plt.close()

    plt.plot(x, yc_intent, 'ro-')
    plt.plot(x, yc_filter, 'bs-')
    plt.savefig(FIGURE_PATH % 'continuity', format='pdf')


def version_each(app, ctype):
    y = []
    data = get_data(app, ctype)
    for i in xrange(1, len(data)):
        y.append(sim_cosine(data[i - 1], data[i]))

    return np.var(y)

    x = xrange(len(data) - 1)
    plt.plot(x, y, 'ro-')
    plt.savefig(FIGURE_PATH % ('version_' + app), format='pdf')
    plt.show()


def version_test():
    apps = load_eapps()
    x = xrange(len(apps))

    yi, yf = [], []
    for app in apps:
        yi.append(version_each(app, COMPONENT.I_INTENT))
        yf.append(version_each(app, COMPONENT.I_FILTER))

    print pearson(yi, yf)

    yi, yf = parallel_sort(yi, yf)
    plt.plot(x, yi, 'ro-')
    plt.plot(x, yf, 'bs-')
    plt.savefig(FIGURE_PATH % 'version', format='pdf')
    plt.show()


if __name__ == '__main__':
    # existence_test(COMPONENT.I_INTENT)
    # cover_test_1(COMPONENT.I_FILTER)
    # cover_test_2()
    version_test()
