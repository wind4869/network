from utils.stats_funcs import *
from utils.rw_funcs import *
from igraph import *
from math import ceil
from random import choice


# count the connections of each app in
# apps_to_count (in GAN) with all apps in app_set (in PAN)
def count_connections(apps_to_count, app_set):
    count = []
    gan = load_gan()
    for app1 in apps_to_count:
        temp = [app1, 0, 0, 0]  # [app, in_count, out_count, all_count]
        for app2 in app_set:
            if app2 in gan[app1]:
                temp[1] += 1
            if app1 in gan[app2]:
                temp[2] += 1
        temp[3] = temp[1] + temp[2]
        count.append(temp)
    return count


# recommend by the app's connection with all apps in PAN
def recommend_all_connection(apps_in_pan):
    gan = load_gan()

    apps_to_count = set(load_apps()) - apps_in_pan
    count = count_connections(apps_to_count, apps_in_pan)
    count.sort(lambda a, b: b[3] - a[3])

    result = [item[0] for item in count]
    return result


# detect communities in network
def detect_community(network):
    apps = load_all_apps()
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


# create and store communities by uid (uid='gan' for GAN)
def create_community(uid):
    network = load_gan() if uid == 'gan' else load_pan(uid)
    dump_clusters(uid, detect_community(network))


# version for test
def create_community_test(uid, pan):
    dump_clusters(uid, detect_community(pan))


# recommend by the score = (the ratio between PAN's community
# and GAN's community) * (app's connection in community range)
def recommend_community_match(uid):
    app_score = {}
    [app_score.setdefault(app, 0) for app in load_apps()]

    pan_clusters = load_clusters(uid)
    gan_clusters = load_clusters('gan')

    for panc in pan_clusters:
        for ganc in gan_clusters:
            common = set(panc) & set(ganc)
            ratio = len(common) * 1.0 / len(ganc)
            count = count_connections(set(ganc) - set(panc), panc)
            for item in count:
                app_score[item[0]] += item[3] * ratio

    temp = []
    for app, score in app_score.iteritems():
        temp.append([app, score])
    temp.sort(lambda a, b: b[1] - a[1])

    result = [item[0] for item in temp]
    return result


# get training and test set (8/2)
def get_app_dataset(uid):
    apps_in_pan = \
        list(apps_in_network(load_pan(uid)) - set(load_natives()))
    num_test = int(ceil(len(apps_in_pan) / 5.0))
    apps_for_test = set([])
    for i in xrange(num_test):
        app = choice(apps_in_pan)
        apps_in_pan.remove(app)
        apps_for_test.add(app)
    return set(apps_in_pan), apps_for_test


# get dataset for community match method,
# use app test set to filter PAN
def get_dataset(uid):
    training_set, test_set = get_app_dataset(uid)
    pan = load_pan(uid)
    [pan.pop(app) for app in test_set]
    for app in pan: pan[app] -= test_set
    return training_set, test_set, pan


# get precision and recall
def evaluate(uid, topk):
    # training_set, test_set = get_app_dataset(uid)
    # result = recommend_all_connection(training_set)[:topk]

    training_set, test_set, pan = get_dataset(uid)
    create_community_test(uid, pan)
    result = recommend_community_match(uid)[:topk]

    num_hit = len(test_set & set(result))

    print '(1) Training: %s, Test: %s' % (len(training_set), len(test_set))
    print '(2) Top: %s, Hit: %s' % (topk, num_hit)
    print '(3) Precision: %s, Recall: %s' \
          % (num_hit * 1.0 / len(result), num_hit * 1.0 / len(test_set))


if __name__ == '__main__':
    evaluate('F01', 30)
