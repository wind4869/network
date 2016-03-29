# -*- coding: utf-8 -*-

import jieba
from gensim import corpora, models
from sklearn.cluster import KMeans
from collections import defaultdict
from BeautifulSoup import BeautifulSoup

from utils.parser_apk import *
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
            train_set.append(preproccess(''.join(raw_desc(app, v))))

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


def predict_lda(app):

    dictionary = corpora.Dictionary.load(DESC_DICT)
    lda = models.LdaModel.load(LDA_MODEL)
    num = lda.num_topics

    data = []
    for v in get_versions(app):
        raw = raw_desc(app, v)[1]  # only use update desc
        if not raw:
            continue

        temp = [0 for i in xrange(num)]
        word_list = preproccess(raw)
        doc_bow = dictionary.doc2bow(word_list)

        for t in lda[doc_bow]:
            index, probability = t
            temp[index] = probability
        data.append(temp)

    heat_map(map(list, zip(*data)), 'Version Labels', 'Topic Labels', 'topics_%d' % num)


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
    print_topics()


def print_topics():
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

    heat_map(map(list, zip(*data)), 'Version Labels', 'Topic Labels', 'topics_%d' % num)


def predict_bm25(app):
    docs = [preproccess(''.join(raw_desc(app, v))) for v in get_versions(app)]
    bm25 = BM25(docs)

    topics = pickle_load(WORD2VEC)
    num = len(topics)

    data = []
    for t in topics:
        scores = bm25.bm25_score(t)
        data.append([x if x > 0 else 0 for x in scores])

    heat_map(data, 'Version Labels', 'Topic Labels', 'topics_%d' % num)
    return data


def sim_neighbors():

    data_topics = [predict_bm25(app) for app in apps]
    data_versions = map(list, zip(*data_topics))

    y = []
    for i in xrange(1, len(data_versions)):
        y.append(sim_cosine(data_versions[i - 1], data_versions[i]))

    x = xrange(len(data_versions) - 1)

    plt.plot(x, y, 'ro-')
    plt.show()


def cluster_test():
    data_topics = [predict_bm25(app) for app in apps]
    data_versions = map(list, zip(*data_topics))

    count = 0
    result_tuples = []

    kmeans_clustering = KMeans(10)
    for i in kmeans_clustering.fit_predict(data_versions):
        result_tuples.append((count, i))
        count += 1

    clusters = [[] for i in xrange(10)]
    for word, index in result_tuples:
        clusters[index].append(word)

    print clusters


if __name__ == '__main__':
    apps = load_eapps()

    # train_lda(apps, 50)
    # predict_lda(apps[0])

    # train_word2vec(apps, 50)
    # predict_bm25(apps[0])
    predict_tfidf(apps[2])
