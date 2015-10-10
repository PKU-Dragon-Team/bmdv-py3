#!/usr/bin/env python
# encoding: utf-8


def minute_to_range(active_time):
    hour = int(active_time[-4:-2])
    minute = int(active_time[-2:])
    result = hour * 2 + (minute >= 30 and 1 or 0)
    return result


def active_matrix(logs):
    result = {}
    for log in logs:
        day = log['day']
        entity = log['entity']
        result.setdefault(day, {})
        result[day].setdefault(entity, [0] * 48)
        result[day][entity][minute_to_range(log['minute'])] += 1
    avg_result = {}
    n = float(len(result))
    for day_data in result.values():
        for app, matrix in day_data.items():
            avg_result.setdefault(app, [0] * 48)
            for i in range(48):
                avg_result[app][i] += matrix[i]
    for app in avg_result:
        for i in range(48):
            avg_result[app][i] /= n
    return avg_result
