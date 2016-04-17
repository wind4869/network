# -*- coding: utf-8 -*-

import numpy as np
import igraph as ig
import pygraphviz as pyv
from scipy.stats import spearmanr

from utils.functions import *


def correlation_analyse():
    rank = []
    for app in load_capps():
        rank.append((app, downloadCount(app)))
    rank = [x[0] for x in sorted(rank, key=lambda x: x[1])]

    lan = load_gan()
    rvalues, pvalues = [], []
    for uid in load_uids():
        lan = load_pan(uid)
        # degrees = lan.in_degree()
        degrees = lan.out_degree()

        x, y = [], []
        for app in degrees:
            if app in load_capps():
                x.append(rank.index(app))
                y.append(degrees[app])

        sp = spearmanr(x, y)
        rvalues.append(sp[0])
        pvalues.append(sp[1])

    print sum(rvalues) / 40, sum(pvalues) / 40


# number of nodes, number of edges and density
def scale_and_density(lan):
    nodes = lan.number_of_nodes()
    edges = lan.number_of_edges()
    density = float(edges) / (nodes * (nodes - 1))
    return nodes, edges, density


def stats_scale_and_density():
    nodes, edges, density = [], [], []
    for uid in load_uids():
        result = scale_and_density(load_pan(uid))
        nodes.append(result[0])
        edges.append(result[1])
        density.append(result[2])

    data = sorted(zip(nodes, edges, density), key=lambda x: x[0])

    x = xrange(len(load_uids()))
    yn, ye, yd = [], [], []
    for t in data:
        yn.append(t[0])
        ye.append(t[1])
        yd.append(t[2])

    f, (ax1, ax2, ax3) = plt.subplots(3, 1, sharex=True)
    print pearson(yn, ye)

    ax1.plot(x, yn, 'ro-', label='Number of Nodes (Used Apps)')
    ax2.plot(x, ye, 'go-', label='Number of Edges (SQ Relations)')
    ax3.plot(x, yd, 'bo-', label='Density')

    ax1.legend(loc=0)
    ax2.legend(loc=0)
    ax3.legend(loc=0)

    plt.xlabel('User Labels')
    # plt.savefig('/Users/wind/Desktop/fig_scale.pdf', format='pdf')
    plt.show()


def degree_histograms(lan):
    idict, odict = lan.in_degree(), lan.out_degree()  # { node: degree, ... }
    ivalues, ovalues = [set(d.values()) for d in idict, odict]
    ihist = [idict.values().count(i) if i in ivalues else 0 for i in xrange(max(ivalues) + 1)]
    ohist = [odict.values().count(i) if i in ovalues else 0 for i in xrange(max(ovalues) + 1)]

    print 'Max In-Degree, Out-Degree: %d, %d' % (max(ivalues), max(ovalues))
    return ihist, ohist, nx.degree_histogram(lan)


def power_law_distribution(lan):
    ihist, ohist, hist = degree_histograms(lan)
    ix, ox, x = [range(len(h)) for h in ihist, ohist, hist]
    iy, oy, y = [[sum(h[i:]) for i in xrange(len(h))] for h in ihist, ohist, hist]

    return pearson(ix, iy)[2], pearson(ox, oy)[2]

    # y = c * x^-r (power function)
    plt.plot(ix, iy, color='blue', linewidth=2)  # In-Degree
    plt.plot(ox, oy, color='red', linewidth=2)  # Out-Degree
    # plt.plot(x, y, color='black', linewidth=2)  # Degree

    # lny = -rlnx + lnc (linear correlation)
    ix, ox, x = [np.array([np.log(i) for i in d[1:]]) for d in ix, ox, x]
    iy, oy, y = [np.array([np.log(i) for i in a[1:]]) for a in iy, oy, y]

    plt.legend(['In Degree', 'Out Degree'])
    plt.xlabel('Degree Values')
    plt.ylabel('Number of Nodes (Apps)')
    # plt.title('Power Law Distribution of GAN')
    # plt.savefig('/Users/wind/Desktop/fig_degree.pdf', format='pdf')
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


