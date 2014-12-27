from utils.constants import *
import xml.etree.cElementTree as ET


def xml_parer():
    tree = ET.parse(XML_PATH)
    intent_filter = []
    ns = {'android': '{http://schemas.android.com/apk/res/android}'}
    keys = ['mimeType', 'scheme', 'host', 'port', 'path', 'pathPrefix', 'pathPattern']

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

        piece = {'action': action, 'category': category, 'data': data}
        [piece.pop(key) for key in piece.copy() if not piece[key]]
        if piece: intent_filter.append(piece)

    return intent_filter

if __name__ == '__main__':
    for f in xml_parer():
        print f