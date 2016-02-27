# -*- coding: utf-8 -*-

import jieba
from gensim import corpora, models
from collections import defaultdict
from BeautifulSoup import BeautifulSoup

from utils.funcs_rw import *


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


def train_model(train_set, num_topics):

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


def test(app, v, dictionary, lda):
    word_list = preproccess(app, v)
    doc_bow = dictionary.doc2bow(word_list)
    return lda[doc_bow]


if __name__ == '__main__':

    train_set = []
    for app in apps[:1]:

        # train_set.extend([preproccess(app, v) for v in versions[app]])
        # train_model(train_set, 10)

        dictionary = corpora.Dictionary.load(DESC_DICT)
        lda = models.LdaModel.load(LDA_MODEL)

        for v in versions[app]:
            print test(app, v, dictionary, lda)
