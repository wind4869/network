# -*- coding: utf-8 -*-

import igraph as ig
from BeautifulSoup import BeautifulSoup

from utils.parser_apk import *


# get number, apk and html of each version for app
def download_dataset(app):

    # get version numbers from wandoujia (limited)
    versions = set([])
    soup = BeautifulSoup(urllib2.urlopen(VERSION_URL % app).read())
    for span in soup.findAll(attrs={'class': 'version-code'}):
        versions.add(int(re.findall(r'\d+', span.text)[0]))

    versions = sorted(versions)
    max_version = versions[-1]
    print '>>', len(versions), versions

    # create apk and html directory of app
    run('mkdir %s%s' % (APK_DIR, app))
    run('mkdir %s%s' % (HTML_DIR, app))

    # crawl as much versions as possible in the limited time
    version_range = xrange(max_version) if max_version < 1000 else versions

    version_date = {}
    for v in version_range:
        url = HTML_URL % (app, v)
        if url_exists(url):

            # get datetime of this version
            soup = BeautifulSoup(urllib2.urlopen(url).read())
            date = \
                soup.findAll(attrs={'class': 'line_content'})[-1].findAll('span')[-1].text.strip()
            version_date[v] = date

            print '>> %d (%s) crawling ...' % (v, date)

            # download apk and html of this version from http://apk.hiapk.com
            parameters = (app, v, app, v)
            [run(cmd) for cmd in [raw_cmd % parameters for raw_cmd in [HTML_CMD, APK_CMD]]]

        else:
            print '>> %d missed' % v

    # store dict (version: date) numbers to file
    pickle_dump(version_date, VERSION_PATH % app)


def analyse_dataset(app, versions):

    run('mkdir %s%s/' % (APP_DIR, app))

    for v in versions:

        print '>> %d analysing ...' % v
        run('mkdir %s%s/%s' % (APP_DIR, app, v))

        parameters = (app, v, app, v)
        [run(cmd) for cmd in [raw_cmd % parameters for raw_cmd in [D2J_CMD, XML_CMD]]]

    # remove all apk files
    print '>> remove all apk files'
    run('rm -r %s' % (APK_DIR + app))


def extract_dataset(app, versions):

    print '>> start extracting ... '

    # prepare for intent extracting
    f = open('/Users/wind/repos/IntentAnalysis/versions.txt', 'w')
    f.write(app + '\n')
    [f.write(str(v) + '\n') for v in versions]
    f.close()

    # do intents extracting
    run(INTENT_ANALYSIS)

    # remove all jar files
    print '>> remove all jar files'
    run('rm %s/*/classes.jar' % (APP_DIR + app))

    print '>> extraction finished '


def get_part(t1=100, t2=700):
    gan = load_gan()

    c0 = set([])
    for u, v in gan.edges():
        if gan[u][v]['weights'][INDEX.E_INTENT] or gan[u][v]['weights'][INDEX.I_INTENT]:
            [c0.add(i) for i in u, v]
        else:
            gan.remove_edge(u, v)

    # c1 = set([])
    # for app in c0:
    #     if url_exists('http://apk.hiapk.com/appinfo/' + app):
    #         c1.append(app)

    # apps = load_content(APPSC1_TXT)
    # gan = gan.subgraph(apps)
    #
    # degree_rank = []
    # idict, odict = gan.in_degree(), gan.out_degree()
    # for app in apps:
    #     degree_rank.append((app, idict[app] + odict[app]))
    # degree_rank = sorted(degree_rank, key=lambda x: x[1], reverse=True)
    #
    # download_rank = []
    # for app in load_capps():
    #     download_rank.append((app, downloadCount(app)))
    # download_rank = sorted(download_rank, key=lambda x: x[1], reverse=True)
    #
    # c2 = set([x[0] for x in degree_rank][:t1]) & \
    #      set([x[0] for x in download_rank][:t2])

    # store c2 to txt file
    # f = open(APPSC2_TXT, 'w')
    # for app in c2:
    #     f.write(app + '\n')
    # f.close()

    apps = load_eapps()
    gan = gan.subgraph(apps)

    print gan.number_of_nodes(), gan.number_of_edges()

    elist = []
    for e in gan.edges():
        u, v = e
        weights = gan[u][v]['weights']
        we, wi = weights[INDEX.E_INTENT], weights[INDEX.I_INTENT]
        w = we if we else wi
        elist.append((u, v, w))

    # write networkx to file
    part = nx.DiGraph()
    part.add_weighted_edges_from(elist)
    nx.write_graphml(part, GRAPHML_PATH)

    # read file to construct igraph
    graph = ig.Graph.Read_GraphML(GRAPHML_PATH)
    graph.vs['size'] = [15 for i in xrange(len(graph.vs))]

    # draw the graph
    ig.plot(graph, FIGURE_PATH % 'network', bbox=(2400, 1400))

    return part


if __name__ == '__main__':

    # apps = load_eapps()
    #
    # count = 1
    # for app in apps[count - 1:]:
    #
    #     print '> %d. %s' % (count, app)
    #     count += 1
    #
    #     download_dataset(app)
    #
    #     versions = get_versions(app)
    #     analyse_dataset(app, versions)
    #     extract_dataset(app, versions)

    get_part()
