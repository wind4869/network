# -*- coding: utf-8 -*-

import codecs
import cPickle as pickle
from utils.db_connect import *
from utils.consts_global import *
from igraph import *

# get db object
appDetails = getAppDetails()

# open file use utf-8 encoding
open_in_utf8 = lambda filename: \
    codecs.open(filename, encoding='utf-8')


# data_dict = [set([]), set([...]), ... , set([...])]
def load_data_dict():
    data_dict = [set([])]
    f = open_in_utf8(DATA_DICT_TXT)
    for line in f.readlines():
        data_dict.append(set(line.strip().split('|')))
    f.close()
    return data_dict


# tag_io = {tag: {'I': set([1, 2, ...]), 'O': set([3, 4, ...])}, ... }
def load_tag_io():
    tag_io, tag_all = {}, set([])
    f = open_in_utf8(TAG_IO_TXT)
    parse = lambda s: set([int(i) for i in s.split(',')]) if s else set([])
    for line in f.readlines():
        tag, input_str, output_str = line.strip().split('|')
        tag_io[tag] = {'I': parse(input_str), 'O': parse(output_str)}
        tag_all.add(tag)
    f.close()
    return tag_io, tag_all


# perm_dict = {permission: [native_app1, native_app2, ...], ... }
def load_perms_natives():
    perm_dict = {}
    f = open_in_utf8(PERM_NATIVES_TXT)
    for line in f.readlines():
        permission, native_apps = line.strip().split('->')
        perm_dict[permission] = native_apps.split(',') if native_apps else []
    f.close()
    return perm_dict


# load the dict for mapping the app name in pan
def load_map_dict():
    map_dict = {}
    f = open_in_utf8(MAP_DICT_TXT)
    for line in f.readlines():
        key, value = line[:-1].split('->')
        map_dict[key] = value
    return map_dict


def load_content(path):
    f = open_in_utf8(path)
    content = [line[:-1] for line in f.readlines()]
    f.close()
    return content


# load some number of apps to test
def load_apps(number=NUMBER_OF_APP):
    return load_content(APPS_TXT)[:number]


# load all 14 categories
def load_categories():
    return load_content(CATEGORIES_TXT)


# load all native apps
def load_natives():
    return [n.split('->')[0] for n in load_content(NATIVES_TXT)]


# load all apps
def load_all_apps():
    return load_apps() + load_natives()


def description(app):
    return appDetails.find_one({'title': app})['description']


def categories(app):
    return appDetails.find_one({'title': app})['categories']


def tags(app):
    return appDetails.find_one({'title': app})['tags']


def permissions(app):  # gotten from wandoujia website
    return appDetails.find_one({'title': app})['permissions']


def perms(app):  # extracted form xml file
    return appDetails.find_one({'title': app})['perms']


def packageName(app):
    return appDetails.find_one({'title': app})['packageName']


def explicit_intents(app):
    return appDetails.find_one({'title': app})['explicits']


def implicit_intents(app):
    return appDetails.find_one({'title': app})['implicits']


def intent_filters(app):
    return appDetails.find_one({'title': app})['filters']


def likesCount(app):
    return appDetails.find_one({'title': app})['likesCount']


def downloadCount(app):
    return appDetails.find_one({'title': app})['downloadCount']


# edges = {app1: set([]), app2: set([]), ...}
def get_edges(apps):
    edges = {}
    [edges.setdefault(app, set([])) for app in apps]
    return edges


def pickle_dump(obj, path):
    pickle.dump(obj, open(path, 'w'))


def pickle_load(path):
    return pickle.load(open(path))


def dump_clusters(graph, clusters, uid):
    result = []
    for c in clusters:
        result.append([graph.vs[i]['name'] for i in c])
    pickle_dump(result, CLUSTERS_TXT % uid)


def load_clusters(uid):
    return pickle_load(CLUSTERS_TXT % uid)


def dump_network(network, path):
    pickle_dump(network, path)


def load_network(path):
    return pickle_load(path)


# get Global App Network(GAN) by test mask, number of app, test date
def load_gan(test=ALL_MASK, number=NUMBER_OF_APP, date='0118'):
    return load_network(GAN_TXT % (test, number, date))


# get Personal App Network(PAN) by uid
def load_pan(uid):
    return load_network(PAN_TXT % uid)


# get usage edges by uid
def load_usage_edges(uid):
    return load_network(USAGE_TXT % uid)
