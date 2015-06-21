# -*- coding: utf-8 -*-

import Levenshtein

from utils.funcs_rw import *


# calculate the similarity of two IO vectors
def v_sim(v1, v2):
    return reduce(lambda a, b: a + b, [a * b for a, b in zip(v1, v2)])


# get io tag matching result
def iotag_match(app_from, app_to):
    v1, v2 = [vectors(app) for app in (app_from, app_to)]
    return v_sim(v1[1], v2[0])


# calculate the similarity of categories or tags
def c_sim(l1, l2):
    return len(set(l1) & set(l2))


# get sim matching result
def sim_match(app_from, app_to):
    if Levenshtein.ratio(app_from, app_to) > 0.1:
        c = c_sim(categories(app_from), categories(app_to))
        t = c_sim(tags(app_from), tags(app_to))
        if c > 0 and t > 2:
            return c + t


if __name__ == '__main__':
    pass
