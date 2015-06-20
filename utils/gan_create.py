# -*- coding: utf-8 -*-

from utils.gan_edt_intent import *
from utils.gan_links_else import *
from itertools import combinations


# create each type of edge
def create_edges(gan, apps):
    count = 0
    for app_pair in combinations(apps, 2):
        count += 1
        print '> %d ...' % count
        for i in xrange(2):
            app_from, app_to = app_pair[i], app_pair[1 - i]
            exp = explicit_match(app_from, app_to)
            imp = implicit_match(app_from, app_to)
            iotag = iotag_match(app_from, app_to)
            sim = sim_match(app_from, app_to)
            if exp or imp or iotag or sim:
                if not gan.has_edge(app_from, app_to):
                    gan.add_edge(app_from, app_to,
                                 weights=[0 for i in xrange(NUM_EDGETYPE)])

                weights = gan[app_from][app_to]['weights']
                weights[INDEX.EDT_EXP] = exp
                weights[INDEX.EDT_IMP] = imp
                weights[INDEX.IDT_TAG] = iotag
                weights[INDEX.SIM] = sim

    for app_from in apps:
        for app_to, num in refs(app_from).iteritems():
            if not gan.has_edge(app_from, app_to):
                gan.add_edge(app_from, app_to,
                             weights=[0 for i in xrange(NUM_EDGETYPE)])

            gan[app_from][app_to]['weights'][INDEX.IDT_REF] = num

        for nat, num in nats(app_from).iteritems():
            if not gan.has_edge(app_from, nat):
                gan.add_edge(app_from, nat,
                             weights=[0 for i in xrange(NUM_EDGETYPE)])

            gan[app_from][nat]['weights'][INDEX.NAT] = num


# create gan
def create_gan():
    apps = load_capps()
    gan = nx.DiGraph()
    gan.add_nodes_from(apps)
    create_edges(gan, apps)
    dump_gan(gan)


if __name__ == '__main__':
    create_gan()
