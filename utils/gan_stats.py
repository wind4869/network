# -*- coding: utf-8 -*-

import numpy as np
import matplotlib.pyplot as plt
from utils.funcs_rw import *
from scipy.stats import linregress


# get r-value(Pearson correlation coefficient)
# linregress[0] = slope(斜率)
# linregress[1] = intercept(截距)
def pearson(x, y):
    return linregress(x, y)[2]


def scale_and_density(network):
    nodes = network.number_of_nodes()
    edges = network.number_of_edges()
    density = float(edges) / (nodes * (nodes - 1))

    print ' nodes: %d\n edges: %d\n density: %.3f' % \
          (nodes, edges, density)


def degree_histograms(network):
    idict, odict = network.in_degree(), network.out_degree()  # { node: degree, ... }
    ivalues, ovalues = [set(d.values()) for d in idict, odict]
    ihist = [idict.values().count(i) if i in ivalues else 0 for i in xrange(max(ivalues) + 1)]
    ohist = [odict.values().count(i) if i in ovalues else 0 for i in xrange(max(ovalues) + 1)]

    print 'Max In-Degree, Out-Degree: %d, %d' % (max(ivalues), max(ovalues))
    return ihist, ohist, nx.degree_histogram(network)


def power_law_distribution(network):
    ihist, ohist, hist = degree_histograms(network)
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
    plt.title('Power Law Distribution of GAN')
    plt.show()


def degree_distribution(network):
    ihist, ohist, hist = degree_histograms(network)
    ix, ox, x = [range(len(h)) for h in ihist, ohist, hist]
    iy, oy, y = [[i / float(sum(h)) for i in h] for h in ihist, ohist, hist]

    plt.loglog(ix, iy, color='blue', linewidth=2)  # In-Degree
    plt.loglog(ox, oy, color='red', linewidth=2)  # Out-Degree
    # plt.loglog(x, y, color='black', linewidth=2)

    plt.legend(['In-Degree', 'Out-Degree'])
    plt.xlabel('Degree Values')
    plt.ylabel('Frequency of Degrees')
    plt.title('Degree Distribution of GAN')
    plt.show()


def strongly_connected_components(network):
    num = nx.number_strongly_connected_components(network)
    components = nx.strongly_connected_component_subgraphs(network)

    print 'Number of strongly connected components: %d' % num
    for c in components:
        print len(c.number_of_nodes()), c.nodes()


if __name__ == '__main__':
    # gan = load_gan()
    # scale_and_density(gan)
    # power_law_distribution(gan)
    # degree_distribution(gan)
    # strongly_connected_components(gan)
    pass
