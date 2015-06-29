# -*- coding: utf-8 -*-

import time
from math import sqrt
from itertools import combinations

from utils.gan_edt_intent import *
from utils.gan_rels_else import *


# create each type of edge
def create_edges(gan, apps):
    count = 0
    for app_pair in combinations(apps, 2):
        count += 1
        print '> %d ...' % count  # display progress

        exp, imp, iotag, sim = 0, 0, 0, 0
        for i in xrange(2):
            app_from, app_to = app_pair[i], app_pair[1 - i]

            # calculate each weight
            exp = explicit_match(app_from, app_to)
            imp = implicit_match(app_from, app_to)
            iotag = iotag_match(app_from, app_to)

            if not i:  # calculate only once
                sim = sim_match(app_from, app_to)

            if exp or imp or iotag or sim:
                weights = get_weights(gan, app_from, app_to)

                weights[INDEX.EDT_EXP] = exp
                weights[INDEX.EDT_IMP] = imp
                weights[INDEX.IDT_TAG] = iotag
                weights[INDEX.SIM] = sim

    for app_from in apps:
        ref_apps = refs(app_from)
        ref_count = reduce(lambda a, b: a + b, ref_apps.values(), 0)
        for app_to, num in ref_apps.iteritems():
            weights = get_weights(gan, app_from, app_to)
            weights[INDEX.IDT_REF] = float(num) / ref_count

        nat_apps = nats(app_from)
        nat_count = reduce(lambda a, b: a + b, nat_apps.values(), 0)
        for nat, num in nat_apps.iteritems():
            weights = get_weights(gan, app_from, nat)
            weights[INDEX.NAT] = float(num) / nat_count


# create gan
def create_gan():
    apps = load_capps()
    gan = nx.DiGraph()
    gan.add_nodes_from(apps)
    create_edges(gan, apps)
    dump_gan(gan)


if __name__ == '__main__':
    # start = time.clock()
    # create_gan()  # create gan
    # print 'finished in (%.2f) minutes' %\
    #       ((time.clock() - start) / float(60))
    gan = load_gan()
    m = 0
    for app_from, app_to in gan.edges():
        weights = gan[app_from][app_to]['weights']
        result = sqrt(weights[INDEX.EDT_IMP])
        if result:
            if result > m:
                m = result
            print result
