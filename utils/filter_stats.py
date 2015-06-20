# -*- coding: utf-8 -*-

from utils.funcs_rw import *


# create 1-itemset candidate
def createC1(dataSet):
    C1 = []
    for record in dataSet:
        for item in record:
            if not [item] in C1:
                C1.append([item])

    C1.sort()
    return map(frozenset, C1)


# get Lk from Ck by scanning data set
def scanD(D, Ck, minSupport):
    tSupportData = {}
    for record in D:
        for itemset in Ck:
            if itemset.issubset(record):
                tSupportData.setdefault(itemset, 0)
                tSupportData[itemset] += 1
    retList = []
    supportData = {}
    numItems = float(len(D))
    for itemset in tSupportData:
        support = tSupportData[itemset] / numItems
        if support >= minSupport:
            retList.append(itemset)
        supportData[itemset] = support
    return retList, supportData


# get Ck+1 from Lk
def aprioriGen(Lk, k):
    retList = []
    lenLk = len(Lk)
    for i in xrange(lenLk):
        for j in xrange(i + 1, lenLk):
            L1 = list(Lk[i])[:k - 2]; L2 = list(Lk[j])[:k - 2]
            L1.sort(); L2.sort()
            if L1 == L2:  # if first k-2 elements are equal
                retList.append(Lk[i] | Lk[j])  # set union
    return retList


def apriori(dataSet, minSupport=0.1):
    C1 = createC1(dataSet)
    D = map(set, dataSet)
    L1, supportData = scanD(D, C1, minSupport)
    L = [L1]
    k = 2
    while (len(L[k - 2]) > 0):
        Ck = aprioriGen(L[k - 2], k)
        Lk, supK = scanD(D, Ck, minSupport)
        supportData.update(supK)
        L.append(Lk)
        k += 1
    return L, supportData


def filter_frequent_pattern(dataSet):
    k = 1
    code_dict = pickle_load(CODE_DICT)
    L, supportData = apriori(dataSet)
    for itemset in L:
        if itemset:
            print '\nfrequent %d-itemset:\n' % k
        for item in itemset:
            print '-> {%s} sup: %.2f' % (item, supportData[item])
            for f in item:
                print f, code_dict[f]
        k += 1


if __name__ == '__main__':
    filter_frequent_pattern()
