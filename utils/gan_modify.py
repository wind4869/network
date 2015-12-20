# -*- coding: utf-8 -*-

from utils.gan_rels_intent import *
from utils.gan_rels_else import *


def add_app(gan, new_app):
    old_apps = [app for app in gan.nodes() if app not in load_napps()]  # apps already in gan
    gan.add_node(new_app)  # add new app to gan

    for app_pair in [(new_app, old_app) for old_app in old_apps]:
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

    # calculate E_IO weight
    for app_to in refs(new_app):
        weights = get_weights(gan, new_app, app_to)
        weights[INDEX.E_IO] = 1

    for app_from in old_apps:
        if new_app in refs(app_from):
            weights = get_weights(gan, app_from, new_app)
            weights[INDEX.E_IO] = 1

    # calculate NATIVE weight
    for app_to in explicits(new_app):
        if app_to in load_napps():
            weights = get_weights(gan, new_app, app_to)
            weights[INDEX.NATIVE] = 2

    # calculate total weight for edges
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


def add_apps(new_apps):
    # load gan
    gan = load_gan()

    # add new apps to gan
    count = 0
    for new_app in new_apps:
        count += 1
        print '> %d ...' % count  # display progress
        add_app(gan, new_app)  # add one app each time

    # nx.write_dot(gan, LAN_DIR + 'gan.dot')
    pickle_dump(gan, LAN_DIR + 'gan.pickle')


if __name__ == '__main__':
    pass