# get pan communities using igraph
def pan_community_detection(uid):
    graph = convert_to_igraph(uid)
    # graph.vs['label'] = graph.vs['id']
    graph.vs['size'] = [30 for i in xrange(len(graph.vs))]

    # two kinds of methods for directed graph
    clusters = graph.community_spinglass()  # could get higher modularity
    # clusters = pan.community_edge_betweenness().as_clustering()

    membership = clusters.membership
    vc = ig.VertexClustering(graph, membership)

    result = []
    for c in vc:
        result.append([graph.vs[i]['id'] for i in c])

    scale = sum([len(c) for c in result]) / float(len(result))

    # draw communities
    # ig.plot(vc, bbox=(1000, 1000))

    return len(result), scale, clusters.modularity


def compare_pan_community():
    data = []
    uids = [u for u in load_uids() if u not in ['a2', 'd5']]
    for uid in uids:
        data.append((load_pan(uid).number_of_nodes(), pan_community_detection(uid)))

    data = sorted(data, key=lambda x: x[0])
    data = sorted(data, key=lambda x: x[1][0])

    x = xrange(len(uids))
    yq, ys, ym = [], [], []
    for t in data:
        yq.append(t[1][0])
        ys.append(t[1][1])
        ym.append(t[1][2])

    f, (ax1, ax2, ax3) = plt.subplots(3, 1, sharex=True)

    ax1.plot(x, yq, 'ro-', label='Number of Communities')
    ax2.plot(x, ys, 'go-', label='Average Size')
    ax3.plot(x, ym, 'bo-', label='Modularity Values')

    ax1.legend(loc=0)
    ax2.legend(loc=0)
    ax3.legend(loc=0)

    plt.savefig('/Users/wind/Desktop/figure.pdf', format='pdf')
    plt.show()


# get gan communities using igraph
def gan_community_detection():
    gan = load_gan()
    graph = ig.Graph(directed=True)
    graph.add_vertices(load_apps())

    elist = []
    for e in gan.edges():
        u, v = e
        w = float(gan[u][v]['weight'])
        elist.append((u, v, w))

    # write networkx to file
    graph = nx.DiGraph()
    graph.add_weighted_edges_from(elist)
    nx.write_graphml(graph, GRAPHML_PATH)

    # read file to construct igraph
    graph = ig.Graph.Read_GraphML(GRAPHML_PATH)
    graph.vs['size'] = [10 for i in xrange(len(graph.vs))]

    clusters = graph.community_spinglass()
    membership = clusters.membership
    vc = ig.VertexClustering(graph, membership)

    result = []
    for c in vc:
        result.append(set([graph.vs[i]['id'] for i in c]))

    ig.plot(vc, bbox=(2400, 1400))
    return result, clusters.modularity


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

    return filter(lambda x: x[1] > 16, edge_count_tuples)

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


def compare_gan_pan_each(uid):
    napps = load_napps()
    edges_in_gan, edges_in_pan = set([]), set([])

    for edge in load_gan().edges():
        if edge[0] not in napps and edge[1] not in napps:
            edges_in_gan.add(edge)

    # print len(load_gan().edges()), len(edges_in_gan)

    for edge in load_pan(uid).edges():
        if edge[0] not in napps and edge[1] not in napps:
            edges_in_pan.add(edge)

    intersection = edges_in_gan & edges_in_pan

    return float(len(intersection)) / len(edges_in_gan), \
        float(len(intersection)) / len(edges_in_pan)

    # AVG: 30.925, 379.225, 0.000232797103304, 0.0865941750097
    # AVG(ratio of edges formed by native APPs): 0.629188264373


