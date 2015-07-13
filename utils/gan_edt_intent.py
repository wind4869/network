# -*- coding: utf-8 -*-

import re

from utils.funcs_rw import *


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


# simulate the process of intent matching
def implicit_match_one(implicit, filter):
    if not check_action(implicit.get('action'), filter.get('actions')):
        return False
    if not check_category(implicit.get('categories'), filter.get('categories')):
        return False
    if not check_data(implicit.get('uri'), implicit.get('mimeType'), filter.get('datas')):
        return False
    print implicit, filter
    return True


# get implicit matching result
def implicit_match(app_from, app_to):
    result = 0
    implicit_intents = implicits(app_from)
    intent_filters = filters(app_to)

    if not implicit_intents or not intent_filters:
        return result

    for i in implicit_intents:
        for f in intent_filters:
            if implicit_match_one(i, f):
                result += 1

    return float(result) / (len(implicit_intents) + len(intent_filters))


# get explicit matching result
def explicit_match(app_from, app_to):
    result = 0
    commons = explicits(app_from)['commons']
    package = packageName(app_to)
    if not commons:
        return result

    pattern = re.compile('^' + package.replace('.', '\.'))
    for intent in commons:
        if pattern.match(intent):
            result += 1

    return float(result) / len(commons)


if __name__ == '__main__':
    pass
    from itertools import combinations

    for app_from, app_to in combinations(load_capps(), 2):
        result = implicit_match(app_from, app_to)
        if result > 0:
            print result