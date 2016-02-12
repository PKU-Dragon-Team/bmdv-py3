#!/usr/bin/env python
# encoding: utf-8

import datetime


def str2date(string):
    return datetime.datetime.strptime(string, '%Y%m%d%H%M%S')


def date2str(date):
    return date.strftime('%Y%m%d%H%M%S')


def format_in_one_day(date):
    return date.strftime('%H:%M')


def get_delta(data, format=False):
    for day in data:
        get_delta_by_day(day['locations'], format)


def get_delta_by_day(day, format=False):
    for location in day:
        start_time = str2date(location['start_time'])
        end_time = str2date(location['end_time'])
        delta = end_time - start_time
        location['duration'] = delta.total_seconds() / 60
        if format:
            location['start_time'] = format_in_one_day(start_time)
            location['end_time'] = format_in_one_day(end_time)


def get_stop(data, th=30):
    result = []
    for day in data:
        new_day = {}
        new_day['date'] = day['date']
        new_day['locations'] = get_stop_by_day(day['locations'], th)
        result.append(new_day)
    return result


def get_stop_by_day(day, th=30):
    return [location for location in day if location['duration'] > th]
