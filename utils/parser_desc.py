# -*- coding: utf-8 -*-

import jieba
import jieba.posseg as pseg

from utils.functions import *
from utils.consts_global import *


# jieba分词: https://github.com/fxsjy/jieba
# seg_list = jieba.cut("他来到了网易杭研大厦")  # 默认是精确模式
# print(", ".join(seg_list))


# get inputs and outputs of app: [x, x, ..., x], [x, x, ..., x]
def get_inputs_outputs(app):
    verbdict = load_verbdict()
    noundict, demension = load_noundict()
    desc = description(app)

    inputs = [0 for i in xrange(demension)]
    outputs = [0 for i in xrange(demension)]

    if not desc:
        return inputs, outputs

    jieba.load_userdict(MENDDICT_TXT)
    words = pseg.cut(desc)

    inout = 0
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
                    inputs[index - 1] += 1
                if not inout or (inout >> 1) & 1:
                    outputs[index - 1] += 1

    return inputs, outputs


# update appdict using app titles
def update_appdict():
    titles = [title(app) for app in load_capps()]
    f = open(APPDICT_TXT, 'w')
    for t in titles:
        if t.split(' ')[0] == t:
            f.write(' '.join([t, '100', 'app']).encode('utf-8') + '\n')
    f.close()


# refs = { u'com.tencent.mm': 3, u'com.sina.weibo': 1, ... }
def get_refs(app_from):
    refs = {}
    desc = description(app_from)
    if not desc:
        return refs

    jieba.load_userdict(APPDICT_TXT)
    word = pseg.cut(desc)

    for w in word:
        if w.flag == 'app':
            app_to = packageName(w.word)
            if app_to != app_from:
                refs.setdefault(app_to, 0)
                refs[app_to] += 1

    return refs.keys()


if __name__ == '__main__':
    pass
