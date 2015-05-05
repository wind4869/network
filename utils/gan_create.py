# -*- coding: utf-8 -*-

import Levenshtein
from utils.gan_stats import *
from utils.graph import *
from utils.vector_funcs import *
from utils.intent_match import *
from itertools import combinations


# merge different kinds of edges
def merge_edges(edges, another):
    for app in edges:
        edges[app] |= another[app]


# get data edges
def get_data_edge(apps, vectors):
    data_edges = get_edges(apps)
    for app_pair in combinations(apps, 2):
        app1, app2 = app_pair
        if v_sim(vectors[app1]['O'], vectors[app2]['I']) > 0:
            data_edges[app1].add(app2)
        if v_sim(vectors[app2]['O'], vectors[app1]['I']) > 0:
            data_edges[app2].add(app1)
    return data_edges


# get call edges
def get_call_edges(apps):
    call_edges = get_edges(apps)
    for app_pair in combinations(apps, 2):
        app1, app2 = app_pair
        if app1 in description(app2) and app1 not in app2:
            call_edges[app2].add(app1)
        if app2 in description(app1) and app2 not in app1:
            call_edges[app1].add(app2)

    # delete some app form call_edges
    for app in call_edges:
        for af in APP_FILTER:
            if af in call_edges[app]:
                call_edges[app].remove(af)

    return call_edges


# get sim edges
def get_sim_edges(apps):
    sim_edges = get_edges(apps)
    for app_pair in combinations(apps, 2):
        app1, app2 = app_pair
        if Levenshtein.ratio(app1, app2) > 0.1 and \
                c_sim(categories(app1), categories(app2)) > 0 and \
                c_sim(tags(app1), tags(app2)) > 2:
            sim_edges[app1].add(app2)
            sim_edges[app2].add(app1)
    return sim_edges


# get native edges
def get_native_edges(apps):
    system_edges = get_edges(apps)
    perms_natives = load_perms_natives()
    map_dict = load_map_dict()

    for app in apps:
        for p in perms(app):
            if p in perms_natives:
                [system_edges[app].add(s) for s in perms_natives[p]]

        for s in explicit_intents(app)['natives']:
            key = s.split('.')[2]
            value = map_dict.get(key)
            if value:
                system_edges[app].add(value)

    return system_edges


# create GAN by input parameter
def create_gan(test=ALL_MASK, number=NUMBER_OF_APP):
    # graph object to draw
    graph = Graph()

    # load data dictionary and tag I/O
    data_dict = load_data_dict()
    tag_io, tag_all = load_tag_io()

    # load test apps
    apps = load_apps(number)
    edges = get_edges(apps)

    # data edges
    if test & DATA_MASK:
        v_fill = get_v_fill(tag_io, data_dict)
        vectors = get_vectors(apps, tag_all, len(data_dict), v_fill)

        data_edges = get_data_edge(apps, vectors)
        graph.add_edges(data_edges, DATA_EDGE)
        merge_edges(edges, data_edges)

        print '> data edges finished'

    # call edges
    if test & CALL_MASK:
        call_edges = get_call_edges(apps)
        graph.add_edges(call_edges, CAll_EDGE)
        merge_edges(edges, call_edges)

        print '> call edges finished'

    # sim edges
    if test & SIM_MASK:
        sim_edges = get_sim_edges(apps)
        graph.add_edges(sim_edges, SIM_EDGE)
        merge_edges(edges, sim_edges)

        print '> sim edges finished'

    # native edges
    if test & NATIVE_MASK:
        native_edges = get_native_edges(apps)
        graph.add_edges(native_edges, NATIVE_EDGE)
        merge_edges(edges, native_edges)

        print '> native edges finished'

    # intent edges
    if test & INTENT_MASK:
        intent_edges = get_intent_edges(apps)
        graph.add_edges(intent_edges)
        merge_edges(edges, intent_edges)

        print '> intent edges finished'

    dump_network(edges, GAN_TXT % (test, number, '0118'))
    graph.draw(IMAGE[test])


if __name__ == '__main__':
    # 1, 2, 4, 8, 16 for single
    # 7 without native and intent edges
    # 23 without native edges
    # 31 for all
    create_gan(DATA_MASK)
