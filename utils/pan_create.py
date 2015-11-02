# -*- coding: utf-8 -*-

import time
from utils.funcs_rw import *


# creates time object from string
def maketime(s):
    return time.mktime(time.strptime(s, '%Y-%m-%d %H:%M:%S'))


# create pan
def create_pan(uid):
    # create a directed graph
    pan = nx.DiGraph()
    # total usage time of apps
    app_time = {}
    # separate by the screen
    session = []
    # load applog.txt
    f = open_in_utf8(LOG_PATH % uid)
    for line in f.readlines():
        if line[0] == '[' and not session:
            continue
        elif line[0] not in ['[', ']']:
            record = line.strip().split(',')
            # usage time
            app = record[2]
            app_time.setdefault(app, 0)
            app_time[app] += maketime(record[1]) - maketime(record[0])
            # add to session
            session.append(app)
        elif len(session) > 1:
            for index in xrange(len(session)):
                app_from = session[index]
                for offset in xrange(len(CORRELATION)):
                    weight = CORRELATION[offset]
                    nextIndex = index + offset + 1
                    if nextIndex < len(session):
                        app_to = session[nextIndex]
                        if pan.has_edge(app_from, app_to):
                            pan[app_from][app_to]['weight'] += weight
                            print '> %s -> %s: %f' % (app_from, app_to, weight)
                        elif app_from != app_to:
                            pan.add_edge(app_from, app_to, weight=weight)
                            print 'ADD > %s -> %s: %f' % (app_from, app_to, weight)
            session = []
    f.close()

    # set the weight of each node
    total_time = sum(app_time.values())
    for app, t in app_time.iteritems():
        weight = t / total_time
        if pan.has_node(app):
            pan.node[app]['weight'] = weight
        else:
            pan.add_node(app, weight=weight)

    # dump pan
    dump_pan(uid, pan)


if __name__ == '__main__':
    create_pan('a1')
    pass
