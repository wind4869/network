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

    data = []
    for v in get_versions(app):
        vector = predict_lda_each(app, v, dictionary, lda)
        if vector:
            data.append(vector)

    # heat_map(map(list, zip(*data)), 'Version Labels', 'Topic Labels', app)
    return data


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


def cluster_version(app, num_clusters=5):

    data_versions = predict_lda(app)
    num_versions = len(data_versions)

    if num_versions < num_clusters:
        return

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

    heat_map(data, 'Version Labels', 'Cluster Labels', app)


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


def cluster_topic_fp():

    result = []
    # for app in load_eapps():
    #     temp = cluster_topic(map(list, zip(*predict_lda(app))))
    #     result.append(sorted(temp, key=lambda x: len(x)))

    result = [[[1], [6], [8], [15], [0, 2, 3, 4, 5, 7, 9, 10, 11, 12, 13, 14, 16, 17, 18, 19]], [[6], [10], [18], [0], [1, 2, 3, 4, 5, 7, 8, 9, 11, 12, 13, 14, 15, 16, 17, 19]], [[6], [14], [1], [10], [0, 2, 3, 4, 5, 7, 8, 9, 11, 12, 13, 15, 16, 17, 18, 19]], [[16], [15], [0], [2], [1, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 17, 18, 19]], [[6], [0], [10], [18], [1, 2, 3, 4, 5, 7, 8, 9, 11, 12, 13, 14, 15, 16, 17, 19]], [[6], [14], [1], [12], [0, 2, 3, 4, 5, 7, 8, 9, 10, 11, 13, 15, 16, 17, 18, 19]], [[15], [19], [10], [6], [0, 1, 2, 3, 4, 5, 7, 8, 9, 11, 12, 13, 14, 16, 17, 18]], [[0], [13], [15], [10], [1, 2, 3, 4, 5, 6, 7, 8, 9, 11, 12, 14, 16, 17, 18, 19]], [[12], [1], [10], [9], [0, 2, 3, 4, 5, 6, 7, 8, 11, 13, 14, 15, 16, 17, 18, 19]], [[0], [3], [18], [17], [1, 2, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 19]], [[6], [7], [5], [12], [0, 1, 2, 3, 4, 8, 9, 10, 11, 13, 14, 15, 16, 17, 18, 19]], [[1], [3], [6], [10], [0, 2, 4, 5, 7, 8, 9, 11, 12, 13, 14, 15, 16, 17, 18, 19]], [[1], [14], [12], [19], [0, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 13, 15, 16, 17, 18]], [[12], [19], [6], [5], [0, 1, 2, 3, 4, 7, 8, 9, 10, 11, 13, 14, 15, 16, 17, 18]], [[15], [6], [3], [13], [0, 1, 2, 4, 5, 7, 8, 9, 10, 11, 12, 14, 16, 17, 18, 19]], [[0], [10], [5], [11, 16], [1, 2, 3, 4, 6, 7, 8, 9, 12, 13, 14, 15, 17, 18, 19]], [[13], [15], [0], [19], [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 14, 16, 17, 18]], [[1], [0], [3], [17, 19], [2, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 18]], [[6], [3], [5], [15], [0, 1, 2, 4, 7, 8, 9, 10, 11, 12, 13, 14, 16, 17, 18, 19]], [[12], [5], [10], [0], [1, 2, 3, 4, 6, 7, 8, 9, 11, 13, 14, 15, 16, 17, 18, 19]], [[10], [2], [4], [0], [1, 3, 5, 6, 7, 8, 9, 11, 12, 13, 14, 15, 16, 17, 18, 19]], [[7], [4], [6], [14], [0, 1, 2, 3, 5, 8, 9, 10, 11, 12, 13, 15, 16, 17, 18, 19]], [[0], [9], [10], [19], [1, 2, 3, 4, 5, 6, 7, 8, 11, 12, 13, 14, 15, 16, 17, 18]], [[10], [1], [0], [19], [2, 3, 4, 5, 6, 7, 8, 9, 11, 12, 13, 14, 15, 16, 17, 18]], [[17], [12], [2], [6, 15], [0, 1, 3, 4, 5, 7, 8, 9, 10, 11, 13, 14, 16, 18, 19]], [[8], [9], [3], [19], [0, 1, 2, 4, 5, 6, 7, 10, 11, 12, 13, 14, 15, 16, 17, 18]], [[6], [1], [4], [5, 10, 19], [0, 2, 3, 7, 8, 9, 11, 12, 13, 14, 15, 16, 17, 18]], [[0], [3], [1], [4], [2, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19]], [[3], [0], [11], [10], [1, 2, 4, 5, 6, 7, 8, 9, 12, 13, 14, 15, 16, 17, 18, 19]], [[0], [1], [4], [3], [2, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19]], [[8], [10], [2], [3], [0, 1, 4, 5, 6, 7, 9, 11, 12, 13, 14, 15, 16, 17, 18, 19]], [[5], [1], [11], [12], [0, 2, 3, 4, 6, 7, 8, 9, 10, 13, 14, 15, 16, 17, 18, 19]], [[3], [1], [0], [10], [2, 4, 5, 6, 7, 8, 9, 11, 12, 13, 14, 15, 16, 17, 18, 19]], [[13], [8], [5], [0, 19], [1, 2, 3, 4, 6, 7, 9, 10, 11, 12, 14, 15, 16, 17, 18]], [[6], [19], [3], [10], [0, 1, 2, 4, 5, 7, 8, 9, 11, 12, 13, 14, 15, 16, 17, 18]], [[19], [10], [6], [17], [0, 1, 2, 3, 4, 5, 7, 8, 9, 11, 12, 13, 14, 15, 16, 18]], [[5], [1], [0], [6], [2, 3, 4, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19]], [[3], [0], [1], [8, 10], [2, 4, 5, 6, 7, 9, 11, 12, 13, 14, 15, 16, 17, 18, 19]], [[11], [13], [8], [5, 16], [0, 1, 2, 3, 4, 6, 7, 9, 10, 12, 14, 15, 17, 18, 19]], [[19], [6], [9], [8], [0, 1, 2, 3, 4, 5, 7, 10, 11, 12, 13, 14, 15, 16, 17, 18]], [[4], [0], [7], [16], [1, 2, 3, 5, 6, 8, 9, 10, 11, 12, 13, 14, 15, 17, 18, 19]], [[0], [12], [6], [3], [1, 2, 4, 5, 7, 8, 9, 10, 11, 13, 14, 15, 16, 17, 18, 19]], [[16], [1], [8], [5], [0, 2, 3, 4, 6, 7, 9, 10, 11, 12, 13, 14, 15, 17, 18, 19]], [[16], [8], [13], [5], [0, 1, 2, 3, 4, 6, 7, 9, 10, 11, 12, 14, 15, 17, 18, 19]], [[3], [10], [0], [5], [1, 2, 4, 6, 7, 8, 9, 11, 12, 13, 14, 15, 16, 17, 18, 19]], [[0], [9], [5], [6], [1, 2, 3, 4, 7, 8, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19]], [[0], [15], [6], [3], [1, 2, 4, 5, 7, 8, 9, 10, 11, 12, 13, 14, 16, 17, 18, 19]], [[5], [3], [10], [0, 2], [1, 4, 6, 7, 8, 9, 11, 12, 13, 14, 15, 16, 17, 18, 19]], [[5], [3, 15], [0, 7], [8, 14], [1, 2, 4, 6, 9, 10, 11, 12, 13, 16, 17, 18, 19]], [[6], [5], [3], [10], [0, 1, 2, 4, 7, 8, 9, 11, 12, 13, 14, 15, 16, 17, 18, 19]]]

    shade = [0, 0.2, 0.4, 0.6, 0.8]
    data = [[0 for j in xrange(20)] for i in xrange(50)]
    for i in xrange(50):
        for j in xrange(5):
            for k in result[i][j]:
                data[i][k] = 0.8 - shade[j]

    # plt.figure(figsize=(16, 9))
    plt.imshow(map(list, zip(*data)), cmap=plt.cm.jet, interpolation='nearest')

    plt.grid()
    plt.xlabel('App Labels')
    plt.ylabel('Topic Labels')
    plt.savefig(FIGURE_PATH % 'topic_cluster', format='pdf')
    plt.show()

    # frequent_patterns(data)


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


