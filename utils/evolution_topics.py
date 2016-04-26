# -*- coding: utf-8 -*-

import jieba
from gensim import corpora, models
from sklearn.cluster import KMeans
from BeautifulSoup import BeautifulSoup

from utils.fp_apriori import frequent_patterns
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

    data, versions, version_data = [], [], {}
    for v in get_versions(app):
        vector = predict_lda_each(app, v, dictionary, lda)
        if vector:
            data.append(vector)
            versions.append(v)
            version_data[v] = vector

    # heat_map(map(list, zip(*data)), 'Version Labels', 'Topic Labels', app)

    return data
    # return version_data
    # return data, versions


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

    count = 0
    shade = [2, 4, 6, 8, 10]
    data = [0 for i in xrange(len(data_versions))]

    for i in sorted(clusters, key=lambda x: len(x)):
        for j in i:
            data[j] = count
        count += 1

    # return data

    heat_map([data], 'Version Labels', 'Cluster Labels', app)


def cluster_version():

    result = [cluster_version_each(app) for app in load_eapps()]
    result.sort(key=lambda x: len(x))

    data = []
    for i in xrange(len(result)):
        temp = [0 for j in xrange(len(result[-1]))]
        for k in xrange(len(result[i])):
            temp[k] += result[i][k]
        data.append(temp)

    heat_map(data, 'Version Labels', 'App Labels', 'cluster_version')


def compare_two_1(app1, app2):

    data = []

    pl1 = predict_lda(app1)
    pl2 = predict_lda(app2)

    vd1 = get_version_date(app1)
    vd2 = get_version_date(app2)

    for u in pl1[0]:
        temp = []
        for v in pl2[0]:
            temp.append(sim_cosine(u, v))
        data.append(temp)

    plt.figure(figsize=(16, 9))

    x = [0, 34]
    y = [30, 54]
    im = plt.imshow(data, cmap=plt.cm.Greys, interpolation='nearest')

    plt.xticks(xrange(len(pl2[1])), [vd2[str(v)][3:] for v in pl2[1]], rotation=90)
    plt.yticks(xrange(len(pl1[1])), [vd1[str(v)][3:] for v in pl1[1]])

    plt.xlabel('Versions of %s' % app2)
    plt.ylabel('Versions of %s' % app1)
    plt.plot(x, y, 'r-', linewidth=2)

    plt.grid()
    plt.colorbar(im)

    plt.savefig(FIGURE_PATH % ('compare_%s_%s' % (app1, app2)), format='pdf')
    plt.show()


def month_vector(app, start, end):

    data = []

    version_data = predict_lda(app)
    points = get_points(start, end)
    version_date = get_version_date(app)

    for i in xrange(1, len(points)):

        low, high = [maketime(points[index]) for index in i - 1, i]
        temp = np.array([0.0 for i in xrange(20)])

        for v, d in version_data.items():
            if low <= maketime(version_date[str(v)]) < high:
                temp += np.array(d)

        data.append(temp)

    return data


def compare_two_2(app1, app2):

    data = []

    mvector1 = month_vector(app1, '2013-1-1', '2016-2-1')
    mvector2 = month_vector(app2, '2013-1-1', '2016-2-1')

    for u in mvector1:
        temp = []
        for v in mvector2:
            temp.append(sim_cosine(u, v))
        data.append(temp)

    im = plt.imshow(data, cmap=plt.cm.Greys, interpolation='nearest')

    plt.xticks(xrange(0, len(mvector2), 12), [str(y) for y in xrange(2013, 2017)])
    plt.yticks(xrange(0, len(mvector1), 12), [str(y) for y in xrange(2013, 2017)])

    plt.xlabel('Versions of Alipay')
    plt.ylabel('Versions of Taobao')
    plt.plot([0, 36], [0, 36], 'r-')

    plt.grid()
    plt.colorbar(im)

    plt.savefig(FIGURE_PATH % ('compare_%s_%s' % (app1, app2)), format='pdf')
    plt.show()


