# -*- coding: utf-8 -*-

from utils.pan_usage import *


# create pan with subgan and uan
def create_pan(uid):
    gan = load_gan()
    uan = load_uan(uid)

    # filter gan by apps in common
    apps = set(gan.nodes()) & set(uan.nodes())
    subgan = nx.subgraph(gan, apps)
    uan = nx.subgraph(uan, apps)

    uan_only = set(uan.edges()) - set(subgan.edges())
    pan = subgan  # create pan on the basis of subgan

    # add nodes' weight from uan
    for node in pan.nodes():
        pan.node[node]['weight'] = uan.node[node]['weight']

    # add edges only in uan
    for u, v in uan_only:
        pan.add_edge(u, v, weights=uan[u][v]['weights'])
        pan[u][v]['weight'] = 0

    # add usg weight from uan
    for u, v in subgan.edges():
        if uan.has_edge(u, v):
            pan[u][v]['weights'][INDEX.USG] = uan[u][v]['weights'][INDEX.USG]

    # adjust global weight of pan
    mw = 0
    for u, v in pan.edges():
        gan_part = pan[u][v]['weight']
        usg_part = get_weights(pan, u, v)[INDEX.USG]
        pan[u][v]['weight'] = temp = sqrt(gan_part + usg_part) / 2
        if temp > mw:
            mw = temp

    # divide max weight to normalize
    for u, v in pan.edges():
        pan[u][v]['weight'] /= mw

    # dump pan to pickle file
    dump_pan(uid, pan)


if __name__ == '__main__':
    for uid in ['F02']:
        create_pan(uid)
