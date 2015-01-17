# -*- coding: utf-8 -*-

import cPickle as pickle
from utils.db_read import *
from utils.vector_funs import get_edges


# use pickle to store the out edges of app network
def store_network(edges_out, path):
    pickle.dump(edges_out, open(path, 'w'))


# load out edges and form in edges
def load_network(path):
    edges_out = pickle.load(open(path))
    length = len(edges_out)
    apps = load_apps(length)
    edges_in = get_edges(apps)

    for app_from, app_tos in edges_out.iteritems():
        for app_to in app_tos:
            edges_in[app_to].add(app_from)

    return edges_out, edges_in