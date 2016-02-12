#!/usr/bin/env python
# encoding: utf-8

import json
import pandas as pd
from get_stop import str2date


df = pd.read_csv('stop.csv')
df['data'] = df['data'].map(lambda x: json.loads(x))


def to_dist(row):
    result = {}
    for day in row:
        date = day['date']
        result.setdefault(date, {})
        for location in day['locations']:
            loc = location['location']
            result[date].setdefault(loc, 0)
            st = str2date(location['start_time'])
            dt = str2date(location['end_time'])
            duration = (dt - st).total_seconds() / 60.0
            result[date][loc] += duration
    return result


df['data'] = df.data.map(to_dist)
