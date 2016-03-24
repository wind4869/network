# -*- coding: utf-8 -*-

import os
import re
import math
import numpy
import codecs
import urllib2
import cPickle as pickle

import networkx as nx

from utils.db_connect import *
from utils.consts_global import *


# get db object
appDetails = getAppDetails()
usageRecords = getUsageRecords()

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


# load map for packageName to chinese name
def load_natdict():
    natdict = {}
    f = open_in_utf8(NATDICT_TXT)
    for line in f.readlines():
        key, value = line.strip().split('->')
        natdict[key] = value
    f.close()
    return natdict


def load_appmap():
    appmap = {}
    f = open_in_utf8(FILE_DIR + 'appmap.txt')
    for line in f.readlines():
        key, value = line.strip().split('->')
        appmap[key] = value
    f.close()
    return appmap


# load raw intents from file
def load_rintents(app, v):
    path = INTENT_PATH % (app, v)
    if not os.path.exists(path):
        print '[load_rintents][File not exists]: %s' % path
        return None

    f = open(path)
    lines = f.readlines()
    f.close()
    return eval(lines[0]) if lines else None


# load content from file line by line
def load_content(path):
    f = open_in_utf8(path)
    content = [line.strip() for line in f.readlines()]
    f.close()
    return content


# load native apps from natdict
def load_napps():
    return load_natdict().keys()


# load common apps form applist
def load_capps():
    return load_content(APPLIST_TXT)


# load all applications
def load_apps():
    return load_capps() + load_napps()


# load all uids
def load_uids():
    return [re.findall(r'[a-z]\d+', name)[0]
            for name in os.listdir(LOG_DIR) if name != '.DS_Store']


def packageName(title):
    return appDetails.find_one({'title': title})['packageName']


def title(app):
    natdict = load_natdict()
    record = appDetails.find_one({'packageName': app})
    return record['title'] if record else natdict[app] if app in natdict else app


def description(app):
    return appDetails.find_one({'packageName': app})['description']


def likesRate(app):
    return appDetails.find_one({'packageName': app})['likesRate']


def likesCount(app):
    return appDetails.find_one({'packageName': app})['likesCount']


def dislikesCount(app):
    return appDetails.find_one({'packageName': app})['dislikesCount']


def downloadCount(app):
    return appDetails.find_one({'packageName': app})['downloadCount']


def installedCount(app):
    return appDetails.find_one({'packageName': app})['installedCount']


def commentsCount(app):
    return appDetails.find_one({'packageName': app})['commentsCount']


def categories(app):
    return appDetails.find_one({'packageName': app})['categories']


def tags(app):
    return appDetails.find_one({'packageName': app})['tags']


def updatedDate(app):
    return appDetails.find_one({'packageName': app})['updatedDate']


def version(app):
    return appDetails.find_one({'packageName': app})['version']


def developer(app):
    return appDetails.find_one({'packageName': app})['developer']


def sims(app):
    return appDetails.find_one({'packageName': app})['sims']


def explicits(app):
    return appDetails.find_one({'packageName': app})['explicits']


def implicits(app):
    return appDetails.find_one({'packageName': app})['implicits']


def filters(app):
    return appDetails.find_one({'packageName': app})['filters']


def permissions(app):
    return appDetails.find_one({'packageName': app})['permissions']


def inputs(app):
    return appDetails.find_one({'packageName': app})['inputs']


def outputs(app):
    return appDetails.find_one({'packageName': app})['outputs']


def refs(app):
    return appDetails.find_one({'packageName': app})['refs']


# add new edge if not exists and get weights
def get_weights(gan, app_from, app_to):
    if not gan.has_edge(app_from, app_to):
        gan.add_edge(app_from, app_to,
                     weights=[0 for i in xrange(NUM_EDGETYPE)])

    return gan[app_from][app_to]['weights']


def pickle_dump(obj, path):
    pickle.dump(obj, open(path, 'w'))


def pickle_load(path):
    return pickle.load(open(path))


# dump and load gan
def dump_gan(gan):
    nx.write_dot(gan, GAN_DOT)
    pickle_dump(gan, GAN_PICKLE)


def load_gan():
    return pickle_load(GAN_PICKLE)


# dump and load pan
def dump_pan(uid, pan):
    nx.write_dot(pan, PAN_DOT % uid)
    pickle_dump(pan, PAN_PICKLE % uid)


def load_pan(uid):
    return pickle_load(PAN_PICKLE % uid)


# get neighbors of app in lan
def neighbors(lan, app):
    return set(lan.successors(app) + lan.predecessors(app))


# compute similarity of two pans
def g_sim(pan1, pan2):
    medges = pan1.number_of_edges() + pan2.number_of_edges()
    mcs = 0

    for app_from, app_to in pan1.edges():
        if pan2.has_edge(app_from, app_to):
            mcs += 1
            # mcs += pan1[app_from][app_to]['weight'] + \
            #        pan2[app_from][app_to]['weight']

    return 2 * mcs / float(medges)


# calculate cosine similarity of two vectors
def sim_cosine(u, v):
    return numpy.dot(u, v) / (math.sqrt(numpy.dot(u, u)) * math.sqrt(numpy.dot(v, v)))


# judge whether url of app exists
def url_exists(url):
    try:
        if urllib2.urlopen(url).geturl() == url:
            return True
    except urllib2.HTTPError:
        pass

    return False


# get apps for evolution analysis
def load_eapps():
    return load_content(APPSC2_TXT)


# get all version numbers of an app
def get_versions(app):
    return sorted(pickle_load(VERSION_PATH % app).keys())


if __name__ == '__main__':
    pass