def compare_gan_pan_all():
    data = [(0.0003989762119843421, 0.06743002544529263), (1.5055706112616681e-05, 0.1), (6.775067750677507e-05, 0.125), (0.00012044564890093345, 0.13559322033898305), (0.00042155977115326706, 0.15864022662889518), (0.00034628124059018367, 0.1619718309859155), (0.00024841915085817523, 0.16751269035532995), (0.00013550135501355014, 0.18181818181818182), (0.00013550135501355014, 0.18181818181818182), (0.0002032520325203252, 0.1875), (0.0004742547425474255, 0.19090909090909092), (0.0003613369467028004, 0.19123505976095617), (0.00022583559168925022, 0.19230769230769232), (0.00038392050587172537, 0.19391634980988592), (0.00037639265281541704, 0.19455252918287938), (0.0005420054200542005, 0.19672131147540983), (0.00018819632640770852, 0.20161290322580644), (0.0001656127672387835, 0.21568627450980393), (0.0005344775669978922, 0.21712538226299694), (0.00014302920806985846, 0.22093023255813954), (0.00013550135501355014, 0.23076923076923078), (0.00018819632640770852, 0.23809523809523808), (9.03342366757001e-05, 0.24), (0.00027100271002710027, 0.2465753424657534), (0.0004893104486600421, 0.24714828897338403), (0.0002032520325203252, 0.24770642201834864), (0.00015808491418247515, 0.25), (0.00010538994278831677, 0.25925925925925924), (0.00023336344474555857, 0.28440366972477066), (5.269497139415838e-05, 0.2916666666666667), (0.0006775067750677507, 0.29508196721311475), (0.0002032520325203252, 0.3103448275862069), (0.0002183077386329419, 0.31521739130434784), (6.0222824450466725e-05, 0.32), (0.00027100271002710027, 0.36363636363636365), (0.00015055706112616682, 0.36363636363636365), (8.280638361939175e-05, 0.3793103448275862), (0.00015055706112616682, 0.4444444444444444), (6.0222824450466725e-05, 0.47058823529411764), (2.2583559168925024e-05, 0.75)]

    x = xrange(len(load_uids()))
    yp, yg = [], []
    for t in data:
        yg.append(t[0] * 100)
        yp.append(t[1] * 100)

    fig, ax1 = plt.subplots()
    ax1.plot(x, yp, 'ro-', label='Ratios of Common Edges in PAN')
    ax1.set_xlabel('User Labels')
    ax1.set_ylabel('Ratios of Common Edges in PAN (%)')
    ax1.legend(loc=(0.02, 0.8))

    ax2 = ax1.twinx()
    ax2.plot(x, yg, 'bs-', label='Ratios of Common Edges in GAN')
    ax2.set_ylabel('Ratios of Common Edges in GAN (%)')
    ax2.legend(loc=(0.02, 0.9))

    # plt.savefig('/Users/wind/Desktop/fig_percentage.pdf', format='pdf')
    plt.show()


def edges_in_gan_not_in_pan():
    gan = load_gan()
    edge_count_tuples = []
    for edge in gan.edges():
        edge_count_tuples.append((edge, gan[edge[0]][edge[1]]['weight']))

    edge_count_tuples.sort(key=lambda x: x[1], reverse=True)

    result = set([])
    for uid in load_uids():
        pan = load_pan(uid)
        nodes_in_pan, edges_in_pan = pan.nodes(), pan.edges()

        for tuple in edge_count_tuples:
            e = tuple[0]
            if e[0] in nodes_in_pan \
                    and e[1] in nodes_in_pan \
                    and e not in edges_in_pan \
                    and tuple[1] >= 2:
                result.add(tuple)

    result = sorted(result, key=lambda x: x[1], reverse=True)
    print len(result), result


def draw_comparison_graphs(l1, l2):

    mapdict = {
        u'com.youdao.dict': u'Youdao Dictionary',
        u'cn.wps.moffice_eng': u'WPS Office',
        u'com.sina.weibo': u'Sina Weibo',
        u'com.sankuai.meituan': u'Meituan',
        u'com.taobao.taobao': u'Taobao',
        u'com.UCMobile': u'UC Browser',
        u'com.baidu.tieba': u'Baidu Tieba',
        u'com.qiyi.video': u'Qiyi Video',
        u'com.tencent.mm': u'WeChat',
        u'com.eg.android.AlipayGphone': u'Alipay',
        u'com.tencent.mobileqq': u'QQ'
    }

    def myTitleEn(app):
        if app in mapdict:
            return mapdict[app]
        else:
            return '@' + app.split('.')[2].capitalize()

    gan = load_gan()
    # graph = pyv.AGraph(directed=True, strict=True, rankdir='LR')
    graph = pyv.AGraph(directed=True)

    for tuple in l1:
        e, v = tuple
        weights = gan[e[0]][e[1]]['weights']

        label = ''
        if weights[0] or weights[1]: label += '[IR]'
        elif weights[2] or weights[3]: label += '[SM]'
        if weights[4]: label += '[SR]'

        label = '%.2f%s' % (v / float(40), label)
        graph.add_edge(myTitleEn(e[0]), myTitleEn(e[1]),
                       label=label, style='bold')

    for tuple in l2:
        e, v = tuple
        graph.add_edge(myTitleEn(e[0]), myTitleEn(e[1]),
                       label='%.2f' % (v / float(40)), color='red', style='dashed')
        # graph.add_edge(myTitleEn(e[0]), myTitleEn(e[1]),
        #                label='%.2f' % (v / float(40)), style='bold')

    graph.layout(prog='dot')
    # graph.draw('/Users/wind/Desktop/fig_difference.pdf', format='pdf')
    # graph.draw('/Users/wind/Desktop/fig_commonness.pdf', format='pdf')


