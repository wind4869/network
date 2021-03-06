# -*- coding: utf-8 -*-

from utils.functions import *


# map to app already exists in gan
def domap(app):
    appmap = load_appmap()
    return appmap[app] if app in appmap else app


# create pan
def create_pan(uid):
    # create a directed graph
    pan = nx.DiGraph()
    # total usage time of apps
    times = {}
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
            app = domap(record[2])  # do mapping
            if app != u'com.android.launcher':
                times.setdefault(app, 0)
                times[app] += maketime(record[1]) - maketime(record[0])
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
                        elif app_from != app_to:
                            pan.add_edge(app_from, app_to, weight=weight)
            session = []
    f.close()

    # set the weight of each node
    total = sum(times.values())
    for app, t in times.iteritems():
        weight = t / total
        if pan.has_node(app):
            pan.node[app]['weight'] = weight
        else:
            pan.add_node(app, weight=weight)

    # dump pan
    dump_pan(uid, pan)


# create PAN for all users
def create_all():
    count = 1
    for uid in load_uids():
        print '> %d ...' % count
        create_pan(uid)
        count += 1


if __name__ == '__main__':
    create_all()
