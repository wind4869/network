# -*- coding: utf-8 -*-

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
                temp[1] += gan[app2][app1]['weight']
            if gan.has_edge(app1, app2):
                temp[2] += gan[app1][app2]['weight']
        temp[3] = temp[1] + temp[2]
        result.append(temp)
    return result


# Method 1st: recommend by the app's degree with all apps in PAN
def recommend_degree_sum(apps_in_pan):
    gan = load_gan()

    apps_gan = set(load_capps()) - apps_in_pan
    count = count_degrees(apps_gan, apps_in_pan)
    count = sorted(count, key=lambda x: x[3], reverse=True)

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


# Method 2nd: recommend by the community matching score:
# (the ratio between PAN's community and GAN's community) *
# (app's connection in community range)
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


# compute similarity of two graphs
def g_sim(pan1, pan2):
    mnodes = max(pan1.number_of_nodes(), pan2.number_of_nodes())
    mcs = 0

    for app_from, app_to in pan1.edges():
        if pan2.has_edge(app_from, app_to):
            mcs += pan1[app_from][app_to]['weights'][INDEX.USG] + \
                   pan2[app_from][app_to]['weights'][INDEX.USG]

    return mcs * 1.0 / mnodes


# get neighbors of node in directed graph
def neighbors(g, node):
    return g.successors(node) + g.predecessors(node)


# Method 3rd: use u2 to recommend for u1
def recommend_pan_compare(u1, u2):
    result = {}

    pan1, pan2 = [load_pan(u) for u in u1, u2]
    apps1, apps2 = [pan.nodes() for pan in pan1, pan2]
    apps = set(apps1) & set(apps2)
    if not apps:
        return {}

    sim = g_sim(pan1, pan2)
    if not sim:
        return {}

    # the score is: Σ(sim * weight)
    for app in apps:
        for neighbor in neighbors(pan2, app):
            if neighbor not in apps1:
                result.setdefault(neighbor, 0)
                if pan2.has_edge(app, neighbor):
                    result[neighbor] += sim * pan2[app][neighbor]['weights'][INDEX.USG]
                if pan2.has_edge(neighbor, app):
                    result[neighbor] += sim * pan2[neighbor][app]['weights'][INDEX.USG]

    temp = []
    for app, score in result.iteritems():
        temp.append([app, round(score, 2)])

    return sorted(temp, key=lambda x: x[1], reverse=True)


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


def get_rating():
    userapps = load_userapps()
    ratings = [[0 for i in xrange(len(userapps))] for j in xrange(NUM_USER)]
    cnts = [0 for i in xrange(NUM_USER)]

    for r in usageRecords.find():
        user, item, cnt = [r[k] for k in 'user', 'item', 'cnt']
        ratings[user][userapps.index(item)] += cnt
        cnts[user] += cnt

    f_train = open(TRAIN_SET, 'w')
    f_test = open(TEST_SET, 'w')

    for i in xrange(NUM_USER):
        for j in xrange(len(userapps)):
            ratings[i][j] /= float(cnts[i])
            f_target = f_train if ratings[i][j] else f_test
            f_target.write('%d %d %f\n' % (i, j, ratings[i][j]))

    f_train.close()
    f_test.close()


def model_training():
    run(TRAIN_CMD)


def recmommend_matrix_factorize():
    model_training()
    run(PREDICT_CMD)

if __name__ == '__main__':
    # evaluate('F02', 30)
    pass
    # get_rating()
    # recmommend_matrix_factorize()

    userapps = load_userapps()
    ratings = [[0 for i in xrange(len(userapps))] for j in xrange(NUM_USER)]

    f = open_in_utf8(OUTPUT)
    for line in f.readlines():
        temp = line.strip().split()
        user = int(temp[0])
        item = int(temp[1])
        rating = float(temp[2])
        ratings[user][item] = rating
    f.close()

    for i in xrange(NUM_USER):
        pass

