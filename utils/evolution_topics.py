# -*- coding: utf-8 -*-

import jieba
import numpy as np
from numpy import array
from gensim import corpora, models
from sklearn.cluster import KMeans
from BeautifulSoup import BeautifulSoup

from utils.fp_apriori import *
from utils.evolution_networks import *
from utils.bm25 import BM25


def raw_desc(app, v):
    raws = []
    soup = BeautifulSoup(open(HTML_PATH % (app, v)))

    for pre in soup.findAll('pre'):
        raws.append(pre.text)

    if len(raws) < 2:
        raws.append('')

    return raws


def preproccess(raw):

    # step 1. word segmentation
    word_list = list(jieba.cut(raw, cut_all=False))

    # step 2. remove common stop words
    stoplist = load_content(STOPLIST_TXT)
    word_list = [word for word in word_list if word not in stoplist and len(word) > 1]

    # step 3. remove words that appear only once
    # frequency = defaultdict(int)
    # for word in word_list:
    #     frequency[word] += 1
    # word_list = [word for word in word_list if frequency[word] > 1]

    return word_list


def train_lda(apps, num_topics):

    train_set = []
    for app in apps:
        for v in get_versions(app):
            # raw = raw_desc(app, v)[1]  # only use update desc
            raw = ''.join(raw_desc(app, v))  # use all desc
            if not raw:
                continue
            train_set.append(preproccess(raw))

    dictionary = corpora.Dictionary(train_set)
    dictionary.save(DESC_DICT)  # store the dictionary, for future reference

    corpus = [dictionary.doc2bow(text) for text in train_set]
    corpora.MmCorpus.serialize(CORPUS_MM, corpus)

    tfidf = models.TfidfModel(corpus, id2word=dictionary)
    corpus_tfidf = tfidf[corpus]
    tfidf.save(TFIDF_MODEL)

    lda = models.LdaModel(corpus_tfidf, id2word=dictionary, num_topics=num_topics)
    lda.save(LDA_MODEL)  # store to disk, for later use

    # print each topic
    for i in xrange(num_topics):
        print lda.print_topic(i)


def predict_lda_each(app, v, dictionary, lda):

    raw = raw_desc(app, v)[1]  # only use update desc
    # raw = ''.join(raw_desc(app, v))  # use all desc

    if raw:
        vector = [0 for i in xrange(lda.num_topics)]
        word_list = preproccess(raw)
        doc_bow = dictionary.doc2bow(word_list)

        for t in lda[doc_bow]:
            index, probability = t
            vector[index] = probability

        return vector
    else:
        return None


def predict_lda(app):

    dictionary = corpora.Dictionary.load(DESC_DICT)
    lda = models.LdaModel.load(LDA_MODEL)

    data, versions = [], []
    for v in get_versions(app):
        vector = predict_lda_each(app, v, dictionary, lda)
        if vector:
            data.append(vector)
            versions.append(v)

    # heat_map(map(list, zip(*data)), 'Version Labels', 'Topic Labels', app)
    return data  # , versions


def print_lda():

    lda = models.LdaModel.load(LDA_MODEL)
    for i in xrange(lda.num_topics):
        print i, lda.print_topic(i)


def train_word2vec(apps, num_topics):

    train_set = []
    for app in apps:
        for v in get_versions(app):
            train_set.append(preproccess(''.join(raw_desc(app, v))))

    # train a word2vec model
    word2vec = models.Word2Vec(train_set)

    # initialize a k-means object and use it to extract centroids
    kmeans_clustering = KMeans(num_topics)
    idx = kmeans_clustering.fit_predict(word2vec.syn0)

    # create a word / index (cluster number) dictionary
    word_centroid_map = dict(zip(word2vec.index2word, idx))

    # one cluster for one topic
    topics = [[] for i in xrange(num_topics)]
    for word, index in word_centroid_map.iteritems():
        topics[index].append(word)

    # store topics
    pickle_dump(topics, WORD2VEC)

    # print each topic
    print_word2vec()


def print_word2vec():
    topics = pickle_load(WORD2VEC)
    for i in xrange(len(topics)):
        print i, ','.join(topics[i])


