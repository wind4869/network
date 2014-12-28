# -*- coding: utf-8 -*-

import re
from utils.graph import *
from utils.vector_funs import *
from itertools import permutations


# get content from file
def content(path):
    f = open(path)
    lines = f.readlines()
    f.close()
    return eval(lines[0]) if lines else None


# get raw intents, process, return (explicits, implicits)
def get_intents(app):
    commons, systems = [], []  # two kinds of explict intents
    implicits = []  # implicit intents

    # raw string of intents
    raw_intents = content(INTENT_PATH % app)
    # pattern for removing self-calling intents
    self_pattern = re.compile(packageName(app))
    # pattern for recognizing system-app-calling intents
    sys_pattern = re.compile('com.android')

    if raw_intents:
        for typed_intens in [raw_intents.get(i) for i in ['called', 'queried']]:
            if typed_intens:
                for key in typed_intens:
                    for intent in typed_intens[key]:
                        if intent['explicit'] == 'true':  # explicit intents
                            class_name = intent.get('class')
                            if class_name:
                                class_name = class_name.replace(r'/', r'.')  # remove self-calling intents
                                if not self_pattern.match(class_name):
                                    if sys_pattern.match(class_name):  # system-app-calling intents
                                        systems.append(class_name)
                                    else:
                                        commons.append(class_name)
                        else:
                            intent.pop('explicit')  # implicit intents
                            if intent:
                                implicits.append(intent)
    return {'common': commons, 'system': systems}, implicits


def get_intent_filters(app):
    return content(INTENT_FILTER_PATH % app)


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
    uri_pattern = re.compile(get_uri(data))

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
        for intent_filter in intent_filters:
            if implicit_match_one(implicit, intent_filter):
                return True
    return False


def explicit_match(commons, package_name):
    pattern = re.compile(package_name)
    for intent in commons:
        if pattern.match(intent):
            return True
    return False


def get_intent_edges(apps):
    explicit_edges, implicit_edges, system_edges = \
        get_edges(apps), get_edges(apps), get_edges(apps)

    for app1, app2 in permutations(apps, 2):
        explicits, implicits = get_intents(app1)
        intent_filters = get_intent_filters(app2)

        # check explicit comment intents
        if explicit_match(explicits['common'], packageName(app2)):
            explicit_edges[app1].add(app2)

        # check implicit intents
        if implicit_match(implicits, intent_filters):
            implicit_edges[app1].add(app2)

        # check explicit system intents
        for app in explicits['system']:
            system_edges[app1].add(app.split('.')[2])

    return explicit_edges, implicit_edges, system_edges


def draw(edges, name):
    graph = Graph()
    graph.add_edges(edges)
    graph.draw(ROOT_DIR + 'test/%s.jpg' % name)


if __name__ == '__main__':
    apps = load_apps(NUMBER_FOR_TEST)
    explicit_edges, implicit_edges, system_edges = get_intent_edges(apps)

    draw(explicit_edges, 'explicit')
    draw(implicit_edges, 'implicit')
    draw(system_edges, 'system')
