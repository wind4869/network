# -*- coding: utf-8 -*-

import jieba
import matplotlib.pyplot as plt
from gensim import corpora, models
from collections import defaultdict
from BeautifulSoup import BeautifulSoup

from utils.parser_apk import *


# get number, apk and html of each version for app
def download_dataset(app):

    versions = set([])
    soup = BeautifulSoup(urllib2.urlopen(VERSION_URL % app).read())
    for span in soup.findAll(attrs={'class': 'version-code'}):
        versions.add(int(re.findall(r'\d+', span.text)[0]))

    latest = sorted(versions)[-1]
    print 'Latest version: ' + str(latest)

    run('mkdir %s%s' % (APK_DIR, app))
    run('mkdir %s%s' % (HTML_DIR, app))

    versions = []
    for v in xrange(latest + 1):

        if url_exists(HTML_URL % (app, v)):

            print '> %d ...' % v
            versions.append(v)

            parameters = (app, v, app, v)
            [run(cmd) for cmd in [raw_cmd % parameters for raw_cmd in [HTML_CMD, APK_CMD]]]

    print versions
    return versions


def parser_dataset(app, versions):

    run('mkdir %s%s/' % (APP_DIR, app))

    for v in versions:

        print '> %d ...' % v
        run('mkdir %s%s/%s' % (APP_DIR, app, v))

        parameters = (app, v, app, v)
        [run(cmd) for cmd in [raw_cmd % parameters for raw_cmd in [D2J_CMD, XML_CMD]]]


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


def preproccess(app, v):

    # step 1. get raw description from html
    raw = ""
    soup = BeautifulSoup(open(HTML_PATH % (app, v)))
    for pre in soup.findAll('pre'):
        raw += pre.text

    # step 2. word segmentation
    word_list = list(jieba.cut(raw, cut_all=False))

    # step 3. remove common stop words
    stoplist = load_content(STOPLIST_TXT)
    word_list = [word for word in word_list if word not in stoplist and len(word) > 1]

    # step 4. remove words that appear only once
    frequency = defaultdict(int)
    for word in word_list:
        frequency[word] += 1
    word_list = [word for word in word_list if frequency[word] > 1]

    return word_list


def train(num_topics):

    train_set = []
    for app in APPS:
        train_set.extend([preproccess(app, v) for v in VERSIONS[app]])

    dictionary = corpora.Dictionary(train_set)
    dictionary.save(DESC_DICT)  # store the dictionary, for future reference

    corpus = [dictionary.doc2bow(text) for text in train_set]
    # corpora.MmCorpus.serialize(CORPUS_MM, corpus)

    tfidf = models.TfidfModel(corpus)
    corpus_tfidf = tfidf[corpus]
    # tfidf.save(TFIDF_MODEL)

    lda = models.LdaModel(corpus_tfidf, id2word=dictionary, num_topics=num_topics)
    lda.save(LDA_MODEL)  # store to disk, for later use

    for i in xrange(num_topics):
        print lda.print_topic(i)


def predict(app, v, dictionary, lda):
    word_list = preproccess(app, v)
    doc_bow = dictionary.doc2bow(word_list)
    return lda[doc_bow]


def topics_test(app):

    dictionary = corpora.Dictionary.load(DESC_DICT)
    lda = models.LdaModel.load(LDA_MODEL)
    num = lda.num_topics

    data = []
    for v in VERSIONS[app]:
        temp = [0 for i in xrange(num)]
        for t in predict(app, v, dictionary, lda):
            index, probability = t
            temp[index] = probability
        data.append(temp)

    heat_map(data, 'Topic Labels', 'Version Labels', 'topics_%d' % num)


def unique(c):
    return reduce(lambda a, b: a if b in a else a + [b], [[], ] + c)


def get_components_each(app, v):
    intents = get_intents(app, v)
    filters = get_filters(app, v)[0]
    return [
        ['.'.join(i.split('.')[:3]) for i in intents[0]],
        intents[1],
        filters
    ]


def get_components_all(app):

    eintents, iintents, filters = [], [], []

    for v in VERSIONS[app]:
        components = get_components_each(app, v)

        eintents.extend(components[0])
        iintents.extend(components[1])
        filters.extend(components[2])

    return [unique(c) for c in [eintents, iintents, filters]]


def components_test(app, index):
    data = []
    components_all = get_components_all(app)[index]

    for v in VERSIONS[app]:
        components = get_components_each(app, v)[index]
        if not components:
            continue

        data.append([1 if i in components else 0 for i in components_all])

    # heat_map(data, 'Explict-intent Labels', 'Version Labels', 'explict_intents')
    # heat_map(data, 'Implicit-intent Labels', 'Version Labels', 'implicit_intents')
    heat_map(data, 'Intent-filter Labels', 'Version Labels', 'intent_filters')


if __name__ == '__main__':
    app = 'com.taobao.taobao'
    # parser_dataset(app, download_dataset(app))

    # app = APPS[0]

    # train(30)
    # topics_test(app)
    # components_test(app, 1)

    for v in VERSIONS[app]:
        print v