def predict_tfidf(app):

    dictionary = corpora.Dictionary.load(DESC_DICT)
    tfidf = models.TfidfModel.load(TFIDF_MODEL)
    topics = pickle_load(WORD2VEC)
    num = len(topics)

    data = []
    for v in get_versions(app):
        raw = raw_desc(app, v)[1]
        if not raw:
            continue

        tfidf_dict = {}
        corpus = dictionary.doc2bow(preproccess(raw))
        for index, score in tfidf[corpus]:
            tfidf_dict[index] = score

        temp = []
        for i in xrange(num):
            score = 0
            for word in topics[i]:
                score += tfidf_dict.get(dictionary.token2id[word], 0)
            temp.append(score / float(len(topics[i])))
        data.append(temp)

    heat_map(map(list, zip(*data)), 'Version Labels', 'Topic Labels', app)


def predict_bm25(app):
    docs = [preproccess(''.join(raw_desc(app, v))) for v in get_versions(app)]
    bm25 = BM25(docs)

    topics = pickle_load(WORD2VEC)
    num = len(topics)

    data = []
    for t in topics:
        scores = bm25.bm25_score(t)
        data.append([x if x > 0 else 0 for x in scores])

    heat_map(data, 'Version Labels', 'Topic Labels', app)
    return data


def sim_neighbors():

    data_topics = [predict_bm25(app) for app in load_eapps()]
    data_versions = map(list, zip(*data_topics))

    y = []
    for i in xrange(1, len(data_versions)):
        y.append(sim_cosine(data_versions[i - 1], data_versions[i]))

    x = xrange(len(data_versions) - 1)

    plt.plot(x, y, 'ro-')
    plt.show()


def k_means(data, num_clusters=5):

    count = 0
    result_tuples = []

    kmeans_clustering = KMeans(num_clusters)
    for i in kmeans_clustering.fit_predict(data):
        result_tuples.append((count, i))
        count += 1

    clusters = [[] for i in xrange(num_clusters)]
    for number, index in result_tuples:
        clusters[index].append(number)

    return clusters


def cluster_version_each(app, num_clusters=5):

    data_versions = predict_lda(app)
    num_versions = len(data_versions)

    if num_versions < num_clusters:
        return None

    count = 0
    result_tuples = []

    kmeans_clustering = KMeans(num_clusters)
    data = [[0 for i in xrange(num_versions)] for j in xrange(num_clusters)]

    for i in kmeans_clustering.fit_predict(data_versions):
        result_tuples.append((count, i))
        data[i][count] = 1
        count += 1

    clusters = [[] for i in xrange(num_clusters)]
    for number, index in result_tuples:
        clusters[index].append(number)

    return clusters

    # heat_map(data, 'Version Labels', 'Cluster Labels', app)


def cluster_version():

    data = []

    for app in load_eapps():
        result = cluster_version_each(app)
        if result:
            total = reduce(lambda a, b: a + b, [len(i) for i in result])
            data.append([len(i) / float(total) for i in result])

    plt.imshow(map(list, zip(*data)), cmap=plt.cm.Greys, interpolation='nearest')

    plt.grid()
    plt.xlabel('App Labels')
    plt.ylabel('Cluster Labels')

    plt.savefig(FIGURE_PATH % 'topic_version', format='pdf')
    plt.show()


def compare_wechat_alipay():

    data = []

    wechat = predict_lda(apps[1])
    alipay = predict_lda(apps[2])

    vd_wechat = get_version_date(apps[1])
    vd_alipay = get_version_date(apps[2])

    for u in wechat[0]:
        temp = []
        for v in alipay[0]:
            temp.append(sim_cosine(u, v))
        data.append(temp)

    plt.figure(figsize=(16, 9))
    im = plt.imshow(data, cmap=plt.cm.Greys, interpolation='nearest')

    plt.xticks(xrange(len(alipay[1])), [vd_alipay[str(v)][3:] for v in alipay[1]], rotation=90)
    plt.yticks(xrange(len(wechat[1])), [vd_wechat[str(v)][3:] for v in wechat[1]])
    plt.yticks()

    plt.xlabel('Versions of Alipay')
    plt.ylabel('Versions of Wechat')

    plt.grid()
    plt.colorbar(im)

    plt.savefig(FIGURE_PATH % 'compare_wechat_alipay', format='pdf')
    plt.show()


