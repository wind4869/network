from utils.db_read import *
from utils.global_consts import *
import xml_parse.etree.cElementTree as ET


def xml_parer(xml):
    tree = ET.parse(xml)
    intent_filters = []
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

        piece = {'actions': action, 'categories': category, 'datas': data}
        [piece.pop(key) for key in piece.copy() if not piece[key]]
        if piece:
            intent_filters.append(piece)

    return intent_filters


if __name__ == '__main__':
    apps = load_apps(NUMBER_FOR_TEST)
    for app in apps:
        print '%d intent-filters extracting ---> %s.apk' % (apps.index(app), app)
        f = open(INTENT_FILTER_PATH % app, 'w')
        f.write(str(xml_parer(XML_PATH % app)) + '\n')