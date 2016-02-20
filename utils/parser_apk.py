# -*- coding: utf-8 -*-

import xml.etree.cElementTree as et
from utils.funcs_rw import *
from utils.consts_global import *


# use curl to download app
def apk_download(pkg):
    print '> downloading %s.apk ... ' % pkg
    run(APK_CMD % (pkg, pkg))


# use dex2jar to get jar by decompiling apk
def dex_decompile(pkg):
    print '-> decompiling classes.dex for %s.jar ... ' % pkg
    run(D2J_CMD % (pkg, pkg))


# use APKParser to extract AndroidManifest.xml from apk
def xml_extract(pkg):
    print '--> extracting AndroidManifest.xml ... '
    run(XML_CMD % (pkg, pkg))


# get jar and AndroidManifest.xml
def apk_decompile(pkg):
    print '> decompiling %s.apk ... ' % pkg

    path = APK_PATH % pkg
    if os.path.exists(path):
        dex_decompile(pkg)
        xml_extract(pkg)
    else:
        print '[parser_xml][File not exists]: %s' % path
        return


# parse xml to extract intent-filters and permissions(perms)
def get_filters(app):
    filters = []
    ns = {'android': '{http://schemas.android.com/apk/res/android}'}
    keys = ['mimeType', 'scheme', 'host', 'port', 'path', 'pathPrefix', 'pathPattern']

    path = XML_PATH % app
    if not os.path.exists(path):
        print '[parser_xml][File not exists]: %s' % path
        return [], []

    try:
        tree = et.parse(path)
    except et.ParseError:
        print '[parser_xml][cElementTree.ParseError]: %s' % path
        return [], []

    for f in tree.iter('intent-filter'):
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


# extract explicit and implicit intents from raw intents
def get_intents(app):
    explicits = []  # explict intents
    implicits = []  # implicit intents

    # raw string of intents
    raw_intents = load_rintents(app)
    # pattern for removing self-calling intents
    self_pattern = re.compile('^' + app.replace('.', '\.'))

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
                                    explicits.append(class_name)
                        else:
                            intent.pop('explicit')  # implicit intents
                            if intent:
                                implicits.append(intent)

    return explicits, implicits


if __name__ == '__main__':
    pass