def cluster_topic():

    result = []
    for app in load_eapps():
        temp = k_means(map(list, zip(*predict_lda(app))))
        result.append(sorted(temp, key=lambda x: len(x)))

    shade = [0, 0.2, 0.4, 0.6, 0.8]
    data = [[0 for j in xrange(20)] for i in xrange(50)]
    for i in xrange(50):
        for j in xrange(5):
            for k in result[i][j]:
                data[i][k] = 0.8 - shade[j]

    # frequent_patterns(data)

    plt.imshow(map(list, zip(*data)), cmap=plt.cm.jet, interpolation='nearest')

    plt.grid()
    plt.xlabel('App Labels')
    plt.ylabel('Topic Labels')

    plt.savefig(FIGURE_PATH % 'topic_cluster', format='pdf')
    plt.show()


def topic_importance():

    data = []
    apps = load_eapps()

    for app in apps:
        d = predict_lda(app)
        data.append(reduce(lambda a, b: a + b, [np.array(i) for i in d]) / len(d))

    result = []
    for c in k_means(data, 4):
        result.append([apps[i] for i in c])

    print result

    # heat_map(map(list, zip(*data)), 'App Labels', 'Topic Labels', 'topic_importance')


def proper_version(app, low, high):
    version_date = get_version_date(app)
    versions = sorted([int(v) for v in version_date])
    low, high = [maketime(t) for t in low, high]

    prev = -1
    for v in versions:
        if maketime(version_date[str(v)]) > high or v == versions[-1]:
            if prev != -1 and maketime(version_date[str(prev)]) > low:
                return prev
            else:
                return -1
        prev = v

    return -1


def topics_common(low, start, end):

    dictionary = corpora.Dictionary.load(DESC_DICT)
    lda = models.LdaModel.load(LDA_MODEL)
    points = get_points(start, end)

    apps = []
    for app in load_eapps():
        version_date = get_version_date(app)
        versions = sorted([int(v) for v in version_date])

        s = maketime(version_date[str(versions[0])])
        e = maketime(version_date[str(versions[-1])])

        if s <= maketime(start) and e >= maketime(end):
            apps.append(app)

    apps = load_eapps()

    data = []
    for high in points:
        temp = []
        for app in apps:
            v = proper_version(app, low, high)
            if v != -1:
                vector = predict_lda_each(app, v, dictionary, lda)
                if vector:
                    temp.append(np.array(vector))
        low = high
        data.append(reduce(lambda a, b: a + b, temp, np.array([0 for i in xrange(lda.num_topics)])))

    heat_map(map(list, zip(*data)), 'Time Line (2012.1~2016.3)', 'Topic Labels', 'topic_common_%d' % len(apps))


def version_range_each(app):

    y = []
    data = predict_lda(app)

    for i in xrange(1, len(data)):
        y.append(sim_cosine(data[i - 1], data[i]))

    return np.var(y)

    x = xrange(len(data) - 1)
    plt.plot(x, y, 'ro-')
    plt.savefig(FIGURE_PATH % ('version_' + app), format='pdf')
    plt.show()


def version_range():

    temp = []
    for app in load_eapps():
        temp.append((app, downloadCount(app)))

    apps = [x[0] for x in sorted(temp, key=lambda x: x[1])]

    x = xrange(len(apps))
    y = []
    d = []

    for app in apps:
        y.append(version_range_each(app))
        d.append(downloadCount(app))

    plt.plot(x, y, 'ro-')
    plt.savefig(FIGURE_PATH % 'version_range', format='pdf')
    plt.show()


def version_rank():

    apps = load_eapps()
    x = xrange(len(apps))
    yd, yv = [], []

    for app in apps:
        yd.append(downloadCount(app))
        yv.append(len(get_versions(app)))

    yd, yv = parallel_sort(yd, yv)

    # SpearmanrResult(correlation=0.54035899627597683, pvalue=5.108717908700016e-05)
    print spearmanr(yd, yv)

    plt.plot(x, yv, 'ro-')
    # plt.plot(x, yd, 'bs-')
    plt.savefig(FIGURE_PATH % 'version_rank', format='pdf')
    plt.show()


if __name__ == '__main__':

    apps = load_eapps()

    # train_lda(apps, 20)
    # predict_lda(apps[0])

    # train_word2vec(apps, 50)
    # predict_bm25(apps[0])
    # predict_tfidf(apps[0])

    # topics_common('2011-12-1', '2012-1-1', '2016-3-1')
    # cluster_topic()
    # topic_importance()

    # cluster_version()
    # compare_wechat_alipay()
    # version_range_each(apps[0])
    version_range()
