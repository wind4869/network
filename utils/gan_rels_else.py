# -*- coding: utf-8 -*-

import Levenshtein

from utils.funcs_rw import *


# calculate the similarity of two IO vectors
def v_sim(v1, v2):
    s1, s2 = [reduce(lambda a, b: a + b, v) for v in v1, v2]
    if not s1 or not s2:
        return 0
    return reduce(
        lambda a, b: a + b,
        [(a / float(s1) + b / float(s2)) / 2 if a and b else 0 for a, b in zip(v1, v2)])


# get io tag matching result
def iotag_match(app_from, app_to):
    v1, v2 = [vectors(app) for app in (app_from, app_to)]
    return v_sim(v1[1], v2[0])


# calculate the similarity of categories or tags
def ct_sim(l1, l2):
    return len(set(l1) & set(l2)) / float(min(len(l1), len(l2)))


# calculate the similarity of likesCount or downloadCount
def n_sim(n1, n2):
    return 1 - abs(n1 - n2) / float(max(n1, n2))


# get sim matching result
def sim_match(app_from, app_to):
        lev_sim = Levenshtein.ratio(app_from, app_to)
        cat_sim = ct_sim(categories(app_from), categories(app_to))
        tag_sim = ct_sim(tags(app_from), tags(app_to))
        like_sim = n_sim(likesCount(app_from), likesCount(app_to))
        down_sim = n_sim(downloadCount(app_from), downloadCount(app_to))

        result = (lev_sim + cat_sim + tag_sim + like_sim + down_sim) / float(5)
        return result if result > 0.7 else 0


if __name__ == '__main__':
    pass
    # from itertools import combinations
    #
    # for app_from, app_to in combinations(load_capps(), 2):
    #     result = sim_match(app_from, app_to)
    #     if result > 0:
    #         print result