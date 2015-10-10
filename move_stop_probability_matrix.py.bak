#!/usr/bin/env python
# encoding: utf-8

from periodic_probability_matrix import get_time_interval
from collections import Counter


def fill_empty_interval(stop_dict):
    pass


def get_status(moves, stops):
    moves_dict = {move['date']: move['moves'] for move in moves}
    stops_dict = {stop['date']: stop['locations'] for stop in stops}
    dates = ['%02d' % d for d in range(1, 32)]
    results = []
    for date in dates:
        status = [0] * 48
        for stop in stops_dict.get(date, []):
            start_idx, end_idx = get_time_interval(stop['start_time'],
                                                   stop['end_time'])
            for i in range(start_idx, end_idx + 1):
                status[i] = 1
        for move in moves_dict.get(date, []):
            if not move:
                continue
            start_idx, end_idx = get_time_interval(move[0]['start_time'],
                                                   move[-1]['end_time'])
            for i in range(start_idx, end_idx + 1):
                status[i] = 2
        results.append(status)
    return results


def generate_status_matrix(moves, stops):
    mp = {0: 'off', 1: 'stop', 2: 'move'}
    data = get_status(moves, stops)
    matrix = {mp[i]: [0] * 48 for i in range(3)}
    n = len(data)
    for i in range(48):
        counter = Counter([data[j][i] for j in range(n)])
        for k, v in counter.items():
            matrix[mp[k]][i] = float(v) / n
    return matrix
