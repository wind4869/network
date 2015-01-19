# -*- coding: utf-8 -*-

import codecs
import cPickle as pickle
from utils.db_connect import *
from utils.global_consts import *

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
def loaa_all_apps():
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


# edges = {app1: set([]), app2: set([]), ...}
def get_edges(apps):
    edges = {}
    [edges.setdefault(app, set([])) for app in apps]
    return edges


# use pickle to store the out edges of app network
def store_network(edges_out, path):
    pickle.dump(edges_out, open(path, 'w'))


# load out edges and form in edges
def load_network(path):
    edges_out = pickle.load(open(path))
    edges_in = {}

    for app_from, app_tos in edges_out.iteritems():
        for app_to in app_tos:
            edges_in.setdefault(app_to, set([]))
            edges_in[app_to].add(app_from)

    return edges_out, edges_in


# get Global App Network(GAN) by test mask, number of app, test date
def load_gan(test=31, number=NUMBER_OF_APP, date='0118'):
    return pickle.load(open(GAN_TXT % (test, number, date)))


# get Personal App Network(PAN) by uid
def load_pan(uid):
    return pickle.load(open(PAN_TXT % uid))


if __name__ == '__main__':
    gan = load_gan(ALL_MASK)
    print gan[u'微信']