def compare_similarity():
    uids = ['l1', 'a13', 'f5', 'a6', 'f2', 'd7', 'g1', 'f6', 'g8', 'f4', 'a11', 'f1', 'a7', 'd9', 'd2', 'd6', 'a17', 'g2', 'a1', 'a10', 'd5', 'a9', 'a8', 'w2', 'a3', 'd4', 'g4', 'd8', 'n4', 'a2', 'a12', 'f3', 'n2', 'n5', 'd10', 'd3', 'g6', 'a15', 'a14', 'g7']
    data = []
    for u1 in uids:
        pan1 = load_pan(u1)
        temp = []
        for u2 in uids:
            temp.append(g_sim(pan1, load_pan(u2)))
        data.append(temp)

    # print np.array(data)

    fig, ax = plt.subplots()
    im = ax.imshow(data, cmap=plt.cm.Reds, interpolation='nearest')
    # ax.set_title('Similarity Comparison')

    # Move left and bottom spines outward by 10 points
    ax.spines['left'].set_position(('outward', 10))
    ax.spines['bottom'].set_position(('outward', 10))
    # Hide the right and top spines
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)
    # Only show ticks on the left and bottom spines
    ax.yaxis.set_ticks_position('left')
    ax.xaxis.set_ticks_position('bottom')

    plt.xlabel('User Labels')
    plt.ylabel('User Labels')

    plt.colorbar(im)
    # plt.savefig('/Users/wind/Desktop/fig_similarity.pdf', format='pdf')
    plt.show()


def personality_degree(uid_base):
    pan_base = load_pan(uid_base)

    result = 0
    for uid in [uid for uid in load_uids() if uid != uid_base]:
        pan = load_pan(uid)
        result += 1 / g_sim(pan_base, pan)  # PAY ATTENTION!!!

    return result / (len(load_uids()) - 1)


def personal_pattern(uid_base):
    edges_count = {}
    for uid in load_uids():
        for edge in load_pan(uid).edges():
            edges_count.setdefault(edge, 0)
            edges_count[edge] += 1

    pan_base = load_pan(uid_base)
    edges_weight_tuples = []
    for e in pan_base.edges():
        edges_weight_tuples.append((e, pan_base[e[0]][e[1]]['weight']))

    result = filter(lambda x: edges_count[x[0]] < 8 and x[1] > 10, edges_weight_tuples)

    graph = pyv.AGraph(directed=True, strict=True, rankdir='LR')
    for tuple in result:
        e, v = tuple
        graph.add_edge(title(e[0]), title(e[1]), label=v, style='bold')

    # graph.layout(prog='dot')
    # graph.draw('/Users/wind/Desktop/personal_%s.jpg' % uid_base, format='jpg')

    return result


def subpattern(uid):
    mapdict = {
        u'com.youdao.dict': u'Youdao Dictionary',
        u'cn.wps.moffice_eng': u'WPS Office',
        u'com.sina.weibo': u'Sina Weibo',
        u'com.sankuai.meituan': u'Meituan',
        u'com.taobao.taobao': u'Taobao',
        u'com.UCMobile': u'UC Browser',
        u'com.baidu.tieba': u'Baidu Tieba',
        u'com.qiyi.video': u'Qiyi Video',
        u'com.tencent.mm': u'WeChat',
        u'com.eg.android.AlipayGphone': u'Alipay',
        u'com.tencent.mobileqq': u'QQ',
        u'com.baidu.netdisk': u'Baidu Netdisk',
        u'com.nowcoder.app.florida': u'Nowcoder',
        u'com.duokan.reader': u'Duokan Reader'
    }

    def myTitleEn(app):
        if app in mapdict:
            return mapdict[app]
        else:
            return '@' + app.split('.')[2].capitalize()

    edges_count = {}
    for u in load_uids():
        for edge in load_pan(u).edges():
            edges_count.setdefault(edge, 0)
            edges_count[edge] += 1

    pan = load_pan(uid)
    edges_weight_tuples = []
    for e in pan.edges():
        edges_weight_tuples.append((e, pan[e[0]][e[1]]['weight']))

    result = filter(lambda x: x[1] > 10, edges_weight_tuples)
    # result1 = filter(lambda x: edges_count[x[0]] < 8 and x[1] > 10, edges_weight_tuples)
    # result2 = filter(lambda x: edges_count[x[0]] >= 8 and x[1] > 10, edges_weight_tuples)
    #
    # graph = pyv.AGraph(directed=True, strict=True, rankdir='LR')
    # for tuple in result1:
    #     e, v = tuple
    #     if myTitleEn(e[0]) != 'Nowcoder':
    #         graph.add_edge(myTitleEn(e[0]), myTitleEn(e[1]), label=v, color='red', style='bold')
    # for tuple in result2:
    #     e, v = tuple
    #     if myTitleEn(e[1]) != 'Sina Weibo':
    #         graph.add_edge(myTitleEn(e[0]), myTitleEn(e[1]), label=v)
    #
    # graph.layout(prog='dot')
    # graph.draw('/Users/wind/Desktop/subpattern_%s.pdf' % uid, format='pdf')

    return result


