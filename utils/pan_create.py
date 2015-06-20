# -*- coding: utf-8 -*-

from utils.pan_usage import *


# create pan by uid
def create_pan(uid):
    gan = load_gan()
    uan = load_uan(uid)

    apps = set(gan.nodes()) & set(uan.nodes())
    subgan = nx.subgraph(gan, apps)
    print subgan.nodes()


if __name__ == '__main__':
    for uid in ['F01']:
        create_pan(uid)
