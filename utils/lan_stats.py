# -*- coding: utf-8 -*-

import numpy as np
import igraph as ig
import matplotlib.pyplot as plt
from utils.funcs_rw import *
from scipy.stats import linregress


# get r-value(Pearson correlation coefficient)
# linregress(x, y)[0] = slope(斜率)
# linregress(x, y)[1] = intercept(截距)
def pearson(x, y):
    return linregress(x, y)[2]


def correlation_analyse():
    for uid in load_uids():
        pan = load_pan(uid)
        apps_score = nx.pagerank(pan)

        x, y = [], []
        for app in apps_score:
            x.append(apps_score[app])
            y.append(pan.node[app]['weight'])

        # correlated significantly if r > 0.8
        r = pearson(x, y)
        if r > 0.8:
            print r, uid


# number of nodes, number of edges and density
def scale_and_density(lan):
    nodes = lan.number_of_nodes()
    edges = lan.number_of_edges()
    density = float(edges) / (nodes * (nodes - 1))
    return nodes, edges, density


# get maximum, minimum and average statistics of PAN
def stats_scale_and_density():
    nodes, edges, density = [], [], []
    for uid in load_uids():
        result = scale_and_density(load_pan(uid))
        nodes.append(result[0])
        edges.append(result[1])
        density.append(result[2])

    print 'max: ', [max(x) for x in (nodes, edges, density)]
    print 'min: ', [min(x) for x in (nodes, edges, density)]
    print 'avg: ', [float(sum(x)) / len(x) for x in (nodes, edges, density)]


def degree_histograms(lan):
    idict, odict = lan.in_degree(), lan.out_degree()  # { node: degree, ... }
    ivalues, ovalues = [set(d.values()) for d in idict, odict]
    ihist = [idict.values().count(i) if i in ivalues else 0 for i in xrange(max(ivalues) + 1)]
    ohist = [odict.values().count(i) if i in ovalues else 0 for i in xrange(max(ovalues) + 1)]

    print 'Max In-Degree, Out-Degree: %d, %d' % (max(ivalues), max(ovalues))
    return ihist, ohist, nx.degree_histogram(lan)


def degree_distribution(lan):
    ihist, ohist, hist = degree_histograms(lan)
    ix, ox, x = [range(len(h)) for h in ihist, ohist, hist]
    iy, oy, y = [[i / float(sum(h)) for i in h] for h in ihist, ohist, hist]

    plt.loglog(ix, iy, color='blue', linewidth=2)  # In-Degree
    plt.loglog(ox, oy, color='red', linewidth=2)  # Out-Degree
    # plt.loglog(x, y, color='black', linewidth=2)

    plt.legend(['In-Degree', 'Out-Degree'])
    plt.xlabel('Degree Values')
    plt.ylabel('Frequency of Degrees')
    plt.title('Degree Distribution of LAN')
    plt.show()


def power_law_distribution(lan):
    ihist, ohist, hist = degree_histograms(lan)
    ix, ox, x = [range(len(h)) for h in ihist, ohist, hist]
    iy, oy, y = [[sum(h[i:]) for i in xrange(len(h))] for h in ihist, ohist, hist]

    # y = c * x^-r (power function)
    plt.plot(ix, iy, color='blue', linewidth=2)  # In-Degree
    plt.plot(ox, oy, color='red', linewidth=2)  # Out-Degree
    # plt.plot(x, y, color='black', linewidth=2)  # Degree

    # lny = -rlnx + lnc (linear correlation)
    ix, ox, x = [np.array([np.log(i) for i in d[1:]]) for d in ix, ox, x]
    iy, oy, y = [np.array([np.log(i) for i in a[1:]]) for a in iy, oy, y]

    print 'r-value of In-Degree: %f' % pearson(ix, iy)
    print 'r-value of Out-Degree: %f' % pearson(ox, oy)
    # print 'r-value of Degree: %f' % pearson(x, y)

    plt.legend(['In-Degree', 'Out-Degree'])
    plt.xlabel('Degree Values')
    plt.ylabel('The Number of Apps')
    plt.title('Power Law Distribution of LAN')
    plt.show()


def weakly_connected_components(lan):
    num = nx.number_weakly_connected_components(lan)
    components = nx.weakly_connected_component_subgraphs(lan)

    print 'Number of weakly connected components: %d' % num
    for c in components:
        print c.number_of_nodes(), c.nodes()


