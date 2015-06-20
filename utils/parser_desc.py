# -*- coding: utf-8 -*-

import jieba
import jieba.posseg as pseg
from utils.funcs_rw import *
from utils.consts_global import *


# jieba分词: https://github.com/fxsjy/jieba
# seg_list = jieba.cut("他来到了网易杭研大厦")  # 默认是精确模式
# print(", ".join(seg_list))


# get the IO vectors of app:
# [[x, x, ..., x], [x, x, ..., x]]
def get_vectors(app):
    verbdict = load_verbdict()
    noundict, demension = load_noundict()
    desc = description(app)

    vectors = []
    [vectors.append([0 for i in xrange(demension)]) for j in xrange(2)]

    jieba.load_userdict(MENDDICT_TXT)
    words = pseg.cut(desc)

    verb, inout = None, None
    for w in words:
        if w.flag in ['v', 'vn']:
            inout = verbdict.get(w.word)
        elif w.flag in ['n', 'nr', 'ns', 'nt', 'nz']:
            indexs = noundict.get(w.word)
            if not indexs:
                continue

            # regard as output if lacking verb
            for index in indexs:
                if inout and inout & 1:
                    vectors[0][index - 1] += 1
                if not inout or (inout >> 1) & 1:
                    vectors[1][index - 1] += 1

    return vectors


# update appdict using app names
def update_appdict():
    apps = load_capps()
    f = open(APPDICT_TXT, 'w')
    for app in apps:
        name = app.split(' ')[0]
        if name and name in apps:
            f.write(' '.join([name, '100', 'app']).encode('utf-8') + '\n')
    f.close()


# refs = { u'微信': 3, u'微博': 1, ... }
def get_refs(app):
    jieba.load_userdict(APPDICT_TXT)
    word = pseg.cut(description(app))

    refs = {}
    apps = load_capps()
    for w in word:
        if w.flag == 'app' and w.word != app:
            refs.setdefault(w.word, 0)
            refs[w.word] += 1

    return refs


if __name__ == '__main__':
    pass
