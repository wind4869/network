# -*- coding: utf-8 -*-

from utils.functions import *
from math import ceil
from random import choice


# Method 1st: use "gan->pan" pattern to recommend
def recommend_gan_based(uid, pan):
    gan = load_gan()
    # gan, pan = load_gan(), load_pan(uid)
    apps_gan, apps_pan = [set(lan.nodes()) for lan in gan, pan]

    result = {}  # record score of each app candidate
    for app in apps_gan - apps_pan:
        result.setdefault(app, 0)

    # the score is: Σ(edge weight * node weight)
    for common in apps_pan & apps_gan:
        for app in set(gan.predecessors(common)) - apps_pan:
            result[app] += gan[app][common]['weight'] * pan.node[common]['weight']
        for app in set(gan.successors(common)) - apps_pan:
            result[app] += gan[common][app]['weight'] * pan.node[common]['weight']

    temp = []
    for app, score in result.iteritems():
        temp.append((app, round(score, 2)))

    return sorted(temp, key=lambda x: x[1], reverse=True)


# use "pan of u2->pan of u1" pattern to recommend
def recommend_by_pan(pan_base, pan_other):
    apps_base, apps_other = [set(pan.nodes()) for pan in pan_base, pan_other]
    sim = g_sim(pan_base, pan_other)

    if not (apps_base & apps_other) or not sim:
        return {}

    scores = {}  # record score of each app candidate
    for app in apps_other - apps_base:
        scores.setdefault(app, 0)

    # the score is: Σ(sim * edge weight * node weight)
    for common in apps_base & apps_other:
        for app in set(pan_other.predecessors(common)) - apps_base:
            scores[app] += sim * pan_other[app][common]['weight'] * pan_base.node[common]['weight']
        for app in set(pan_other.successors(common)) - apps_base:
            scores[app] += sim * pan_other[common][app]['weight'] * pan_base.node[common]['weight']

    return scores


# Method 2nd: use "pans->pan" pattern to recommend
def recommend_pan_based(uid, pan_base):
    # pan_base = load_pan(uid)
    pans_other = [load_pan(u) for u in load_uids() if u != uid]

    result = {}  # record score of each app candidate
    for pan_other in pans_other:
        scores = recommend_by_pan(pan_base, pan_other)
        for app in scores:
            if app in result:
                result[app] += scores[app]
            else:
                result[app] = scores[app]

    temp = []
    for app, score in result.iteritems():
        temp.append((app, round(score, 2)))

    return sorted(temp, key=lambda x: x[1], reverse=True)


# get "user-app-rating" matrix from pan
def get_ratings(uid, pan_base):
    capps, users = load_capps(), load_uids()
    num_capps, num_users = [len(l) for l in capps, users]
    ratings = [[0 for i in xrange(num_capps)] for j in xrange(num_users)]

    for index in xrange(num_users):
        pan = load_pan(users[index])
        if users[index] == uid:
            pan = pan_base
        for app in pan.nodes():
            if app in capps:
                ratings[index][capps.index(app)] = pan.node[app]['weight']

    f_train = open(TRAIN_SET, 'w')
    f_test = open(TEST_SET, 'w')

    for i in xrange(num_users):
        for j in xrange(num_capps):
            f_target = f_train if ratings[i][j] else f_test
            f_target.write('%d %d %f\n' % (i, j, ratings[i][j]))

    f_train.close()
    f_test.close()


# get output file the predict result
def get_output(uid, pan_base):
    # step 1: prepare "user-app-rating" matrix
    get_ratings(uid, pan_base)
    # step 2: train the model
    run(TRAIN_CMD)
    # step 3: do predict using the model
    run(PREDICT_CMD)


# Method 3rd: MF(matrix factorization) method on usage records
def recommend_mf_based(uid, pan_base):
    get_output(uid, pan_base)
    capps, users = load_capps(), load_uids()
    num_capps, num_users = [len(l) for l in capps, users]
    ratings = [[0 for i in xrange(num_capps)] for j in xrange(num_users)]

    # simply read the result from output file
    f = open_in_utf8(OUTPUT)
    for line in f.readlines():
        temp = line.strip().split()
        user = int(temp[0])
        item = int(temp[1])
        rating = float(temp[2])
        ratings[user][item] = rating
    f.close()

    temp = []
    result = ratings[users.index(uid)]
    for index in xrange(num_capps):
        temp.append((capps[index], result[index]))

    return sorted(temp, key=lambda x: x[1], reverse=True)


# get training and test set (8/2)
def get_dataset(uid):
    pan = load_pan(uid)

    # remove native apps
    training_set = set(pan.nodes()) - set(load_napps())
    test_set = set([])

    # the number of apps should in test set
    num_test = int(ceil(len(training_set) / 5.0))

    # randomly create two sets
    for i in xrange(num_test):
        app = choice(list(training_set))
        training_set.remove(app)
        test_set.add(app)

    return training_set, \
        test_set, \
        nx.subgraph(pan, training_set)


# get precision and recall
def evaluate(uid, topk, recommend_algorithm):

    training_set, test_set, pan = get_dataset(uid)
    print '(1) Training: %d, Test: %d' % (len(training_set), len(test_set))

    result = [x[0] for x in recommend_algorithm(uid, pan)[:topk]]
    num_hit = len(test_set & set(result))
    print '(2) Top: %d, Hit: %d' % (topk, num_hit)

    precision = num_hit * 1.0 / len(result)
    recall = num_hit * 1.0 / len(test_set)
    f_score = 2 * precision * recall / (precision + recall) \
        if precision or recall else 0
    print '(3) Precision: %f, Recall: %f, F-Score: %f' \
          % (precision, recall, f_score)

    return precision, recall, f_score


if __name__ == '__main__':
    # print recommend_gan_based('a1')
    # print recommend_pan_based('a1')
    # print recommend_mf_based('a1')

    # evaluate('a1', 100, recommend_gan_based)
    evaluate('a1', 10, recommend_pan_based)
    # evaluate('a1', 30, recommend_mf_based)
