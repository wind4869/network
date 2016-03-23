# -*- coding: utf-8 -*-

from itertools import combinations

from utils.gan_rels_intent import *
from utils.gan_rels_else import *


# create each type of edge and weight
def create_edges(gan, apps):
    count = 0
    for app_pair in combinations(apps, 2):
        count += 1
        print '> %d ...' % count  # display progress

        e_intents, i_intents, i_io, sim = 0, 0, 0, 0
        for i in xrange(2):
            app_from, app_to = app_pair[i], app_pair[1 - i]

            # calculate E_INTENT, I_INTENT and I_IO weights
            e_intents = explicit_match(app_from, app_to)
            i_intents = implicit_match(app_from, app_to)
            i_io = io_match(app_from, app_to)

            # calculate SIMILAR weight only once
            if not i: sim = sim_match(app_from, app_to)

            # add weights to gan
            if e_intents or i_intents or i_io or sim:
                weights = get_weights(gan, app_from, app_to)

                weights[INDEX.E_INTENT] = e_intents
                weights[INDEX.I_INTENT] = i_intents
                weights[INDEX.I_IO] = i_io
                weights[INDEX.SIMILAR] = sim

    for app_from in apps:
        # calculate E_IO weight
        for app_to in refs(app_from):
            weights = get_weights(gan, app_from, app_to)
            weights[INDEX.E_IO] = 1

        # calculate NATIVE weight
        for app_to in explicits(app_from):
            if app_to in load_napps():
                weights = get_weights(gan, app_from, app_to)
                weights[INDEX.NATIVE] = 2


# create gan
def create_gan():
    # create a directed graph
    gan = nx.DiGraph()
    gan.add_nodes_from(load_apps())

    # create each type of edge and weight
    create_edges(gan, load_capps())

    # calculate total weight
    for app_from, app_to in gan.edges():
        weights = get_weights(gan, app_from, app_to)
        if weights[INDEX.E_INTENT] or weights[INDEX.I_INTENT]:
            gan[app_from][app_to]['weight'] = \
                weights[INDEX.E_INTENT] + \
                weights[INDEX.I_INTENT]
        else:
            gan[app_from][app_to]['weight'] = \
                weights[INDEX.E_IO] + \
                weights[INDEX.I_IO]

        # consider SIMILAR weight anyway
        gan[app_from][app_to]['weight'] += weights[INDEX.SIMILAR]

    # dump gan
    dump_gan(gan)


if __name__ == '__main__':
    pass
