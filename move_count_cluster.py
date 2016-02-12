#!/usr/bin/env python
# encoding: utf-8

import pandas as pd
from scipy.spatial.distance import correlation
from sklearn.preprocessing import scale
import kcluster

df = pd.read_csv('speed_move_count.csv', index_col='uid')
X = scale(df.values)
K, C = kcluster.kcluster(X, correlation, 3)
