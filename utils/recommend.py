from utils.stats_funcs import *
from utils.rw_funcs import *
from igraph import *


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
    for uid in USER_IDS:
        detect_community_pan(uid)
    recommend_test('F01')
