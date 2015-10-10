#!/usr/bin/env python
# encoding: utf-8


def raw_merge_locations_by_date(logs):
    if not logs:
        return []
    result = []
    location = None
    start_time = None
    last_start_time = None
    for log in logs:
        cur_start_time = log['start_time']
        cur_location = log['location']
        if location is None:
            location = cur_location
            start_time = cur_start_time
        elif location != cur_location:
            result.append({
                'start_time': start_time,
                'end_time': last_start_time,
                'location': location
            })
            location = cur_location
            start_time = cur_start_time
        last_start_time = cur_start_time

    result.append({
        'start_time': start_time,
        'end_time': last_start_time,
        'location': location
    })
    return result


def check_error_points(result):
    invalid_items = set(map(lambda x: (x['location'], x['start_time']),
                        filter(lambda x: x['start_time'] == x['end_time'],
                               result)))
    return invalid_items


def merge_locations_by_date(logs):
    result = raw_merge_locations_by_date(logs)
    invalid_items = check_error_points(result)
    logs = filter(
        lambda x: (x['location'], x['start_time']) not in invalid_items, logs)
    return raw_merge_locations_by_date(logs)


def merge_locations(logs):
    group_by_day = []
    last_day = None
    one_day_locations = []
    for log in logs:
        cur_day = log['day']
        if last_day is not None and last_day != cur_day:
            group_by_day.append({
                'date': last_day[-2:],
                'locations': merge_locations_by_date(one_day_locations)
            })
            one_day_locations = []
        last_day = cur_day
        one_day_locations.append(log)

    group_by_day.append({
        'date': last_day[-2:],
        'locations': merge_locations_by_date(one_day_locations)
    })

    return group_by_day
