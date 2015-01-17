# -*- coding: utf-8 -*-

import codecs
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


# perm_dict = {permission: [sys_app1, sys_app2, ...], ... }
def load_perm_dict():
    perm_dict = {}
    f = open_in_utf8(PERM_DICT_TXT)
    for line in f.readlines():
        permission, sys_apps = line.strip().split('|')
        perm_dict[permission] = sys_apps.split(',') if sys_apps else []
    f.close()
    return perm_dict


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


def description(app):
    return appDetails.find_one({'title': app})['description']


def categories(app):
    return appDetails.find_one({'title': app})['categories']


def tags(app):
    return appDetails.find_one({'title': app})['tags']


def permissions(app):
    return appDetails.find_one({'title': app})['permissions']


def packageName(app):
    return appDetails.find_one({'title': app})['packageName']


def explicit_intents(app):
    return appDetails.find_one({'title': app})['explicits']


def implicit_intents(app):
    return appDetails.find_one({'title': app})['implicits']


def intent_filters(app):
    return appDetails.find_one({'title': app})['filters']