def compare_personality():
    data = []
    for uid in load_uids():
        data.append((personality_degree(uid), len(personal_pattern(uid))))

    data = sorted(data, key=lambda x: x[0])

    x = xrange(len(load_uids()))
    yd, ys = [], []
    for t in data:
        yd.append(t[0])
        ys.append(t[1])

    fig = plt.figure()
    ax1 = fig.add_subplot(111)
    ax1.plot(x, yd, 'ro-', label='Degree')
    ax1.legend(loc=0)

    ax2 = ax1.twinx()
    ax2.plot(x, ys, 'bo-', label='Scale')
    ax2.legend(loc=9)

    # fig = plt.figure()
    # ax1 = fig.add_subplot(212)
    # ax2 = fig.add_subplot(211)
    #
    # ax1.plot(x, yd, 'ro-', label='Degree')
    # ax2.plot(x, ys, 'bo-', label='Scale')
    #
    # ax1.legend(loc=0)
    # ax2.legend(loc=0)

    plt.show()


def compare_pattern():
    data = []
    for uid in load_uids():
        data.append((len(subpattern(uid)), len(personal_pattern(uid))))

    data = sorted(data, key=lambda x: x[0])

    x = xrange(len(load_uids()))
    ys, yp = [], []
    for t in data:
        ys.append(t[0])
        yp.append(t[1])

    print pearson(ys, yp)

    plt.plot(x, ys, 'ro-', label='| FP |')
    plt.plot(x, yp, 'bs-', label='| PP |')
    plt.xlabel('User Labels')
    plt.ylabel('Number of Edges')
    plt.legend(loc=0)
    # plt.savefig('/Users/wind/Desktop/fig_pattern.pdf', format='pdf')
    plt.show()


def titleEn(app):
    import json
    return json.loads(open(DETAIL_PATH % app).read())['titleEn']


if __name__ == '__main__':
    stats_scale_and_density()
    # compare_pan_community()
    # correlation_analyse()
    power_law_distribution(load_gan())

    compare_gan_pan_all()
    compare_similarity()
    # compare_personality()
    compare_pattern()

    # data for 'fig_difference.pdf'
    # l2 = [((u'com.tencent.mm', u'com.eg.android.AlipayGphone'), 23), ((u'com.tencent.mobileqq', u'com.eg.android.AlipayGphone'), 21), ((u'com.tencent.mobileqq', u'com.UCMobile'), 18), ((u'com.eg.android.AlipayGphone', u'com.tencent.mobileqq'), 18), ((u'com.tencent.mm', u'com.UCMobile'), 18), ((u'com.tencent.mobileqq', u'com.taobao.taobao'), 16), ((u'com.taobao.taobao', u'com.tencent.mobileqq'), 15), ((u'com.tencent.mm', u'com.taobao.taobao'), 15), ((u'com.tencent.mm', u'cn.wps.moffice_eng'), 10), ((u'com.tencent.mm', u'com.sankuai.meituan'), 9)]
    # draw_comparison_graphs(l1, l2)

    # subpattern('l1')
    # subpattern('f2')

    # graph = pyv.AGraph(LAN_DIR + 'pan_a3.dot')
    # graph.layout(prog='dot')
    # graph.draw('/Users/wind/Desktop/fig_difference.pdf', format='pdf')
