# -*- coding: utf-8 -*-

from utils.functions import *


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
    return True


# get implicits matching result
def implicit_match(app_from, app_to):
    implicit_intents = implicits(app_from)
    intent_filters = filters(app_to)

    if not implicit_intents or not intent_filters:
        return 0

    for i in implicit_intents:
        for f in intent_filters:
            if implicit_match_one(i, f):
                return 1

    return 0


# get explicits matching result
def explicit_match(app_from, app_to):
    explicit_intents = explicits(app_from)
    if not explicit_intents:
        return 0

    pattern = re.compile('^' + app_to.replace('.', '\.'))
    for intent in explicit_intents:
        if pattern.match(intent):
            return 2

    return 0


if __name__ == '__main__':
    pass