def cluster_topic():

    result = []
    # for app in load_eapps():
    #     temp = k_means(map(list, zip(*predict_lda(app))))
    #     result.append(sorted(temp, key=lambda x: len(x)))

    clusters = []
    for c in result:
        clusters.append(sorted(c, key=lambda x: len(x))[-1])

    frequent_patterns(clusters)


def topic_importance():

    data = []
    apps = load_eapps()

    # for app in apps:
    #     d = predict_lda(app)
    #     data.append(reduce(lambda a, b: a + b,
    #                        [np.array(i) for i in d]) / len(d))

    # print [list(d) for d in data]

    # temp = []
    # for i in xrange(len(data)):
    #     if apps[i] in ['com.UCMobile', 'com.baidu.browser.apps']:
    #         print apps[i], data[i]
    #         temp.append(data[i])

    result = []
    for c in k_means(data, 10):
        result.append([apps[i] for i in c])

    print result

    # heat_map(temp, 'Topic Labels', 'Two Similar Apps', 'topic_importance')
    heat_map(map(list, zip(*data)), 'App Labels', 'Topic Labels', 'topic_importance')


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
        data.append(reduce(lambda a, b: a + b, temp,
                           np.array([0 for i in xrange(lda.num_topics)])))

    heat_map(
        map(list, zip(*data)),
        'Time Line (2012.1~2016.3)',
        'Topic Labels',
        'topic_common_%d' % len(apps)
    )


def version_range_each(app):

    y = []
    data = predict_lda(app)

    for i in xrange(1, len(data)):
        y.append(sim_cosine(data[i - 1], data[i]))

    return y
    # return np.var(y)

    x = xrange(len(data) - 1)
    plt.plot(x, y, 'ro-')
    plt.savefig(FIGURE_PATH % ('version_' + app), format='pdf')
    plt.show()


def version_range():

    result = [version_range_each(app) for app in load_eapps()]
    result.sort(key=lambda x: len(x))

    data = []
    for i in xrange(len(result)):
        temp = [0 for j in xrange(len(result[-1]))]
        for k in xrange(len(result[i])):
            temp[k] += result[i][k]
        data.append(temp)

    heat_map(data, 'Cosine Similarities', 'App Labels', 'version_range')


def version_test():

    data = [version_range_each(app) for app in load_eapps()]
    data.sort(key=lambda x: len(x))

    plt.figure(figsize=(16, 9))
    plt.boxplot(data, showfliers=False)
    plt.ylabel('Cosine Similarity of Topic Vector')
    plt.xlabel('App Labels (Ordered by the Number of Versions)')
    plt.title('Adjacent Version Rangeability of Each App')

    plt.savefig(FIGURE_PATH % 'version_test', format='pdf')
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
    # for app in apps:
    #     predict_lda(app)

    # print_lda()

    # train_word2vec(apps, 50)
    # predict_bm25(apps[0])
    # predict_tfidf(apps[0])

    # topics_common('2011-12-1', '2012-1-1', '2016-3-1')
    # cluster_topic()
    # topic_importance()

    # cluster_version()
    # cluster_version_each(apps[0])

    # compare_two_2('com.tencent.mm', 'com.tencent.mobileqq')
    # compare_two_2('com.UCMobile', 'com.baidu.browser.apps')
    # compare_two_2('com.tencent.mm', 'com.eg.android.AlipayGphone')
    # compare_two_2('com.taobao.taobao', 'com.eg.android.AlipayGphone')

    # version_range_each(apps[0])
    # version_range()
    # version_rank()
    version_test()

    # data = map(list, zip(*data))
    # result = []
    # for i in xrange(len(data)):
    #     result.append(sum(data[i]))
    #
    # heat_map([result], 'Topic Labels', '', 'topic_hot_degree')
