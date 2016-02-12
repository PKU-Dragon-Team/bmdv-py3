#!/usr/bin/env python
# encoding: utf-8


import pandas as pd
import numpy as np
import json
from sklearn.feature_extraction import DictVectorizer
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.preprocessing import scale
from scipy.spatial.distance import correlation
from scipy.spatial.distance import cosine
from sklearn.metrics import silhouette_score
import sys
import pylab as plt
import kcluster

k = 3

def preprocess(filepath):
    df = pd.read_csv(filepath)
    df.set_index('uid', inplace=True)
    df['data'] = df['data'].map(lambda x: json.loads(x))

    # apps = set(['QQ', u'微信', u'手机腾讯网'])
    # apps = set(['社交沟通'])
    apps = set([])

    def to_avg(row):
        return {k: np.mean(v) for k, v in row.items() if k not in apps}

    return df['data'].map(to_avg)


def cluster(X, k):
    K, C = kcluster.kcluster(X, correlation, k)
    print 'silhouette_score: %.5f' % (silhouette_score(X, K, metric=correlation))
    return K, C


app_mean = preprocess('app_type_matrix.csv')
ch = np.random.choice(len(app_mean), 2000)
app_mean_sample = app_mean.irow(ch)
dv = DictVectorizer(sparse=False)
X = dv.fit_transform(app_mean_sample.values)

df = pd.DataFrame(X, columns=dv.get_feature_names(), index=app_mean_sample.index)

valid_columns = [u'旅游', u'游戏', u'电商购物', u'社交沟通', u'社区论坛',
                 u'网页浏览', u'视频', u'邮箱', u'阅读', u'音乐']

df = df[valid_columns]


def run_cluster(df, k, topN):
    K, C = cluster(df, k)
    fig, axes = plt.subplots(k, 1)
    centers = dv.inverse_transform(C)
    for i in range(k):
        d = dict(sorted(centers[i].items(), key=lambda x: x[1], reverse=True)[:topN])
        serie = pd.Series(d.values(), index=d.keys())
        serie.plot(kind='bar', ax=axes[i])
    return K, C