def strongly_connected_components(lan):
    num = nx.number_strongly_connected_components(lan)
    components = nx.strongly_connected_component_subgraphs(lan)

    print 'Number of strongly connected components: %d' % num
    for c in components:
        print c.number_of_nodes(), c.nodes()


def centrality(lan):
    # compute the degree centrality for nodes
    print nx.degree_centrality(lan)
    print nx.in_degree_centrality(lan)
    print nx.out_degree_centrality(lan)

    # compute closeness centrality for nodes
    print nx.closeness_centrality(lan)

    # compute the shortest-path betweenness centrality for nodes
    print nx.betweenness_centrality(lan)
    # compute betweenness centrality for edges
    print nx.edge_betweenness_centrality(lan)


def link_analysis(lan):
    # compute the PageRank of the nodes in the graph
    print nx.pagerank(lan)

    # compute HITS hubs and authorities values for nodes
    print nx.hits(lan)


def single_source_longest_path(lan, source):
    path, weight = [source], 0
    while lan.successors(source):
        next, mw = None, 0
        for node in lan.successors(source):
            if lan[source][node]['weight'] > mw:
                mw = lan[source][node]['weight']
                next = node

        # form a cycle
        if next in path: break

        weight += mw
        path.append(next)
        source = next

    return path, weight


# get longest path using a greedy algorithm
def longest_path(lan):
    paths = []
    for node in lan.nodes():
        paths.append(single_source_longest_path(lan, node))
    return sorted(paths, key=lambda x: x[1], reverse=True)[0]


# get the centers of star topologies
def star_topologies(lan):
    idict, odict = lan.in_degree(), lan.out_degree()  # { node: degree, ... }
    ilist = sorted([(node, degree) for node, degree in idict.iteritems()],
                   key=lambda x: x[1], reverse=True)
    olist = sorted([(node, degree) for node, degree in odict.iteritems()],
                   key=lambda x: x[1], reverse=True)

    return ilist, olist


# convert graph in networkx to igraph
def convert_to_igraph(uid):
    nx.write_graphml(load_pan(uid), GRAPHML_PATH)
    return ig.Graph.Read_GraphML(GRAPHML_PATH)


# get communities using igraph
def communities(uid):
    pan = convert_to_igraph(uid)

    clusters = pan.community_edge_betweenness().as_clustering()
    # clusters = pan.community_spinglass()
    membership = clusters.membership
    vc = ig.VertexClustering(pan, membership)

    ig.plot(vc, bbox=(1000, 1000))


def compare_gan_pans_nodes():
    apps_count = {}
    for uid in load_uids():
        for node in load_pan(uid).nodes():
            apps_count.setdefault(node, 0)
            apps_count[node] += 1

    app_count_tuples, apps_in_pans = [], set([])
    for node, count in apps_count.iteritems():
        app_count_tuples.append((node, count))
        apps_in_pans.add(node)

    # sort by frequency
    app_count_tuples.sort(key=lambda x: x[1], reverse=True)

    # apps in gan
    apps_in_gan = set(load_gan().nodes())

    # total amount
    print len(apps_in_gan), len(apps_in_pans)  # 2685, 665

    # intersection
    print len(apps_in_gan & apps_in_pans)  # 523 = (665 - 142)

    for threshold in [1, 8, 16]:
        apps = set([x[0] for x in filter(
            lambda x: x[1] > threshold,
            app_count_tuples)])
        print len(apps)  # 213, 37, 20
        print len(apps & apps_in_gan)  # 186, 36, 20


def compare_gan_pans_edges():
    edges_count = {}
    for uid in load_uids():
        for edge in load_pan(uid).edges():
            edges_count.setdefault(edge, 0)
            edges_count[edge] += 1

    edge_count_tuples, edges_in_pans = [], set([])
    for edge, count in edges_count.iteritems():
        edge_count_tuples.append((edge, count))
        edges_in_pans.add(edge)

    # sort by frequency
    edge_count_tuples.sort(key=lambda x: x[1], reverse=True)

    # edges in gan
    edges_in_gan = set(load_gan().edges())

    # total amount
    print len(edges_in_gan), len(edges_in_pans)  # 132841, 9143

    # intersection
    print len(edges_in_gan & edges_in_pans)  # 619 = (9143 - 8524)

    for threshold in [1, 8, 16]:
        edges = set([x[0] for x in filter(
            lambda x: x[1] > threshold,
            edge_count_tuples)])
        print len(edges)  # 1746, 172, 71
        print len(edges & edges_in_gan)  # 185, 17, 6


if __name__ == '__main__':
    pass
