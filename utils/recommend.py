from utils.stats_funcs import *
from utils.rw_funcs import *
from igraph import *
from math import ceil
from random import choice


# detect communities in GAN
def detect_community_gan():
    gan = load_gan()
    apps = load_all_apps()
    indexes = list(xrange(len(apps)))

    graph = Graph(directed=True)
    graph.add_vertices(indexes)
    graph.vs['label'] = graph.vs['name']
    graph.vs['size'] = [30 for i in xrange(len(graph.vs))]

    for from_app in gan:
        from_index = indexes.index(apps.index(from_app))
        for to_app in gan[from_app]:
            to_index = indexes.index(apps.index(to_app))
            graph.add_edge(from_index, to_index)

    clusters = graph.community_leading_eigenvector()
    dump_clusters(graph, clusters, 'gan')
    # membership = clusters.membership
    # vc = ig.VertexClustering(graph, membership)
    # plot(vc, bbox=(1000, 1000))


# detect communities in PAN
def detect_community_pan(uid):
    all_apps = load_all_apps()
    pan = load_pan(uid)

    apps_in_pan = list(apps_in_network(pan))
    indexes = [all_apps.index(i) for i in apps_in_pan]

    graph = Graph(directed=True)
    graph.add_vertices(indexes)
    graph.vs['label'] = graph.vs['name']
    graph.vs['size'] = [30 for i in xrange(len(graph.vs))]

    for from_app in pan:
        from_index = indexes.index(all_apps.index(from_app))
        for to_app in pan[from_app]:
            to_index = indexes.index(all_apps.index(to_app))
            graph.add_edge(from_index, to_index)

    clusters = graph.community_leading_eigenvector()
    dump_clusters(graph, clusters, uid)
    # membership = clusters.membership
    # vc = VertexClustering(graph, membership)
    # plot(vc, bbox=(1000, 1000))


# recommend by the app's connection with all apps in PAN
def recommend_all_connection(apps_in_pan):
    count_rank = []
    gan = load_gan()

    apps_candidate = set(load_apps()) - apps_in_pan
    for app1 in apps_candidate:
        temp = [app1, 0, 0, 0]  # [app, in_count, out_count, all_count]
        for app2 in apps_in_pan:
            if app2 in gan[app1]:
                temp[1] += 1
            if app1 in gan[app2]:
                temp[2] += 1
        temp[3] = temp[1] + temp[2]
        count_rank.append(temp)

    count_rank.sort(lambda a, b: b[3] - a[3])
    result = [item[0] for item in count_rank]
    return result


# get training and test set (8/2)
def get_dataset(uid):
    apps_in_pan = \
        list(apps_in_network(load_pan(uid)) - set(load_natives()))
    num_test = int(ceil(len(apps_in_pan) / 5.0))
    apps_for_test = set([])
    for i in xrange(num_test):
        app = choice(apps_in_pan)
        apps_in_pan.remove(app)
        apps_for_test.add(app)
    return set(apps_in_pan), apps_for_test


# get precision and recall
def evaluate(uid):
    training_set, test_set = get_dataset(uid)
    result = recommend_all_connection(training_set)[:30]

    num_hit = len(test_set & set(result))

    print '(1) Training: %s, Test: %s' % (len(training_set), len(test_set))
    print '(2) Top: %s, Hit: %s' % (30, num_hit)
    print '(3) Precision: %s, Recall: %s' \
          % (num_hit * 1.0 / len(result), num_hit * 1.0 / len(test_set))


def recommend_test(uid):
    apps = load_all_apps()
    index_clusters = load_clusters(uid)

    app_clusters = []
    for ic in index_clusters:
        print ic
        app_clusters.append([apps[i] for i in ic])

    for apps in app_clusters:
        for app in apps:
            print app,
        print


if __name__ == '__main__':
    # for uid in USER_IDS:
    #     detect_community_pan(uid)
    # recommend_test('F01')
    evaluate('F07')
