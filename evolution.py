# -*- coding: utf-8 -*-

import re
import jieba
import matplotlib.pyplot as plt
from gensim import corpora, models
from sklearn.cluster import KMeans
from collections import defaultdict
from BeautifulSoup import BeautifulSoup

from utils.parser_apk import *
from utils.bm25 import BM25


# get number, apk and html of each version for app
def download_dataset(app):

    # get version numbers from wandoujia (limited)
    versions = set([])
    soup = BeautifulSoup(urllib2.urlopen(VERSION_URL % app).read())
    for span in soup.findAll(attrs={'class': 'version-code'}):
        versions.add(int(re.findall(r'\d+', span.text)[0]))

    versions = sorted(versions)
    max_version = versions[-1]
    print '>>', len(versions), versions

    # create apk and html directory of app
    run('mkdir %s%s' % (APK_DIR, app))
    run('mkdir %s%s' % (HTML_DIR, app))

    # crawl as much versions as possible in the limited time
    version_range = xrange(max_version) if max_version < 1000 else versions

    version_date = {}
    for v in version_range:
        url = HTML_URL % (app, v)
        if url_exists(url):

            # get datetime of this version
            soup = BeautifulSoup(urllib2.urlopen(url).read())
            date = \
                soup.findAll(attrs={'class': 'line_content'})[-1].findAll('span')[-1].text.strip()
            version_date[v] = date

            print '>> %d (%s) crawling ...' % (v, date)

            # download apk and html of this version from http://apk.hiapk.com
            parameters = (app, v, app, v)
            [run(cmd) for cmd in [raw_cmd % parameters for raw_cmd in [HTML_CMD, APK_CMD]]]

        else:
            print '>> %d missed' % v

    # store dict (version: date) numbers to file
    pickle_dump(version_date, VERSION_PATH % app)
    return sorted(version_date.keys())


def analyse_dataset(app, versions):

    run('mkdir %s%s/' % (APP_DIR, app))

    for v in versions:

        print '>> %d analysing ...' % v
        run('mkdir %s%s/%s' % (APP_DIR, app, v))

        parameters = (app, v, app, v)
        [run(cmd) for cmd in [raw_cmd % parameters for raw_cmd in [D2J_CMD, XML_CMD]]]

    # remove all apk files
    print '>> remove all apk files'
    run('rm -r %s' % (APK_DIR + app))


def extract_dataset(app, versions):

    print '>> start extracting ... '

    # prepare for intent extracting
    f = open('/Users/wind/repos/IntentAnalysis/versions.txt', 'w')
    f.write(app + '\n')
    [f.write(str(v) + '\n') for v in versions]
    f.close()

    # do intents extracting
    run(INTENT_ANALYSIS)

    # remove all jar files
    print '>> remove all jar files'
    run('rm %s/*/classes.jar' % (APP_DIR + app))

    print '>> extraction finished '


def raw_desc(app, v):
    raws = []
    soup = BeautifulSoup(open(HTML_PATH % (app, v)))

    for pre in soup.findAll('pre'):
        raws.append(pre.text)

    if len(raws) < 2:
        raws.append('')

    return raws


def heat_map(data, xlabel, ylabel, fname):
    fig, ax = plt.subplots()
    im = ax.imshow(data, cmap=plt.cm.Greys, interpolation='nearest')

    # Move left and bottom spines outward by 10 points
    ax.spines['left'].set_position(('outward', 10))
    ax.spines['bottom'].set_position(('outward', 10))
    # Hide the right and top spines
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)
    # Only show ticks on the left and bottom spines
    ax.yaxis.set_ticks_position('left')
    ax.xaxis.set_ticks_position('bottom')

    plt.xlabel(xlabel)
    plt.ylabel(ylabel)

    plt.grid()
    # plt.colorbar(im)

    plt.savefig(FIGURE_PATH % fname, format='pdf')
    plt.show()


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

    return data

    # heat_map(data, 'Version Labels', 'Topic Labels', 'topics_%d' % num)


def unique(c):
    return reduce(lambda a, b: a if b in a else a + [b], [[], ] + c)


def get_components_each(app, v):
    components = list(get_intents(app, v))
    components.append(get_filters(app, v)[0])
    return components


def get_components_all(app):

    eintents, iintents, filters = [], [], []

    for v in get_versions(app):
        components = get_components_each(app, v)

        eintents.extend(components[COMPONENT.E_INTENT])
        iintents.extend(components[COMPONENT.I_INTENT])
        filters.extend(components[COMPONENT.I_FILTER])

    return [unique(c) for c in [eintents, iintents, filters]]


def components_test(app, index):

    data = []
    components_all = get_components_all(app)[index]
    for i in xrange(len(components_all)):
        print i, components_all[i]

    for v in get_versions(app):
        components = get_components_each(app, v)[index]
        if not components:
            continue

        data.append([1 if i in components else 0 for i in components_all])

    if index == 0:
        heat_map(map(list, zip(*data)), 'Version Labels', 'Explict-intent Labels', 'explict_intents')
    elif index == 1:
        heat_map(map(list, zip(*data)), 'Version Labels', 'Implicit-intent Labels', 'implicit_intents')
    elif index == 2:
        heat_map(map(list, zip(*data)), 'Version Labels', 'Intent-filter Labels', 'intent_filters')


if __name__ == '__main__':
    count = 5
    apps = load_content(APPSC2_TXT)

    for app in apps[count:]:

        print '> %d. %s' % (count, app)
        count += 1

        versions = download_dataset(app)
        analyse_dataset(app, versions)
        extract_dataset(app, versions)

    # app = apps[count]
    # versions = sorted(pickle_load(VERSION_PATH % app).keys())
    # analyse_dataset(app, versions)
    # extract_dataset(app, versions)

    # index = 2
    # app = APPS[0]
    # components_all = get_components_all(app)[index]
    #
    # components_test(app, index)

    # train_lda(APPS, 30)
    # predict_lda(app)

    # train_word2vec(APPS, 50)
    # predict_tfidf(app)

    # for app in APPS:
    #     data_topics = predict_bm25(app)
    #     data_versions = map(list, zip(*data_topics))
    #
    #     y = []
    #     for i in xrange(1, len(data_versions)):
    #         y.append(sim_cosine(data_versions[i - 1], data_versions[i]))
    #
    #     x = xrange(len(data_versions) - 1)
    #
    #     plt.plot(x, y, 'ro-')
    #     plt.show()

        # kmeans_clustering = KMeans(10)
        #
        # count = 0
        # result_tuples = []
        # for i in kmeans_clustering.fit_predict(data_versions):
        #     result_tuples.append((count, i))
        #     count += 1
        #
        # clusters = [[] for i in xrange(10)]
        # for word, index in result_tuples:
        #     clusters[index].append(word)

        # print clusters

