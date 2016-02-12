#!/usr/bin/env python
# encoding: utf-8

from get_stop import str2date
import datetime
import math
import pprint


def get_location_in_range(move, start, end):
    result = []
    for location in move:
        cur_start = str2date(location['start_time'])
        cur_end = str2date(location['end_time'])
        if cur_start < end and (cur_start >= start or cur_end <= end):
            result.append(location)
    return result


def entropy(move, delta_t, time_range):
    if len(move) <= 1:
        return 0

    location_time_ranges = {}

    move_start = str2date(move[0]['start_time'])
    move_end = str2date(move[-1]['end_time'])

    if move_start > time_range[0]:
        delta_t -= (move_start - time_range[0]).total_seconds() / 60.0
    if move_end < time_range[1]:
        delta_t -= (time_range[1] - move_end).total_seconds() / 60.0

    if delta_t <= 0:
        return 0

    last_end_time = None
    last_location = None
    last_duration = None
    last_start_time = None
    for location in move:
        cur_location = location['location']
        cur_start_time = str2date(location['start_time'])
        cur_end_time = str2date(location['end_time'])
        cur_duration = location['duration']
        location_time_ranges.setdefault(cur_location, 0)

        if last_end_time:
            location_time_ranges[last_location] += (cur_start_time - last_end_time).total_seconds() / 60.0
            from_ts = max(time_range[0], last_start_time)
            to_ts = min(time_range[1], last_end_time)
            location_time_ranges[last_location] += (to_ts - from_ts).total_seconds() / 60.0

        last_start_time = cur_start_time
        last_end_time = cur_end_time
        last_location = cur_location
        last_duration = cur_duration

    if location:
        from_ts = max(time_range[0], last_start_time)
        to_ts = min(time_range[1], last_end_time)
        location_time_ranges[last_location] += (to_ts - from_ts).total_seconds() / 60.0

    for location in location_time_ranges.keys():
        location_time_ranges[location] /= delta_t

    entropy = sum([-1 * proba * math.log(proba, 2) for proba in location_time_ranges.values() if proba > 0])
    return entropy


def transient_entropy(location, move):
    delta_t = 60

    # set start_time
    start_time = str2date(location['start_time'])
    # get - t/2 and + t/2
    time_range = [start_time - datetime.timedelta(minutes=delta_t / 2),
                  start_time + datetime.timedelta(minutes=delta_t / 2)]
    location_in_ranges = get_location_in_range(move, time_range[0], time_range[1])
    pprint.pprint(location_in_ranges)
    location_time_ranges = {}
    move_start = str2date(move[0]['start_time'])
    move_end = str2date(move[-1]['end_time'])

    if move_start > time_range[0]:
        location_time_ranges['before'] = (move_start - time_range[0]).total_seconds() / 60.0
    if move_end < time_range[1]:
        location_time_ranges['after'] = (time_range[1] - move_end).total_seconds() / 60.0
        # delta_t -= (time_range[1] - move_end).total_seconds() / 60.0

    last_end_time = None
    last_location = None
    last_duration = None
    last_start_time = None
    for location in location_in_ranges:
        cur_location = location['location']
        cur_start_time = str2date(location['start_time'])
        cur_end_time = str2date(location['end_time'])
        cur_duration = location['duration']
        location_time_ranges.setdefault(cur_location, 0)

        if last_end_time:
            location_time_ranges[last_location] += (cur_start_time - last_end_time).total_seconds() / 60.0
            from_ts = max(time_range[0], last_start_time)
            to_ts = min(time_range[1], last_end_time)
            location_time_ranges[last_location] += (to_ts - from_ts).total_seconds() / 60.0

        last_start_time = cur_start_time
        last_end_time = cur_end_time
        last_location = cur_location
        last_duration = cur_duration

    if location:
        from_ts = max(time_range[0], last_start_time)
        to_ts = min(time_range[1], last_end_time)
        location_time_ranges[last_location] += (to_ts - from_ts).total_seconds() / 60.0

    for location in location_time_ranges.keys():
        location_time_ranges[location] /= delta_t

    entropy = sum([-1 * proba * math.log(proba, 2) for proba in location_time_ranges.values() if proba > 0])
    return entropy



if __name__ == '__main__':
    data = [[{'duration': 0.0,
              u'end_time': u'20131201102549',
              u'location': u'116.34636 40.02413',
              u'start_time': u'20131201102549'},
             {'duration': 0.0,
              u'end_time': u'20131201102549',
              u'location': u'116.38127 39.97306',
              u'start_time': u'20131201102549'},
             {'duration': 0.0,
              u'end_time': u'20131201102550',
              u'location': u'116.34636 40.02413',
              u'start_time': u'20131201102550'},
             {'duration': 0.0,
              u'end_time': u'20131201102552',
              u'location': u'116.38127 39.97306',
              u'start_time': u'20131201102552'}],
            [{'duration': 0.0,
              u'end_time': u'20131201114531',
              u'location': u'116.35673 40.01079',
              u'start_time': u'20131201114531'},
             {'duration': 0.0,
              u'end_time': u'20131201114705',
              u'location': u'116.34636 40.02413',
              u'start_time': u'20131201114705'}],
            [{'duration': 10.616666666666667,
              u'end_time': u'20131201131856',
              u'location': u'116.38986 39.96212',
              u'start_time': u'20131201130819'},
             {'duration': 0.0,
              u'end_time': u'20131201131857',
              u'location': u'116.37256 39.95921',
              u'start_time': u'20131201131857'},
             {'duration': 0.0,
              u'end_time': u'20131201131857',
              u'location': u'116.38986 39.96212',
              u'start_time': u'20131201131857'},
             {'duration': 0.0,
              u'end_time': u'20131201131904',
              u'location': u'116.37256 39.95921',
              u'start_time': u'20131201131904'},
             {'duration': 0.0,
              u'end_time': u'20131201132129',
              u'location': u'116.37636 39.97060',
              u'start_time': u'20131201132129'},
             {'duration': 3.2666666666666666,
              u'end_time': u'20131201132658',
              u'location': u'116.36282 39.96718',
              u'start_time': u'20131201132342'}],
            [{'duration': 14.816666666666666,
              u'end_time': u'20131201145000',
              u'location': u'116.31258 39.97103',
              u'start_time': u'20131201143511'},
             {'duration': 0.0,
              u'end_time': u'20131201145007',
              u'location': u'116.31567 39.96686',
              u'start_time': u'20131201145007'},
             {'duration': 0.0,
              u'end_time': u'20131201145008',
              u'location': u'116.31258 39.97103',
              u'start_time': u'20131201145008'}]]

    for move in data:
        for location in move:
            print transient_entropy(location, move)
