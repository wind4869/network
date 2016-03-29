# -*- coding: utf-8 -*-

from utils.parser_apk import *


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


if __name__ == '__main__':
    apps = load_eapps()
    for app in apps:
        existence_test(app, COMPONENT.I_FILTER)
        cover_test(app, COMPONENT.I_FILTER)
        version_test(app, COMPONENT.I_FILTER)