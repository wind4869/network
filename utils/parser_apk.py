# -*- coding: utf-8 -*-

import re
import xml.etree.cElementTree as et
from utils.funcs_rw import *
from utils.consts_global import *


# use curl to download app
def apk_download(app):
    print '> downloading %s.apk ... ' % app
    run(DOWNLOAD_CMD % (app, packageName(app)))


# use dex2jar to get jar by decompiling apk
def dex_decompile(app):
    print '-> decompiling classes.dex for %s.jar ... ' % app
    run(D2J_CMD % (app, app))


# use APKParser to extract AndroidManifest.xml from apk
def xml_extract(app):
    print '--> extracting AndroidManifest.xml ... '
    run(XML_CMD % (app, app))


# get jar and AndroidManifest.xml
def apk_decompile(app):
    print '> decompiling %s.apk ... ' % app
    dex_decompile(app)
    xml_extract(app)


# parse xml to extract intent-filters and permissions(perms)
def get_filters(xml):
    filters = []
    ns = {'android': '{http://schemas.android.com/apk/res/android}'}
    keys = ['mimeType', 'scheme', 'host', 'port', 'path', 'pathPrefix', 'pathPattern']

    try:
        tree = et.parse(xml)
    except et.ParseError:
        print '[parser_xml][cElementTree.ParseError]: %s' % xml
        return [], []

    for f in tree.iter('intent-filters'):
        action, category, data = [], [], []
        for a in f.iter('action'):
            action.append(a.attrib[ns['android'] + 'name'])
        for c in f.iter('category'):
            category.append(c.attrib[ns['android'] + 'name'])
        for d in f.iter('data'):
            piece, attrs = {}, d.attrib
            for key in keys:
                value = attrs.get(ns['android'] + key)
                if value:
                    piece[key] = value
            if piece:
                data.append(piece)

        piece = {'actions': action, 'categories': category, 'datas': data}
        [piece.pop(key) for key in piece.copy() if not piece[key]]
        filters.append(piece)

    perms = []
    perm_pattern = re.compile(r'^android\.permission')
    for p in tree.iter('uses-permission'):
        perm_str = p.attrib[ns['android'] + 'name']
        if perm_pattern.match(perm_str):
            perms.append(perm_str.split('.')[2])

    return filters, perms


# get raw intents, process, return (explicits, implicits)
def get_intents(app):
    commons, natives = [], []  # two kinds of explict intents
    implicits = []  # implicit intents

    # raw string of intents
    raw_intents = load_rintents(INTENT_PATH % app)
    # pattern for removing self-calling intents
    self_pattern = re.compile('^' + packageName(app).replace('.', '\.'))
    # pattern for recognizing native-app-calling intents
    native_pattern = re.compile(r'^com\.android\.')

    if raw_intents:
        for typed_intents in [raw_intents.get(i) for i in ['called', 'queried']]:
            if typed_intents:
                for key in typed_intents:
                    for intent in typed_intents[key]:
                        if 'explicit' not in intent:
                            continue
                        if intent['explicit'] == 'true':  # explicit intents
                            class_name = intent.get('class')
                            if class_name:
                                class_name = class_name.replace('/', '.')  # remove self-calling intents
                                if not self_pattern.match(class_name):
                                    if native_pattern.match(class_name):  # native-app-calling intents
                                        natives.append(class_name)
                                    else:
                                        commons.append(class_name)
                        else:
                            intent.pop('explicit')  # implicit intents
                            if intent:
                                implicits.append(intent)

    return commons, natives, implicits


# nats = { u'@信息': 2, u'@电话': 3, ... }
def get_nats(app):
    result = {}
    permdict = load_permdict()
    natdict = load_natdict()
    appmap = load_appmap()

    # get link to native apps by permissions
    for p in perms(app):
        if p in permdict:
            natives = [natdict[key] for key in permdict[p]]
            for n in natives:
                result.setdefault(n, 0)
                result[n] += 1

    # get link to native apps by intents
    for s in explicits(app)['natives']:
        key = s.split('.')[2]
        value = natdict.get(key)
        if value:
            result.setdefault(appmap[value], 0)
            result[appmap[value]] += 1

    return result


if __name__ == '__main__':
    pass
