# -*- coding: utf-8 -*-

import re
from utils.rw_funcs import *
from itertools import combinations

# f_filters = open(FILTERS_MATCHED, 'a')


def check_action(action, actions):
    if not actions:
        return False
    if not action:
        return True
    if action in actions:
        return True
    return False


def check_category(c1, c2):
    if not c1:
        return False
    if c2 and set(c1).issubset(c2):
        return True
    return False


def get_uri(data):
    scheme, host, port = [data.get(key) for key in ['scheme', 'host', 'port']]
    if not scheme:
        return ''
    if not host:
        return scheme
    if not port:
        return '%s://%s' % (scheme, host)
    path_pattern = ''
    for s in [data.get(key) for key in ['path', 'pathPrefix', 'pathPattern']]:
        if s:
            path_pattern = s
            break
    if not path_pattern:
        return '%s://%s:%s' % (scheme, host, port)
    else:
        return '%s://%s:%s/%s' % (scheme, host, port, path_pattern)


def check_data_one(uri, mimeType, data):
    uri_pattern = re.compile(get_uri(data).replace('*', '.*'))

    # case # 1
    if not uri and mimeType:
        if mimeType == data.get('mimeType') \
                and not data.get('scheme'):
            return True
        return False

    # case # 2
    if uri and not mimeType:
        if not data.get('scheme'):
            return False
        if uri_pattern.match(uri):
            return True
        return False

    # case # 3
    if uri and mimeType:
        if not (data.get('mimeType') or data.get('scheme')):
            return False
        if mimeType == data.get('mimeType') and uri_pattern.match(uri):
            return True
        return False


def check_data(uri, mineType, datas):
    if not (uri or mineType):
        return False
    if not datas:
        return False
    for data in datas:
        if check_data_one(uri, mineType, data):
            return True
    return False


def implicit_match_one(implicit, intent_filter):
    if not check_action(implicit.get('action'), intent_filter.get('actions')):
        return False
    if not check_category(implicit.get('categories'), intent_filter.get('categories')):
        return False
    if not check_data(implicit.get('uri'), implicit.get('mimeType'), intent_filter.get('datas')):
        return False
    return True


def implicit_match(implicits, intent_filters):
    for implicit in implicits:
        if not intent_filters:
            continue
        for intent_filter in intent_filters:
            if implicit_match_one(implicit, intent_filter):
                # f_filters.write(str(intent_filter) + '\n')
                return True
    return False


def explicit_match(commons, package_name):
    pattern = re.compile(package_name)
    for intent in commons:
        if pattern.match(intent):
            return True
    return False


def get_intent_edges(apps):
    intent_edges = get_edges(apps)
    for app_pair in combinations(apps, 2):
        explicits_pair = [explicit_intents(app) for app in app_pair]
        implicits_pair = [implicit_intents(app) for app in app_pair]
        filters_pair = [intent_filters(app) for app in app_pair]

        for i in xrange(2):
            if explicit_match(explicits_pair[i]['commons'], packageName(app_pair[1 - i])) or \
                    implicit_match(implicits_pair[i], filters_pair[1 - i]):
                intent_edges[app_pair[i]].add(app_pair[1 - i])

    return intent_edges
