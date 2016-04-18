# -*- coding: utf-8 -*-

import numpy as np

from utils.parser_apk import *
from utils.gan_rels_intent import *


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


def existence_test(ctype, num_types=4):

    apps = load_eapps()
    x = xrange(len(apps))

    y = [[] for i in xrange(num_types)]

    for app in apps:
        result = existence_each(app, ctype)
        [y[i].append(result[i]) for i in xrange(num_types)]

    temp = []
    for i in xrange(1, num_types):
        temp, y[i] = parallel_sort(y[0][:], y[i])
    y[0] = temp

    shape = ['ro-', 'go-', 'bo-', 'yo-']
    f, ax = plt.subplots(num_types, 1, sharex=True)

    for i in xrange(num_types):
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


def number_each(app):

    versions = get_versions(app)

    yi, yf = [], []
    for v in versions:
        components = get_components_each(app, v)
        ni = len(components[COMPONENT.I_INTENT])
        nf = len(components[COMPONENT.I_FILTER])
        if ni and nf:
            yi.append(ni)
            yf.append(nf)

    x = xrange(len(yi))

    return yi[-1], yf[-1]

    # plt.plot(x, yi, 'ro-')
    # plt.plot(x, yf, 'bs-')
    # plt.savefig(FIGURE_PATH % ('number_' + app), format='pdf')
    # plt.show()
    # plt.close()


def number_test():

    temp = []
    yi, yf = [], []
    apps = load_eapps()
    x = xrange(len(apps))

    for app in apps:

        ni, nf = number_each(app)
        yi.append(ni)
        yf.append(nf)

    print pearson(yi, yf)

    yi, yf = parallel_sort(yi, yf)

    plt.plot(x, yi, 'ro-')
    plt.plot(x, yf, 'bs-')
    plt.savefig(FIGURE_PATH % 'number', format='pdf')
    plt.show()


def case_study(app):

    ctypes = [COMPONENT.I_INTENT, COMPONENT.I_FILTER]
    ylabels = ['Intent Label', 'Filter Label']
    fnames = ['intent_', 'filter_']

    for i in xrange(len(ctypes) - 1):
        count = 0
        cs = get_components_all(app)[ctypes[i]]
        with open(FIGURE_DIR + fnames[i] + app + '.txt', 'w') as f:
            for c in cs:
                content = ' '.join([str(x) for x in count, c])
                f.write(content + '\n')
                count += 1

        data = get_data(app, ctypes[i], DIRECTION.COMPONENT)
        heat_map(data, 'Version Labels', ylabels[i], fnames[i] + app)


def wechat_intent(app='com.tencent.mm'):

    cs = get_components_all(app)[COMPONENT.I_INTENT]
    data = get_data(app, COMPONENT.I_INTENT, DIRECTION.COMPONENT)

    shade = {
        'android.intent.action.CALL': 0,
        'android.intent.action.DIAL': 0,
        'android.intent.action.SEND': .1,
        'android.intent.action.SENDTO': .1,
        'android.intent.action.INSERT': .2,
        'android.intent.action.INSERT_OR_EDIT': .2,
        'android.intent.action.GET_CONTENT': .3,
        'android.intent.action.PICK': .3,
        'com.android.music.musicservicecommand': .4,
        'android.intent.action.VIEW_DOWNLOADS': .5,
        }

    new_data = []
    for i in xrange(len(data)):
        action = cs[i]['action']
        if 'com.tencent' in action:
            continue

        s = shade.get(action, .9)

        if 'uri' in cs[i]:
            s = .8
        elif action == 'android.intent.action.VIEW' and \
                        cs[i].get('mimeType', '') in ['text/plain', 'video/*']:
            s = .7
        elif 'android.settings' in action:
            s = .6
        elif cs[i].get('mimeType', '') == 'vnd.android-dir/mms-sms':
            s = .5

        for j in xrange(len(data[0])):
            data[i][j] = s if data[i][j] else 1

        new_data.append(data[i])

    plt.figure(figsize=(16, 9))
    plt.imshow(new_data, cmap=plt.cm.hot, interpolation='nearest')
    plt.xticks(xrange(0, len(new_data[0]), 5))
    plt.yticks(
        [
            2, 3, 6, 9, 12,
            13, 14, 15, 16, 18,
            19, 20, 21, 22, 23,
            24, 25, 26, 28, 31,
            36, 37,
        ],
        [
            'view message', 'set wireless', 'command music', 'set location', 'send text',
            'insert', 'set apn', 'insert person', 'call', 'view text',
            'get video', 'get image', 'set display', 'view video', 'insert contact',
            'view downloads', 'sendto', 'pick', 'dial', 'set app ops',
            'set nfc', 'set manage app',
        ])
    plt.grid()
    plt.savefig(FIGURE_PATH % 'intents', format='pdf')
    plt.show()


def wechat_filter(app='com.tencent.mm'):

    cs = get_components_all(app)[COMPONENT.I_FILTER]
    data = get_data(app, COMPONENT.I_FILTER, DIRECTION.COMPONENT)

    yticks_dict = {
        4:  ('send image/video/*', 0),
        5:  ('send +app/text', 0),
        9:  ('view timeline/profile', .2),
        11: ('sendm image', .4),
        14: ('send image', .4),
        16: ('view +login/phonenum', .2),
        24: ('view +voip', .2),
        25: ('send +audio', 0),
        27: ('view image', .6),
        29: ('send +app/text', 0),
        30: ('send +audio', 0),
    }

    for i in xrange(len(data)):

        s = yticks_dict.get(i, ('', .8))[1]

        for j in xrange(len(data[0])):
            data[i][j] = s if data[i][j] else 1

    plt.figure(figsize=(16, 9))
    plt.imshow(data, cmap=plt.cm.hot, interpolation='nearest')

    plt.xticks(xrange(0, len(data[0]), 5))
    plt.yticks(
        yticks_dict.keys(),
        [v[0] for v in yticks_dict.values()]
    )
    plt.grid()
    plt.savefig(FIGURE_PATH % 'filters', format='pdf')
    plt.show()


if __name__ == '__main__':
    # existence_test(COMPONENT.I_INTENT)
    # existence_test(COMPONENT.I_FILTER)
    # cover_test_1(COMPONENT.I_INTENT)
    # cover_test_1(COMPONENT.I_FILTER)
    # cover_test_2()
    # version_test()
    # number_test()
    # case_study('com.tencent.mm')
    # wechat_intent()
    wechat_filter()
