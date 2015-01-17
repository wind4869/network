# -*- coding: utf-8 -*-

import Levenshtein
from utils.graph import *
from utils.network_rs import *
from utils.vector_funs import *
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


# get system edges
def get_system_edges(apps):
    system_edges = get_edges(apps)
    perm_dict = load_perm_dict()
    for app in apps:
        for permission in permissions(app):
            sys_apps = perm_dict[permission]
            [system_edges[app].add(sys_app) for sys_app in sys_apps]
    return system_edges


# draw network by input parameter
def draw_network(test=ALL_MASK, number=NUMBER_OF_APP):
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

    # call edges
    if test & CALL_MASK:
        call_edges = get_call_edges(apps)
        graph.add_edges(call_edges, CAll_EDGE)
        merge_edges(edges, call_edges)

    # sim edges
    if test & SIM_MASK:
        sim_edges = get_sim_edges(apps)
        graph.add_edges(sim_edges, SIM_EDGE)
        merge_edges(edges, sim_edges)

    # system edges
    if test & SYSTEM_MASK:
        system_edges = get_system_edges(apps)
        graph.add_edges(system_edges, SYSTEM_EDGE)
        merge_edges(edges, system_edges)

    # intent edges
    if test & INTENT_MASK:
        intent_edges = get_intent_edges(apps)
        graph.add_edges(intent_edges)
        merge_edges(edges, intent_edges)

    store_network(edges, NETWORK_TXT)
    # graph.draw(IMAGE[test])


if __name__ == '__main__':
    draw_network(23, 100)  # 1, 2, 4, 8, 16, 31