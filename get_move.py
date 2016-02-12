#!/usr/bin/env python
# encoding: utf-8

import datetime
from get_stop import str2date


def get_moves(data):
    result = []
    for data_by_day in data:
        new_day = {}
        new_day['date'] = data_by_day['date']
        new_day['moves'] = get_moves_by_day(data_by_day['locations'])
        result.append(new_day)
    return result


def get_moves_by_day(data):
    moves = []
    cur_move = []
    last_endtime = None
    H1 = 30
    H2 = 15

    for record in data:
        if record['duration'] > H1:
            if len(cur_move) > 1:
                moves.append(cur_move)
            cur_move = []
            last_endtime = None
        else:
            start_time = str2date(record['start_time'])
            end_time = str2date(record['end_time'])
            if last_endtime is None:
                cur_move.append(record)
                last_endtime = end_time
            else:
                delta = (start_time - last_endtime).total_seconds() / 60
                if delta < H2:
                    cur_move.append(record)
                    last_endtime = end_time
                else:
                    if len(cur_move) > 1:
                        moves.append(cur_move)
                    cur_move = []
                    last_endtime = None
    return moves


if __name__ == '__main__':
    import json
    from get_stop import get_delta_by_day
    import pprint
    data = json.load(open('31430787_01.json'))
    get_delta_by_day(data)
    pprint.pprint(get_moves(data))
