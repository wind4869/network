# -*- coding: utf-8 -*-

from utils.funcs_stats import *
from utils.funcs_rw import *
from igraph import *
from math import ceil
from random import choice


# count the degrees of each app in
# apps_gan with all apps in apps_pan
def count_degrees(apps_gan, apps_pan):
    result = []
    gan = load_gan()
    for app1 in apps_gan:
        temp = [app1, 0, 0, 0]  # [app, in_degree, out_degree, degree]
        for app2 in apps_pan:
            if gan.has_edge(app2, app1):
                temp[1] += 1
            if gan.has_edge(app1, app2):
                temp[2] += 1
        temp[3] = temp[1] + temp[2]
        result.append(temp)
    return result


# recommend by the app's degree with all apps in PAN
def recommend_degree_sum(apps_in_pan):
    gan = load_gan()

    apps_gan = set(load_capps()) - apps_in_pan
    count = count_degrees(apps_gan, apps_in_pan)
    count.sort(lambda a, b: b[3] - a[3])

    result = [item[0] for item in count]
    return result


# detect communities in network
def detect_community(network):
    apps = load_apps()
    indexes = [apps.index(i) for i in apps_in_network(network)]

    graph = Graph(directed=True)
    graph.add_vertices(indexes)
    graph.vs['label'] = graph.vs['name']
    graph.vs['size'] = [30 for i in xrange(len(graph.vs))]

    for from_app in network:
        from_index = indexes.index(apps.index(from_app))
        for to_app in network[from_app]:
            to_index = indexes.index(apps.index(to_app))
            graph.add_edge(from_index, to_index)

    clusters = graph.community_leading_eigenvector()

    # membership = clusters.membership
    # vc = ig.VertexClustering(graph, membership)
    # plot(vc, bbox=(1000, 1000))

    result = []
    [result.append([graph.vs[i]['name'] for i in c]) for c in clusters]
    return result


# create and store communities by uid (uid='gans' for GAN)
def create_community(uid):
    network = load_gan() if uid == 'gan' else load_pan(uid)
    dump_clusters(uid, detect_community(network))


# version for tests
def create_community_test(uid, pan):
    dump_clusters(uid, detect_community(pan))


# recommend by the score: (the ratio between PAN's community
# and GAN's community) * (app's connection in community range)
def recommend_community_match(uid):
    app_score = {}
    apps = load_apps()
    [app_score.setdefault(app, 0) for app in apps]

    pan_clusters = load_clusters(uid)
    gan_clusters = load_clusters('gans')

    for panc in pan_clusters:
        for ganc in gan_clusters:
            common = set(panc) & set(ganc)
            ratio = len(common) * 1.0 / len(ganc)
            apps_to_count = [apps[i] for i in set(ganc) - set(panc)]
            app_set = [apps[i] for i in panc]
            count = count_degrees(apps_to_count, app_set)
            for item in count:
                app_score[item[0]] += item[3] * ratio

    temp = []
    for app, score in app_score.iteritems():
        temp.append([app, score])
    temp = sorted(temp, key=lambda x: x[1], reverse=True)

    result = [item[0] for item in temp]
    return result


# get training and test set (8/2)
def get_dataset(uid):
    pan = load_pan(uid)

    # remove native apps
    training_set = set(pan.nodes()) - set(load_napps())
    test_set = set([])

    # the number of apps should in test set
    num_test = int(ceil(len(training_set) / 5.0))

    # randomly create two sets
    for i in xrange(num_test):
        app = choice(list(training_set))
        training_set.remove(app)
        test_set.add(app)

    return training_set, \
        test_set, \
        nx.subgraph(pan, training_set)


# get precision and recall
def evaluate(uid, topk):
    training_set, test_set, pan = get_dataset(uid)
    # create_community_test(uid, pan)  # create community using training set

    def display(num_hit, result):
        print '(1) Training: %s, Test: %s' % (len(training_set), len(test_set))
        print '(2) Top: %s, Hit: %s' % (topk, num_hit)
        print '(3) Precision: %s, Recall: %s' \
            % (num_hit * 1.0 / len(result), num_hit * 1.0 / len(test_set))

    print '> Method 1st: Recommend by degree sum'
    result = recommend_degree_sum(training_set)[:topk]
    num_hit = len(test_set & set(result))
    display(num_hit, result)

    # print '> Method 2nd: Recommend by community match'
    # result = recommend_community_match(uid)[:topk]
    # num_hit = len(test_set & set(result))
    # display(num_hit, result)


if __name__ == '__main__':
    evaluate('F02', 30)
