# -*- coding: utf-8 -*-

import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import linregress
from utils.funcs_rw import *


# get r-value(Pearson correlation coefficient)
# linregress[0] = slope(斜率)
# linregress[1] = intercept(截距)
def pearson(x, y):
    return linregress(x, y)[2]


def draw_plot(x, y, xlabel='', ylabel='', title='', style='ro-'):
    plt.plot(x, y, style)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.title(title)
    plt.show()


def draw_bar_chart(x, y, xlabel='', title=''):
    y_pos = np.arange(len(y))
    plt.barh(y_pos, x, align='center', alpha=0.4)
    plt.yticks(y_pos, y)
    plt.xlabel(xlabel)
    plt.title(title)
    plt.show()


# get edges in set a but not in set b
def edges_diff(a, b):
    result = {}
    diff_keys = [k for k in a.keys() if k not in b.keys()]
    for k in a:
        tmp = set([]) if k in diff_keys else b[k]
        result[k] = a[k] - tmp
    return result


# get edges both in set a and set b
def edges_common(a, b):
    result = {}
    common_keys = [k for k in a.keys() if k in b.keys()]
    for k in common_keys:
        result[k] = a[k] & b[k]
    return result


# count the number of edges in set a
def edges_count(a):
    result = 0
    for key in a:
        result += len(a[key])
    return result


# merge different kinds of edges
def merge_edges(edges, another):
    for app in edges:
        if app not in another:
            continue
        edges[app] |= another[app]


# filters to get the sub network contains apps in apps_in_common
def filter_network(network, apps_in_common):
    new_network = {}
    for app_from, app_tos in network.iteritems():
        if app_from in apps_in_common:
            new_network[app_from] = set([])
            for app_to in app_tos:
                if app_to in apps_in_common:
                    new_network[app_from].add(app_to)
    return new_network


# get apps which are in the network
def apps_in_network(network):
    apps = set([])
    for app_from, app_tos in network.iteritems():
        apps.add(app_from)
        for app_to in app_tos:
            apps.add(app_to)
    return apps


# form in-edges to complete network
def complete_network(edges_out, apps):
    edges_in = get_edges(apps)
    [edges_out.setdefault(app, set([])) for app in apps]
    for app_from, app_tos in edges_out.iteritems():
        for app_to in app_tos:
            edges_in[app_to].add(app_from)
    return {'in': edges_in, 'out': edges_out}


# get the in-degree and out-degree of each app in network
def get_degrees(network):
    degrees_in, degrees_out = {}, {}
    apps = apps_in_network(network)
    network_complete = complete_network(network, apps)
    for app in apps:
        degrees_out[app] = len(network_complete['in'][app])
        degrees_in[app] = len(network_complete['out'][app])
    return {'in': degrees_in, 'out': degrees_out}


# get the filters rank list to see which is hot
def get_filters_rank():
    count = {}
    f = open(FILTERS_MATCHED)
    for line in f.readlines():
        filter = line.strip()
        if filter in count:
            count[filter] += 1
        else:
            count[filter] = 1
    f.close
    rank = list(count.iteritems())
    rank.sort(lambda a, b: a[1] - b[1])
    return rank


def app_filters_score():
    rank_f = get_filters_rank()
    scores = {}
    for app in load_capps():
        scores[app] = 0
        fs = filters(app)
        if fs:
            for f in fs:
                for pair in rank_f:
                    if f == eval(pair[0]):
                        scores[app] += pair[1]
    pickle_dump(scores, APP_FILTERS_SCORE)


# prepare data set for frequent pattern mining
def filters_code():
    code = 0
    code_dict = {}
    coded_list = []
    for app in load_capps():
        fs = filters(app)
        coded = []
        if fs:
            for f in fs:
                has = False
                for key, value in code_dict.iteritems():
                    if f == value:
                        coded.append(key)
                        has = True
                        break
                if not has:
                    code_dict[code] = f
                    coded.append(code)
                    code += 1
        if coded:
            coded_list.append(coded)

    pickle_dump(code_dict, CODE_DICT)
    pickle_dump(coded_list, CODED_LIST)