def topic_importance():

    data = []
    apps = load_eapps()

    # for app in apps:
    #     d = predict_lda(app)
    #     data.append(reduce(lambda a, b: a + b, [np.array(i) for i in d]) / len(d))

    data = [[0.069837709999999997, 0.19389058000000001, 0.0018518499999999999, 0.023886040000000001, 0.0018518499999999999, 0.055302799999999999, 0.073543049999999999, 0.0018518499999999999, 0.11219856, 0.01408644, 0.10289001, 0.0018518499999999999, 0.055368340000000002, 0.066425949999999997, 0.018904319999999999, 0.13330253, 0.0074078399999999997, 0.0018518499999999999, 0.0018518499999999999, 0.03070121], [0.18162105000000001, 0.010691880000000001, 0.02822268, 0.0063227700000000001, 0.01951601, 0.040001960000000003, 0.26318869, 0.029499230000000001, 0.045893740000000002, 0.017251699999999998, 0.068914649999999994, 0.010550199999999999, 0.017824110000000001, 0.017101000000000002, 0.0093468100000000005, 0.027046190000000001, 0.0026515200000000001, 0.072128999999999999, 0.098418050000000007, 0.0092767500000000003], [0.040761329999999998, 0.064784140000000004, 0.0034275799999999999, 0.050840009999999998, 0.034029579999999997, 0.053864389999999998, 0.1375422, 0.01181391, 0.040634129999999997, 0.05882971, 0.18055033000000001, 0.019228149999999999, 0.0016891899999999999, 0.029079089999999998, 0.095234490000000005, 0.049332790000000001, 0.028867360000000002, 0.037482219999999997, 0.034617080000000001, 0.0038113000000000001], [0.0033333299999999998, 0.0033333299999999998, 0.01403565, 0.0033333299999999998, 0.0033333299999999998, 0.0033333299999999998, 0.0033333299999999998, 0.0033333299999999998, 0.0033333299999999998, 0.0033333299999999998, 0.042128310000000002, 0.0033333299999999998, 0.0033333299999999998, 0.0033333299999999998, 0.0033333299999999998, 0.18769870999999999, 0.66523878000000003, 0.0033333299999999998, 0.0033333299999999998, 0.0033333299999999998], [0.21024263000000001, 0.0033333299999999998, 0.0033333299999999998, 0.0033333299999999998, 0.01488577, 0.0033333299999999998, 0.50920299999999996, 0.0033333299999999998, 0.01147835, 0.0033333299999999998, 0.17462696, 0.0033333299999999998, 0.0033333299999999998, 0.0033333299999999998, 0.0033333299999999998, 0.0033333299999999998, 0.0033333299999999998, 0.0033333299999999998, 0.021914179999999998, 0.0033333299999999998], [0.0, 0.14222547999999999, 0.0, 0.0, 0.0, 0.0, 0.58330660999999995, 0.0, 0.0, 0.0, 0.0551064, 0.0, 0.047536639999999998, 0.0, 0.084144440000000001, 0.0, 0.015529599999999999, 0.0, 0.0, 0.0], [0.0072638299999999998, 0.01145152, 0.052836309999999997, 0.043924169999999998, 0.0, 0.089204259999999994, 0.072235079999999993, 0.0, 0.0, 0.0, 0.10759259, 0.0, 0.0, 0.0, 0.0, 0.39631708999999998, 0.01105619, 0.0, 0.0, 0.15970038], [0.40022189000000002, 0.049072619999999997, 0.00133333, 0.00133333, 0.020119979999999999, 0.053344950000000002, 0.027586050000000001, 0.077128050000000004, 0.00133333, 0.034911970000000001, 0.092762349999999993, 0.00133333, 0.00133333, 0.064274510000000007, 0.00133333, 0.096847970000000005, 0.012288810000000001, 0.00133333, 0.01245897, 0.00133333], [0.038534220000000001, 0.073992890000000006, 0.0062290399999999999, 0.082464469999999998, 0.01422007, 0.03688222, 0.067764630000000006, 0.02762937, 0.061354659999999998, 0.048986620000000002, 0.20892933, 0.038756319999999997, 0.077541239999999997, 0.059807060000000002, 0.0041040800000000004, 0.029130960000000001, 0.044079380000000001, 0.0026666699999999999, 0.033922790000000001, 0.017443509999999999], [0.71764704999999995, 0.011764709999999999, 0.011764709999999999, 0.011764709999999999, 0.011764709999999999, 0.011764709999999999, 0.011764709999999999, 0.011764709999999999, 0.011764709999999999, 0.011764709999999999, 0.011764709999999999, 0.011764709999999999, 0.011764709999999999, 0.011764709999999999, 0.011764709999999999, 0.011764709999999999, 0.011764709999999999, 0.034017850000000002, 0.045393919999999997, 0.011764709999999999], [0.01773682, 0.10701884, 0.0, 0.0, 0.0, 0.13221047999999999, 0.28054497, 0.13101884, 0.0, 0.0, 0.00204843, 0.0, 0.094181849999999998, 0.015549139999999999, 0.0, 0.0, 0.033317079999999999, 0.095963779999999999, 0.0, 0.035243839999999999], [0.020040780000000001, 0.10743183000000001, 0.035710810000000003, 0.072024370000000004, 0.027993690000000002, 0.03480217, 0.24518908, 0.059756469999999999, 0.05936545, 0.024404260000000001, 0.084354479999999996, 0.013529329999999999, 0.044280590000000002, 0.023662880000000001, 0.032029170000000003, 0.032855710000000003, 0.0027184800000000001, 0.0068864599999999996, 0.018770869999999999, 0.028953179999999999], [0.083291710000000005, 0.14096786, 0.027275629999999999, 0.041572869999999998, 0.00078728999999999995, 0.028032020000000001, 0.0054773900000000004, 0.042263429999999998, 0.013145560000000001, 0.031786010000000003, 0.025490349999999998, 0.0085961600000000003, 0.23402178000000001, 0.0045159600000000003, 0.073497690000000004, 0.0046962000000000002, 0.052285280000000003, 0.035046099999999997, 0.02977403, 0.092165430000000007], [0.029632439999999999, 0.112234, 0.01261379, 0.02748519, 0.033902769999999999, 0.14371422, 0.089468049999999993, 0.0032548299999999998, 0.021738489999999999, 0.016249619999999999, 0.067459950000000005, 0.0025566400000000002, 0.11038530000000001, 0.0011494299999999999, 0.0011494299999999999, 0.043304559999999999, 0.067580189999999998, 0.014769610000000001, 0.037931239999999998, 0.13004415], [0.056943010000000002, 0.010035809999999999, 0.0, 0.16744094000000001, 0.0, 0.0, 0.28003275999999999, 0.0, 0.041183570000000003, 0.02615512, 0.0024423499999999998, 0.0, 0.079269110000000004, 0.1533301, 0.0, 0.10869696, 0.01173308, 0.0, 0.0, 0.01175986], [0.28697708999999999, 0.00096153999999999999, 0.0076081100000000004, 0.040514120000000001, 0.00096153999999999999, 0.07788921, 0.014119140000000001, 0.0037086599999999999, 0.00096153999999999999, 0.00096153999999999999, 0.075386239999999993, 0.15864998, 0.093305269999999996, 0.01348424, 0.00096153999999999999, 0.01002892, 0.06884142, 0.041916170000000003, 0.00096153999999999999, 0.052647560000000003], [0.42202813, 0.032462089999999999, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.022504219999999998, 0.0, 0.028774379999999999, 0.0, 0.02768808, 0.11621693, 0.0, 0.21007008999999999, 0.0, 0.0, 0.03212955, 0.07015064], [0.12890625, 0.37084391, 0.00390625, 0.10797486000000001, 0.00390625, 0.05078125, 0.019914060000000001, 0.00390625, 0.00390625, 0.00390625, 0.016309170000000001, 0.00390625, 0.00390625, 0.01168365, 0.00390625, 0.00390625, 0.00390625, 0.12334581999999999, 0.00390625, 0.111361], [0.04480874, 0.081286540000000004, 0.011296509999999999, 0.15149568999999999, 0.0010928999999999999, 0.13068097000000001, 0.12753723, 0.035815010000000001, 0.0084353199999999996, 0.01062744, 0.07505908, 0.015539620000000001, 0.021338849999999999, 0.05360583, 0.0010928999999999999, 0.11473571, 0.0087464299999999995, 0.00750462, 0.062094700000000003, 0.0010928999999999999], [0.050942460000000002, 0.074171589999999996, 0.0061507899999999997, 0.0093114300000000007, 0.0061507899999999997, 0.13115529000000001, 0.029100830000000001, 0.0061507899999999997, 0.0061507899999999997, 0.056645090000000002, 0.19662698000000001, 0.048124470000000003, 0.18983058999999999, 0.0061507899999999997, 0.032005619999999999, 0.0061507899999999997, 0.031802990000000003, 0.0061507899999999997, 0.03425943, 0.047890929999999998], [0.12161656, 0.0027380999999999998, 0.21880952000000001, 0.0027380999999999998, 0.13880951999999999, 0.0027380999999999998, 0.0027380999999999998, 0.0027380999999999998, 0.0027380999999999998, 0.0027380999999999998, 0.27416667, 0.0027380999999999998, 0.0027380999999999998, 0.0027380999999999998, 0.011085589999999999, 0.0027380999999999998, 0.0027380999999999998, 0.10170261, 0.026547620000000001, 0.0027380999999999998], [0.0016666700000000001, 0.0016666700000000001, 0.0047768400000000001, 0.068333329999999998, 0.097866670000000003, 0.06080696, 0.097348480000000001, 0.49674028999999997, 0.0016666700000000001, 0.0016666700000000001, 0.0016666700000000001, 0.0016666700000000001, 0.0016666700000000001, 0.0016666700000000001, 0.06992131, 0.0016666700000000001, 0.027526370000000001, 0.0016666700000000001, 0.0016666700000000001, 0.0085260900000000001], [0.19425745, 0.072467320000000002, 0.00114583, 0.0064470200000000004, 0.10878744999999999, 0.015919740000000002, 0.035249229999999999, 0.016913279999999999, 0.00114583, 0.15492453, 0.12623798, 0.0071096800000000002, 0.00144104, 0.017812499999999998, 0.00114583, 0.01346873, 0.00114583, 0.052681150000000003, 0.047900020000000001, 0.10005615], [0.19187757, 0.20459327999999999, 0.053195409999999999, 0.0, 0.0, 0.039709479999999998, 0.056909609999999999, 0.0, 0.056105009999999997, 0.0, 0.13509570000000001, 0.0, 0.030906699999999999, 0.0023916599999999999, 0.0, 0.0, 0.053729689999999997, 0.0, 0.0, 0.13241758000000001], [0.0011904800000000001, 0.01321454, 0.089560009999999995, 0.00762365, 0.0011904800000000001, 0.0089894899999999993, 0.079337759999999993, 0.0011904800000000001, 0.0011904800000000001, 0.0011904800000000001, 0.020878649999999999, 0.0011904800000000001, 0.43532131000000002, 0.048809520000000002, 0.0011904800000000001, 0.037699799999999999, 0.0011904800000000001, 0.14395795, 0.030424469999999999, 0.0011904800000000001], [0.054037479999999999, 0.046684919999999998, 0.0059995600000000001, 0.061424859999999998, 0.039186640000000002, 0.032335599999999999, 0.01032545, 0.0075019300000000004, 0.23021559, 0.089755630000000003, 0.091002929999999996, 0.02522717, 0.0038949499999999999, 0.070738469999999998, 0.0053604999999999998, 0.062741729999999996, 0.017294960000000002, 0.0, 0.0, 0.11710063], [0.02083805, 0.34924606000000002, 0.0, 0.0092357700000000008, 0.074216519999999994, 0.04521725, 0.15302241999999999, 0.0, 0.0027804100000000001, 0.01289822, 0.071759429999999999, 0.021321139999999999, 0.0079542999999999992, 0.0, 0.061261089999999997, 0.015070689999999999, 0.0140679, 0.0, 0.0, 0.10308749], [0.10667662999999999, 0.078741820000000004, 0.00029240000000000001, 0.27984067000000001, 0.13187779999999999, 0.029710429999999999, 0.056964330000000001, 0.00029240000000000001, 0.0092556900000000004, 0.020921820000000001, 0.058410940000000001, 0.0098069799999999999, 0.00029240000000000001, 0.0043984699999999998, 0.00029240000000000001, 0.017693380000000002, 0.10308309, 0.00029240000000000001, 0.028910399999999999, 0.021367210000000001], [0.36161884999999999, 0.00173077, 0.00173077, 0.32924192000000002, 0.00173077, 0.027952959999999999, 0.00173077, 0.021097439999999999, 0.00173077, 0.0156051, 0.030613689999999999, 0.13153107999999999, 0.017550690000000001, 0.00173077, 0.00173077, 0.00173077, 0.00173077, 0.00173077, 0.00173077, 0.00173077], [0.11086612999999999, 0.17974762, 0.02061267, 0.079067760000000001, 0.15544796999999999, 0.015832510000000001, 0.065905649999999996, 0.019544329999999999, 0.04739633, 0.00040650000000000001, 0.016119209999999998, 0.05954769, 0.00040650000000000001, 0.016291300000000002, 0.012067720000000001, 0.047666180000000002, 0.026168650000000002, 0.00040650000000000001, 0.056623510000000002, 0.035073229999999997], [0.021154200000000001, 0.027466730000000002, 0.11289904000000001, 0.13048241999999999, 0.01614579, 0.0, 0.022551760000000001, 0.098240110000000005, 0.32047676000000003, 0.0, 0.16871441000000001, 0.0, 0.0057922700000000004, 0.0023511999999999999, 0.0, 0.0021293000000000002, 0.048939129999999997, 0.0, 0.0, 0.0060097500000000003], [0.062076140000000002, 0.16061891, 0.0, 0.018351650000000001, 0.046595829999999998, 0.071703299999999998, 0.078784740000000006, 0.0, 0.063072310000000006, 0.0, 0.029617919999999999, 0.29187058999999999, 0.11700872, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.01023258], [0.12263383999999999, 0.27581577000000002, 0.0018858499999999999, 0.17289515, 0.041886039999999999, 0.018829410000000001, 0.01083693, 0.01550142, 0.021182719999999999, 0.014367090000000001, 0.14017948, 0.0069845599999999999, 0.00206048, 0.01171524, 0.00070921999999999999, 0.038467550000000003, 0.04510948, 0.01489362, 0.0014061200000000001, 0.02026708], [0.10225289999999999, 0.01695605, 0.0011363600000000001, 0.02520004, 0.0011363600000000001, 0.069318179999999993, 0.077081849999999993, 0.01208995, 0.15342501, 0.0046444399999999997, 0.12722388000000001, 0.0011363600000000001, 0.0011363600000000001, 0.30005602999999997, 0.0011363600000000001, 0.0011363600000000001, 0.0011363600000000001, 0.0011363600000000001, 0.0011363600000000001, 0.074399989999999999], [0.0018070199999999999, 0.04882479, 0.0067256299999999998, 0.065097740000000001, 0.01059039, 0.015253920000000001, 0.38407805, 0.016355189999999999, 0.020760480000000001, 0.01247678, 0.087674219999999997, 0.0038265299999999999, 0.031531150000000001, 0.0, 0.0, 0.051193259999999997, 0.026492419999999999, 0.02515324, 0.0, 0.16259910999999999], [0.0041666699999999999, 0.085988729999999999, 0.0041666699999999999, 0.0041666699999999999, 0.0041666699999999999, 0.0041666699999999999, 0.084201390000000001, 0.0041666699999999999, 0.01231842, 0.049172449999999999, 0.2423913, 0.0041666699999999999, 0.0041666699999999999, 0.0041666699999999999, 0.0041666699999999999, 0.0041666699999999999, 0.0041666699999999999, 0.083730159999999998, 0.0041666699999999999, 0.35212158999999998], [0.072443270000000004, 0.10561524999999999, 0.032255039999999999, 0.035761189999999998, 0.052140110000000003, 0.14975274, 0.087434349999999994, 0.016218840000000002, 0.02533902, 0.00342867, 0.050173929999999999, 0.00239726, 0.065207810000000005, 0.067194630000000005, 0.027745390000000002, 0.046600320000000001, 0.046793380000000002, 0.0059782100000000003, 0.00239726, 0.084109600000000007], [0.13442113999999999, 0.22734460000000001, 0.0019607800000000001, 0.1714936, 0.0019607800000000001, 0.0019607800000000001, 0.063292360000000006, 0.0019607800000000001, 0.13750641999999999, 0.019594319999999998, 0.18535750000000001, 0.0019607800000000001, 0.0019607800000000001, 0.0019607800000000001, 0.0019607800000000001, 0.0019607800000000001, 0.0019607800000000001, 0.0073133800000000004, 0.0019607800000000001, 0.0019607800000000001], [0.018067380000000001, 0.0, 0.061538700000000002, 0.0, 0.056753680000000001, 0.17181604, 0.047205789999999997, 0.02062605, 0.11119817999999999, 0.0, 0.059570860000000003, 0.15718032000000001, 0.0, 0.12506154999999999, 0.0, 0.0, 0.094021549999999995, 0.0064206799999999998, 0.019317259999999999, 0.0], [0.0, 0.0, 0.0090662799999999995, 0.0, 0.0, 0.0, 0.41503510999999998, 0.0, 0.055746370000000003, 0.091525529999999994, 0.076910790000000007, 0.0, 0.0461325, 0.0, 0.0, 0.035865800000000003, 0.00509817, 0.0, 0.0, 0.23432079], [0.23365801, 0.0, 0.0094171399999999992, 0.0, 0.38882515000000001, 0.031721190000000003, 0.01365179, 0.073232080000000005, 0.01209327, 0.0070384699999999998, 0.035104789999999997, 0.0, 0.0, 0.0, 0.0, 0.0073392500000000003, 0.068067030000000001, 0.0055941200000000002, 0.01068206, 0.032427400000000002], [0.14087189999999999, 0.00192308, 0.00192308, 0.13414223, 0.046837820000000002, 0.00192308, 0.19650417000000001, 0.00192308, 0.044987630000000001, 0.026900770000000001, 0.051430910000000003, 0.00192308, 0.15110387, 0.00192308, 0.014300800000000001, 0.023953189999999999, 0.0029829100000000001, 0.01281289, 0.057071009999999998, 0.060798829999999998], [0.0, 0.31548990999999998, 0.01368145, 0.027937199999999999, 0.0, 0.084647379999999994, 0.05005764, 0.0, 0.15162751999999999, 0.0, 0.013244580000000001, 0.0, 0.0, 0.02587453, 0.0, 0.0, 0.12406594999999999, 0.0, 0.059669180000000002, 0.10220772], [0.026262609999999999, 0.0017361099999999999, 0.0017361099999999999, 0.01498529, 0.0017361099999999999, 0.064236109999999999, 0.036784339999999999, 0.0017361099999999999, 0.61165024999999995, 0.0017361099999999999, 0.0063543599999999999, 0.0017361099999999999, 0.012400370000000001, 0.029513890000000001, 0.0017361099999999999, 0.0017361099999999999, 0.061400839999999998, 0.046883569999999999, 0.042232430000000001, 0.0027271399999999999], [0.086341470000000003, 0.012022400000000001, 0.0077110800000000004, 0.090338669999999996, 0.02087514, 0.059096000000000003, 0.024043970000000001, 0.023204019999999999, 0.045712759999999998, 0.050385289999999999, 0.36354313999999999, 0.00039682999999999998, 0.057453160000000003, 0.066479819999999995, 0.0070246600000000003, 0.0056586400000000004, 0.00161915, 0.0085270399999999996, 0.010752309999999999, 0.0049687100000000003], [0.21015856999999999, 0.044471169999999997, 0.00833974, 0.00352564, 0.04371046, 0.1485003, 0.07453572, 0.00352564, 0.00352564, 0.17598443, 0.052773010000000002, 0.00352564, 0.0047502100000000004, 0.00352564, 0.050882509999999999, 0.00352564, 0.00352564, 0.12763801999999999, 0.014766430000000001, 0.00352564], [0.13436534, 0.01043673, 0.010658839999999999, 0.14770997, 0.068239670000000002, 0.032775989999999998, 0.14842279, 0.0067492200000000002, 0.0046618099999999997, 0.0061877900000000003, 0.030723070000000002, 0.019444860000000001, 0.022102449999999999, 0.036928240000000001, 0.01230608, 0.120433, 0.03702366, 0.050529329999999997, 0.024443679999999999, 0.026027990000000001], [0.04835238, 0.040948890000000002, 0.065288570000000004, 0.05709674, 0.00058823999999999997, 0.32090734999999998, 0.02478437, 0.00058823999999999997, 0.00058823999999999997, 0.019002519999999998, 0.10417683, 0.00058823999999999997, 0.00058823999999999997, 0.072016339999999998, 0.00058823999999999997, 0.11750484999999999, 0.00058823999999999997, 0.047381180000000002, 0.00058823999999999997, 0.00058823999999999997], [0.092335410000000007, 0.0, 0.0, 0.14583741, 0.0, 0.19311281999999999, 0.0, 0.24214672000000001, 0.063557639999999999, 0.00612256, 0.0, 0.0, 0.0, 0.0, 0.11583095, 0.11916945, 0.0, 0.0, 0.0, 0.0], [0.067304840000000005, 0.028545419999999998, 0.070572629999999997, 0.066884609999999997, 0.0033933700000000002, 0.20785696000000001, 0.087849930000000007, 0.01899878, 0.012079889999999999, 0.033676369999999997, 0.10183824, 0.017972680000000001, 0.015668720000000001, 0.093766429999999998, 0.022670360000000001, 0.06783554, 0.011837520000000001, 0.0076066500000000004, 0.0089758700000000004, 0.0048334800000000002]]

    result = []
    for c in k_means(data, 4):
        result.append([apps[i] for i in c])
    print result

    # heat_map(map(list, zip(*data)), 'App Labels', 'Topic Labels', 'topic_importance')


if __name__ == '__main__':

    apps = load_eapps()

    # train_lda(apps, 20)
    # predict_lda(apps[0])

    # train_word2vec(apps, 50)
    # predict_bm25(apps[0])
    # predict_tfidf(apps[0])

    # topics_common('2011-12-1', '2012-1-1', '2016-3-1')
    # cluster_topic_fp()

    topic_importance()

