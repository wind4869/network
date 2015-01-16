# -*- coding: utf-8 -*-

import cPickle as pickle
from utils.db_read import *
from utils.vector_funs import get_edges


# use pickle to store the adjacent matrix of app network
def store_network(edges):
    length = len(edges)
    apps = load_apps(length)
    network = [[0 for j in xrange(length)] for i in xrange(length)]

    for app_from, app_tos in edges.iteritems():
        index_from = apps.index(app_from)
        for app_to in app_tos:
            index_to = apps.index(app_to)
            network[index_from][index_to] = 1

    pickle.dump(network, open(NETWORK_TXT, 'w'))


# load network from pickle file
def load_network():
    network = pickle.load(open(NETWORK_TXT))
    length = len(network)
    apps = load_apps(length)
    edges = get_edges(apps)

    for i in xrange(length):
        for j in xrange(length):
            if network[i][j]:
                edges[apps[i]].add(apps[j])

    return edges