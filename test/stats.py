# -*- coding: utf-8 -*-

import numpy as np
import matplotlib.pyplot as plt
from utils.data_read_store import *
from scipy.stats import linregress


def draw_plot(x, y, xlabel='', ylabel='', title=''):
    plt.plot(x, y, 'ro-')
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.title(title)
    plt.show()


# get the in and out degree of each app
def get_degrees(network):
    apps = network[0].iterkeys()
    degrees = {}

    for app in apps:
        degree = {}
        degree['out'] = len(network[0][app])
        degree['in'] = len(network[1][app])
        degrees[app] = degree

    return degrees


# test the network to see whether it
# meets the power law distribution
def power_law_distribution(network):
    degrees = get_degrees(network)
    max_degree = 0
    y = []

    for app in degrees:
        for i in xrange(1, len(network[0]) * 2):
            if degrees[app]['in'] + degrees[app]['out'] >= i:
                if i > len(y):
                    y.append(1)
                else:
                    y[i - 1] += 1
            else:
                if i > max_degree:
                    max_degree = i
                break

    # y = c * x^-r (power function)
    x = xrange(1, max_degree)
    draw_plot(x, y)  # the curve of power fun

    # lny = -rlnx + lnc (linear correlation)
    x = np.array([np.log(i) for i in x])
    y = np.array([np.log(i) for i in y])
    # slope(斜率), intercept(截距),
    # r-value(Pearson correlation coefficient)
    print linregress(x, y)[:3]


# test to see weather it meets the law of
# "the higher the rank, the bigger the in degree"
def rank_degree_correlation(network):
    apps = load_apps(len(network[0]))
    degrees = get_degrees(network)
    x, y = [], []

    for app in apps:
        degree_in = degrees[app]['in']
        if degree_in > 0:
            x.append(apps.index(app))
            y.append(degree_in)

    draw_plot(x, y)


# calculate the average degree of each category
def cats_avg_degree(network):
    cats = load_categories()
    apps = load_apps(len(network[0]))
    degrees = get_degrees(network)

    avg_degrees = [0 for i in xrange(len(cats))]
    counts = [0 for i in xrange(len(cats))]

    for app in apps:
        for i in xrange(len(cats)):
            if cats[i] in categories(app):
                avg_degrees[i] += (degrees[app]['in'] + degrees[app]['out'])
            counts[i] += 1

    for i in xrange(len(cats)):
        if counts[i]:
            avg_degrees[i] = avg_degrees[i] * 1.0 / counts[i]

    # draw the bar chart
    y_pos = np.arange(len(cats))
    plt.barh(y_pos, avg_degrees, align='center', alpha=0.4)
    plt.yticks(y_pos, cats)
    plt.xlabel('Average degree')
    plt.title('The average degrees of each category')
    plt.show()


# get the filters rank list to see which is hot
def filters_rank():
    count = {}
    f = open(FILTERS_MATCHED)
    for line in f.readlines():
        filter = line.strip()
        if filter in count:
            count[filter] += 1
        else:
            count[filter] = 1
    f.close
    rank = list(count.iteritems())
    rank.sort(lambda a, b: a[1] - b[1])
    return rank


if __name__ == '__main__':
    # network = get_network(2)
    # power_law_distribution(network)
    # rank_degree_correlation(network)
    # cats_avg_degree(network)
    print filters_rank()[-10:]