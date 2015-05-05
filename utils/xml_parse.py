# -*- coding: utf-8 -*-

import re
import xml.etree.cElementTree as ET


def parer(xml):
    filters = []
    ns = {'android': '{http://schemas.android.com/apk/res/android}'}
    keys = ['mimeType', 'scheme', 'host', 'port', 'path', 'pathPrefix', 'pathPattern']

    try:
        tree = ET.parse(xml)
    except ET.ParseError:
        print 'cElementTree.ParseError in file %s' % xml
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
                if value: piece[key] = value
            if piece: data.append(piece)

        piece = {'actions': action, 'categories': category, 'datas': data}
        [piece.pop(key) for key in piece.copy() if not piece[key]]
        filters.append(piece)

    perms = set([])
    perm_pattern = re.compile(r'^android.permission')
    for p in tree.iter('uses-permission'):
        perm_str = p.attrib[ns['android'] + 'name']
        if perm_pattern.match(perm_str):
            perms.add(perm_str.split('.')[2])

    return filters, list(perms)
