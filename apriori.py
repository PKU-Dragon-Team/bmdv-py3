#!/usr/bin/env python
# encoding: utf-8

import itertools


def loadDataSet():
    return [[1, 3, 4], [2, 3, 5], [1, 2, 3, 5], [2, 5]]


def is_subseq(a, a_start, b, b_start):
    n = len(a)
    m = len(b)

    if b_start == m:
        return True
    elif a_start == n:
        return False

    i = a_start
    j = b_start
    while i < n:
        if a[i] == b[j]:
            return is_subseq(a, i + 1, b, j + 1)
        else:
            i += 1

    return False


def createC1(dataSet):
    C1 = []
    for transaction in dataSet:
        for item in transaction:
            if not [item] in C1:
                C1.append([item])

    C1.sort()
    return map(tuple, C1)#use frozen set so we can use it as a key in a dict


def scanD(D, Ck, minSupport):
    ssCnt = {}
    for tid in D:
        for can in Ck:
            if is_subseq(tid, 0, can, 0):
                if not ssCnt.has_key(can):
                    ssCnt[can] = 1
                else:
                    ssCnt[can] += 1
    retList = []
    supportData = {}
    for key in ssCnt:
        if ssCnt[key] >= minSupport:
            retList.insert(0, key)
        supportData[key] = ssCnt[key]
    return retList, supportData


def aprioriGen(Lk, k): #creates Ck
    retList = []
    lenLk = len(Lk)
    for i in range(lenLk):
        for j in range(i+1, lenLk):
            L1 = list(Lk[i])[:k-2]
            L2 = list(Lk[j])[:k-2]
            if L1 == L2: #if first k-2 elements are equal
                retList += map(tuple, list(itertools.permutations(set(Lk[i]) | set(Lk[j]))))
    return retList


def apriori(dataSet, minSupport=2):
    C1 = createC1(dataSet)
    D = map(list, dataSet)
    L1, supportData = scanD(D, C1, minSupport)
    L = [L1]
    k = 2
    while (len(L[k-2]) > 0):
        Ck = aprioriGen(L[k-2], k)
        Lk, supK = scanD(D, Ck, minSupport)#scan DB to get Lk
        supportData.update(supK)
        L.append(Lk)
        k += 1
    return L, supportData


def close_seq(L):
    n = len(L)
    for i in range(n - 1):
        deleted = set()
        for seq1 in L[i]:
            for seq2 in L[i + 1]:
                if is_subseq(seq2, 0, seq1, 0):
                    deleted.add(seq1)
        for e in deleted:
            L[i].remove(e)
    return L


def freq_seq_mining(dataset, minSupport):
    L, supportData = apriori(dataset, minSupport)
    L = close_seq(L)
    L = filter(lambda x: len(x) > 0, L)
    return L, supportData


if __name__ == '__main__':
    items = loadDataSet()
    c1 = createC1(items)
    L, st = apriori(items)
    import pprint
    pprint.pprint(L)
    pprint.pprint(st)
    L = close_seq(L)
    pprint.pprint(L)
    pprint.pprint(st)
    print freq_seq_mining(items, 2)
