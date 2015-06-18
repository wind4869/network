# -*- coding: utf-8 -*-

from filter_stats import *
from utils.funcs_stats import *
from utils.funcs_vector import *


# test the network to see whether it
# meets the power law distribution
def power_law_distribution_test(network):
    degrees = get_degrees(network)
    apps = degrees['in'].keys()
    max_degree = 0
    y = []

    for app in apps:
        for i in xrange(1, len(network) * 2):
            if degrees['in'][app] + degrees['out'][app] >= i:
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
    # the curve of power fun
    draw_plot(x, y,
              'Degrees',
              'The Number of App',
              'Power Law Distribution Test')

    # lny = -rlnx + lnc (linear correlation)
    x = np.array([np.log(i) for i in x])
    y = np.array([np.log(i) for i in y])
    print 'r-value: ', pearson(x, y)


# test to see weather it meets the law of
# "the higher the rank, the bigger the in-degree"
def rank_degree_correlation_test(network):
    x, y = [], []
    apps = load_apps()
    degrees = get_degrees(network)

    for app in [app for app in degrees['in'] if app in load_apps()]:
        degree_in = degrees['in'][app]
        if degree_in > 0:
            x.append(apps.index(app))
            # x.append(likesCount(app))
            # x.append(downloadCount(app))
            y.append(degree_in)

    print 'r-value: ', pearson(x, y)
    draw_plot(x, y,
              'Rank',
              'In-Degree',
              'Rank-Degree Correlation Test',
              'ro')


# calculate the average metric of each category
def cats_avg_metric(metric, xlabel='', title=''):
    apps = [app for app in metric if app in load_apps()]
    cats = load_categories()

    avg_metric = [0 for i in xrange(len(cats))]
    counts = [0 for i in xrange(len(cats))]

    for app in apps:
        for i in xrange(len(cats)):
            if cats[i] in categories(app):
                avg_metric[i] += metric[app]
            counts[i] += 1

    for i in xrange(len(cats)):
        if counts[i]:
            avg_metric[i] = avg_metric[i] * 1.0 / counts[i]

    draw_bar_chart(avg_metric, cats, xlabel, title)


# test to see weather some score of each app
# has correlation with its rank
def rank_score_correlation_test(scores):
    x, y = [], []
    apps = load_apps()
    for app in [app for app in scores if app in apps]:
        if scores[app]:
            x.append(apps.index(app))
            # x.append(likesCount(app))
            # x.append(downloadCount(app))
            y.append(scores[app])
    print 'r-value: ', pearson(x, y)
    draw_plot(x, y,
              'Rank',
              'Score',
              'Rank-Score Correlation Test', 'ro')


# what the fuck ... -_-
def another_rank_score_test():
    apps = load_apps()

    # load data dictionary and tag I/O
    data_dict = load_data_dict()
    tag_io, tag_all = load_tag_io()

    v_fill = get_v_fill(tag_io, data_dict)
    vectors = get_vectors(apps, tag_all, len(data_dict), v_fill)

    inputs, outputs = [], []
    for app in vectors:
        inputs.append(vectors[app]['I'])
        outputs.append(vectors[app]['O'])
    sum_inputs = reduce(lambda a, b: [i + j for i, j in zip(a, b)], inputs)
    sum_outputs = reduce(lambda a, b: [i + j for i, j in zip(a, b)], outputs)
    sum_all = reduce(lambda a, b: [i + j for i, j in zip(a, b)], [sum_inputs, sum_outputs])

    x, y = [], []
    for app in vectors:
        score = 0
        for i in xrange(11):
            if vectors[app]['I'][i]:
                score += sum_all[i]
            if vectors[app]['O'][i]:
                score += sum_all[i]
        if score:
            x.append(likesCount(app))
            y.append(score)

    print len(x)
    print linregress(x, y)
    draw_plot(x, y, 'Rank', 'Score', 'Rank-Score Test')


if __name__ == '__main__':
    network = load_gan()
    # power_law_distribution_test(network)
    # rank_degree_correlation_test(network)
    # cats_avg_metric(get_degrees(network)['in'])
    # rank_score_correlation_test(pickle_load(APP_FILTERS_SCORE))
    filter_frequent_pattern(pickle_load(CODED_LIST))
