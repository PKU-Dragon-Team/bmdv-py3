import random
import numpy as np
from math import sqrt


def sts(v1, v2):
    n = len(v1)
    d1 = [v1[i] - v1[i - 1] for i in xrange(1, n)]
    d2 = [v2[i] - v2[i - 1] for i in xrange(1, n)]
    return np.sqrt(sum([(d1[i] - d2[i]) ** 2 for i in xrange(n - 1)]))


def pearson(v1, v2):
    # Simple sums
    sum1 = sum(v1)
    sum2 = sum(v2)

    # Sums of the squares
    sum1Sq = sum([pow(v, 2) for v in v1])
    sum2Sq = sum([pow(v, 2) for v in v2])

    # Sum of the products
    pSum = sum([v1[i]*v2[i] for i in range(len(v1))])

    # Calculate r (Pearson score)
    num = pSum-(sum1*sum2/len(v1))
    den = np.sqrt((sum1Sq-pow(sum1, 2)/len(v1))*(sum2Sq-pow(sum2, 2)/len(v1)))
    if den == 0:
        return 0

    return 1.0-num/den


def kcluster(rows, distance, k):
    # Determine the minimum and maximum values for each point
    ranges = [(min([row[i] for row in rows]),  max([row[i] for row in rows]))
              for i in range(len(rows[0]))]

    # Create k randomly placed centroids
    clusters = np.array([[random.random()*(ranges[i][1]-ranges[i][0])+ranges[i][0]
                 for i in range(len(rows[0]))] for j in range(k)])

    lastmatches = None
    for t in range(100):
        print 'Iteration %d' % t
        bestmatches = [[] for i in range(k)]

        # Find which centroid is the closest for each row
        for j in range(len(rows)):
            row = rows[j]
            bestmatch = 0
            for i in range(k):
                d = distance(clusters[i], row)
                if d < distance(clusters[bestmatch], row):
                    bestmatch = i
            bestmatches[bestmatch].append(j)

        # If the results are the same as last time,  this is complete
        if bestmatches == lastmatches:
            break
        lastmatches = bestmatches

        # Move the centroids to the average of their members
        for i in range(k):
            # avgs = [0.0]*len(rows[0])
            if len(bestmatches[i]) > 0:
                clusters[i] = np.mean(rows[bestmatches[i]], axis=0)
                # for rowid in bestmatches[i]:
                #     for m in range(len(rows[rowid])):
                #         avgs[m] += rows[rowid][m]
                # for j in range(len(avgs)):
                #     avgs[j] /= len(bestmatches[i])
                # clusters[i] = avgs

        def bestmatch2label(K, n):
            labels = np.empty(n, dtype=int)
            for i in range(len(K)):
                labels[K[i]] = i
            return labels

    return bestmatch2label(bestmatches, len(rows)), np.array(clusters)


def silhouette_coef(idx, X, labels, dist):
    labelx = labels[idx]
    incluster = X[labels == labelx, :]
    inlen = len(incluster)
    indist = np.empty(inlen)
    for i in np.arange(inlen):
        indist[i] = dist(X[idx], incluster[i])
    indist_mean = np.mean(indist)

    outdists = {}
    labels_unq = np.unique(labels)
    outlabels = labels_unq[labels_unq != labelx]
    for outlabel in outlabels:
        outcluster = X[labels == outlabel, :]
        outdist = np.empty(len(outcluster))
        for i in np.arange(len(outcluster)):
            outdist[i] = dist(X[idx], outcluster[i])
        outdists[outlabel] = np.mean(outdist)

    return (min(outdists.values()) - indist_mean) / max(min(outdists.values()), indist_mean)


def silhouette_score(X, labels, dist):
    return np.mean([silhouette_coef(i, X, labels, dist) for i in xrange(len(X))])


def pick_k(X, rng, dist):
    n = len(X)
    for i in rng:
        K, C = kcluster(X, dist, i)
        labels = np.empty(n, dtype=int)
        for j in range(i):
            labels[K[j]] = j
        print i, silhouette_score(X, labels, dist)
