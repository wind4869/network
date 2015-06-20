# -*- coding: utf-8 -*-

import codecs
import networkx as nx
import cPickle as pickle
from utils.db_connect import *
from utils.consts_global import *
from igraph import *


# get db object
appDetails = getAppDetails()

# open file use utf-8 encoding
open_in_utf8 = lambda filename: \
    codecs.open(filename, encoding='utf-8')

# run a shell command
run = lambda cmd: os.popen(cmd.encode('utf-8'))


# verbdict = {u'发': 1, u'分享': 2, u'收发': 3, ... }
def load_verbdict():
    verbdict = {}
    f = open_in_utf8(VERBDICT_TXT)
    for line in f.readlines():
        temp = line.strip().split(':')
        flag = temp[0][0]
        verbs = temp[1].split('|')
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
        temp = line.strip().split(':')
        flag = temp[0][0]
        nouns = temp[1].split('|')
        for noun in nouns:
            noundict.setdefault(noun, [])
            noundict[noun].append(int(flag))
    f.close()
    return noundict, dimension


# permdict = {permission: [native1, native2, ...], ... }
def load_permdict():
    permdict = {}
    f = open_in_utf8(PERMDICT_TXT)
    for line in f.readlines():
        permission, natives = line.strip().split('->')
        permdict[permission] = natives.split(',') if natives else []
    f.close()
    return permdict


# load map for mapping native's '.apk' name to chinese name
def load_natdict():
    natdict = {}
    f = open_in_utf8(NATDICT_TXT)
    for line in f.readlines():
        key, value = line.strip().split('->')
        natdict[key] = value
    f.close()
    return natdict


# load map for mapping pan' app name to gan' app name
def load_appmap():
    appmap = {}
    f = open_in_utf8(APPMAP_TXT)
    for line in f.readlines():
        key, value = line.strip().split('->')
        appmap[key] = value
    f.close()
    return appmap


# load raw intents from file
def load_rintents(path):
    f = open(path)
    lines = f.readlines()
    f.close()
    return eval(lines[0]) if lines else None


# assist for simply load content from file
def load_content(path):
    f = open_in_utf8(path)
    content = [line[:-1] for line in f.readlines()]
    f.close()
    return content


# load native apps from natdict
def load_napps():
    return [n.strip().split('->')[1] for n in load_content(NATDICT_TXT)]


# load common apps form applist
def load_capps():
    return load_content(APPLIST_TXT)


# load all applications
def load_apps():
    return load_capps() + load_napps()


# load all categories
def load_categories():
    return load_content(CATELIST_TXT)


def description(app):
    return appDetails.find_one({'title': app})['description']


def categories(app):
    return appDetails.find_one({'title': app})['categories']


def tags(app):
    return appDetails.find_one({'title': app})['tags']


def likesCount(app):
    return appDetails.find_one({'title': app})['likesCount']


def downloadCount(app):
    return appDetails.find_one({'title': app})['downloadCount']


def permissions(app):  # gotten from wandoujia website
    return appDetails.find_one({'title': app})['permissions']


def perms(app):  # extracted form xml file
    return appDetails.find_one({'title': app})['perms']


def packageName(app):
    return appDetails.find_one({'title': app})['packageName']


def explicits(app):
    return appDetails.find_one({'title': app})['explicits']


def implicits(app):
    return appDetails.find_one({'title': app})['implicits']


def filters(app):
    return appDetails.find_one({'title': app})['filters']


def vectors(app):
    return appDetails.find_one({'title': app})['vectors']


def refs(app):
    return appDetails.find_one({'title': app})['refs']


def nats(app):
    return appDetails.find_one({'title': app})['nats']


# dump network to dot file
def dump_network(network, path):
    nx.write_dot(network, GAN_DOT)


# load network from dot file
def load_network(path):
    return nx.read_dot(path)


def pickle_dump(obj, path):
    pickle.dump(obj, open(path, 'w'))


def pickle_load(path):
    return pickle.load(open(path))


def dump_clusters(uid, result):
    pickle_dump(result, CLUSTERS_TXT % uid)


def load_clusters(uid):
    return pickle_load(CLUSTERS_TXT % uid)


# get Global App Network(GAN) by test mask, number of app, test date
def load_gan(test=0, number=NUMBER_OF_APP, date='0118'):
    return load_network(GAN_TXT % (test, number, date))


# get Personal App Network(PAN) by uid
def load_pan(uid):
    return load_network(PAN_TXT % uid)


# get usages edges by uid
def load_usage_edges(uid):
    return load_network(USAGE_TXT % uid)


if __name__ == '__main__':
    pass