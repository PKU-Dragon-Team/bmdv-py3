#!/usr/bin/env python
# encoding: utf-8


import pandas as pd
import numpy as np
import json
from sklearn.feature_extraction import DictVectorizer
from scipy.spatial.distance import correlation
import pylab as plt
import kcluster

k = 8


def preprocess(filepath):
    df = pd.read_csv(filepath)
    df.set_index('uid', inplace=True)
    df['data'] = df['data'].map(lambda x: json.loads(x))

    apps = set(['QQ', u'微信', u'手机腾讯网'])
    # apps = set([])

    def to_avg(row):
        return {k: np.mean(v) for k, v in row.items() if k not in apps}

    return df['data'].map(to_avg)


def cluster(vals, k):
    dv = DictVectorizer(sparse=False)
    X = dv.fit_transform(vals)
    K, C = kcluster.kcluster(X, correlation, k)
    return K, C, dv


def normalize(row):
    if not len(row):
        return {}
    minactive = min(row.values())
    return {k: v - minactive for k, v in row.items()}

app_mean = preprocess('app_matrix.csv')
normalized_app_mean = app_mean.map(normalize)
K, C, dv = cluster(normalized_app_mean.values, k)

fig, axes = plt.subplots(k, 1)

centers = dv.inverse_transform(C)
N = 20
for i in range(k):
    d = dict(sorted(centers[i].items(), key=lambda x: x[1], reverse=True)[:N])
    serie = pd.Series(d.values(), index=d.keys())
    serie.plot(kind='bar', ax=axes[i])
