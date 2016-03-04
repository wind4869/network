# -*- coding: utf-8 -*-

import math
from gensim import corpora


class BM25:
    def __init__(self, docs):
        self.dictionary = corpora.Dictionary()
        self.df = {}
        self.doc_tf = []
        self.doc_idf = {}
        self.n = 0
        self.doc_avg_len = 0
        self.docs = docs
        self.doc_len = []
        self.build_dictionary()
        self.tfidef_generator()

    def build_dictionary(self):
        self.dictionary.add_documents(self.docs)

    def tfidef_generator(self, base=math.e):
        doc_total_len = 0
        for doc in self.docs:
            doc_total_len += len(doc)
            self.doc_len.append(len(doc))
            bow = dict([(term, freq * 1.0 / len(doc)) for term, freq in self.dictionary.doc2bow(doc)])
            for term, tf in bow.items():
                if term not in self.df:
                    self.df[term] = 0
                self.df[term] += 1
            self.doc_tf.append(bow)
            self.n += 1
        for term in self.df:
            self.doc_idf[term] = math.log((self.n - self.df[term] + 0.5) / (self.df[term] + 0.5), base)
        self.doc_avg_len = doc_total_len / self.n

    def bm25_score(self, query, k1=1.5, b=0.75):
        query_bow = self.dictionary.doc2bow(query)
        scores = []
        for idx, doc in enumerate(self.doc_tf):
            common_terms = set(dict(query_bow).keys()) & set(doc.keys())
            tmp_score = []
            doc_terms_len = self.doc_len[idx]
            for term in common_terms:
                upper = (doc[term] * (k1 + 1))
                below = ((doc[term]) + k1 * (1 - b + b * doc_terms_len / self.doc_avg_len))
                tmp_score.append(self.doc_idf[term] * upper / below)
            scores.append(sum(tmp_score))
        return scores

    def tfidef(self):
        result = []
        for doc in self.doc_tf:
            doc_tfidf = [(term, tf * self.doc_idf[term]) for term, tf in doc.items()]
            doc_tfidf.sort()
            result.append(doc_tfidf)
        return result

    def items(self):
        # Return a list [(term_idx, term_desc),]
        items = self.dictionary.items()
        items.sort()
        return items


if __name__ == '__main__':
    pass
