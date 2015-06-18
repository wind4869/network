# -*- coding: utf-8 -*-

import jieba
import jieba.posseg as pseg
from utils.funcs_rw import *
from utils.consts_global import *


# jieba分词工具的基本用法:
# seg_list = jieba.cut("他来到了网易杭研大厦")  # 默认是精确模式
# print(", ".join(seg_list))


# verbdict = {u'发': 1, u'分享': 2, u'收发': 3, ... }
def load_verbdict():
    verbdict = {}
    f = open_in_utf8(VERBDICT_TXT)
    for line in f.readlines():
        temp = line.split(':')
        flag = temp[0][0]
        verbs = temp[1].strip().split('|')
        [verbdict.setdefault(verb, int(flag)) for verb in verbs]
    f.close()
    return verbdict


# noundict = {u'语音': [1], u'单词': [4], ... }
# use list in case of a noun belonging to multiple categories
def load_noundict():
    dimension = 0
    noundict = {}
    f = open_in_utf8(NOUNDICT_TXT)
    for line in f.readlines():
        dimension += 1
        temp = line.split(':')
        flag = temp[0][0]
        nouns = temp[1].strip().split('|')
        for noun in nouns:
            noundict.setdefault(noun, [])
            noundict[noun].append(int(flag))
    f.close()
    return noundict, dimension


# get the IO vector of app:
# [[x, x, ..., x], [x, x, ..., x]]
def get_vector(app):
    verbdict = load_verbdict()
    noundict, demension = load_noundict()
    s = description(app)

    vector = []
    [vector.append([0 for i in xrange(demension)]) for j in xrange(2)]

    jieba.enable_parallel(10)
    jieba.load_userdict(USERDICT_TXT)
    words = pseg.cut(s)

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
                    vector[0][index - 1] += 1
                if not inout or (inout >> 1) & 1:
                    vector[1][index - 1] += 1

    return vector


if __name__ == '__main__':
    pass
    # print get_vector(load_apps()[0])
