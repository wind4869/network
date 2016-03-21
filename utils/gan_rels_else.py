# -*- coding: utf-8 -*-

import Levenshtein

from utils.funcs_rw import *


# get io matching result
def io_match(app_from, app_to):
    count = 0
    ov, iv = outputs(app_from), inputs(app_to)
    for i in [a * b for a, b in zip(ov, iv)]:
        if i: count += 1
    return float(count) / 9


# calculate similarity of two collections
def sim_collection(l1, l2):
    if not l1: return 0
    s = set(l1) | set(l2)
    return len(set(l1) & set(l2)) / float(len(s)) if s else 0


# calculate similarity of two intent-filers
def sim_filters(f1, f2):
    length = len([f for f in f1 if f in f2])
    return float(length) / (len(f1) + len(f2) - length) if length else 0


# calculate similarity of inputs or outputs
def sim_io(u, v):
    count = 0
    for i in [a * b for a, b in zip(u, v)]:
        if i: count += 1
    return float(count) / 9


# get sim matching result
def sim_match(app_from, app_to):
    # calculate collection similarity
    sim_cats = sim_collection(categories(app_from), categories(app_to))
    sim_tags = sim_collection(tags(app_from), tags(app_to))
    sim_perms = sim_collection(permissions(app_from), permissions(app_to))
    sim_intents = sim_collection(explicits(app_from).extend(implicits(app_to)),
                                 explicits(app_to).extend(implicits(app_to)))
    sim_ifilters = sim_filters(filters(app_from), filters(app_to))

    sim_inputs = sim_io(inputs(app_from), inputs(app_to))
    sim_outputs = sim_io(outputs(app_from), outputs(app_to))

    # calculate cosine similarity
    ivec_from, ivec_to = [
        [likesRate(app), likesCount(app), dislikesCount(app), downloadCount(app),
         installedCount(app), commentsCount(app)] for app in app_from, app_to]
    sim_ivec = sim_cosine(ivec_from, ivec_to)

    # calculate Levenshtein similarity
    desc_from, desc_to = [description(app) for app in app_from, app_to]
    sim_desc = Levenshtein.ratio(desc_from, desc_to) if desc_from and desc_to else 0

    sim = reduce(lambda a, b: a + b,
                 [sim_cats, sim_tags, sim_perms,
                  sim_intents, sim_ifilters, sim_inputs,
                  sim_outputs, sim_ivec, sim_desc]) / 9

    # calculate the contribution of similar apps
    sims_from, sims_to = [sims(app) for app in app_from, app_to]
    if app_to in sims_from or app_from in sims_to: sim = sim / 2 + 0.5

    return sim if sim > 0.6 else 0


if __name__ == '__main__':
    pass
