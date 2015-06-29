# -*- coding: utf-8 -*-

import time
from math import sqrt
from itertools import combinations

from utils.gan_edt_intent import *
from utils.gan_rels_else import *


# create each type of edge with weight
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


# use sqrt to "smooth" and
# divide max weight to normalize
def fix_edt_emp(gan):
    mw = 0
    for u, v in gan.edges():
        ws = gan[u][v]['weights']
        w = sqrt(ws[INDEX.EDT_IMP])
        if w > mw:
            mw = w
        ws[INDEX.EDT_IMP] = w

    for u, v in gan.edges():
        ws = gan[u][v]['weights']
        ws[INDEX.EDT_IMP] /= mw


# add global weight of gan
def add_global_weight(gan):
    fix_edt_emp(gan)
    mw = 0
    for u, v in gan.edges():
        weights = get_weights(gan, u, v)
        nat = weights[INDEX.NAT]
        if nat:
            gan[u][v]['weight'] = nat
        else:
            temp = reduce(
                lambda a, b: a + b,
                [WEIGHTS[i] * weights[i] for i in xrange(NUM_EDGETYPE - 2)]) / WEIGHT_GAN
            gan[u][v]['weight'] = sqrt(temp)  # use sqrt to "smooth"
            if temp > mw:
                mw = temp

    # divide max weight to normalize
    for u, v in gan.edges():
        if not get_weights(gan, u, v)[INDEX.NAT]:
            w = gan[u][v]['weight']
            w /= mw


# create raw gan
def create_rgan():
    apps = load_capps()
    gan = nx.DiGraph()
    gan.add_nodes_from(apps)
    create_edges(gan, apps)
    dump_rgan(gan)


# create the final gan
def create_gan():
    # create_rgan()
    gan = load_rgan()
    add_global_weight(gan)
    dump_gan(gan)


if __name__ == '__main__':
    # start = time.clock()
    # create_rgan()  # create raw gan
    # print 'finished in (%.2f) minutes' %\
    #       ((time.clock() - start) / float(60))

    gan = load_gan()
    for u, v in gan.edges():
        print gan[u][v]['weight']
