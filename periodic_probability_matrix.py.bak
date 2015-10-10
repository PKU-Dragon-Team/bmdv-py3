#!/usr/bin/env python
# encoding: utf-8


def get_locations(data):
    locations = []
    for day in data:
        for record in day['locations']:
            if record['location'] not in locations:
                locations.append(record['location'])
    return locations


def generate_matrix(data):
    n = float(len(data))
    locations = get_locations(data)
    matrix = {location: [0] * 48 for location in locations}
    for day in data:
        for record in day['locations']:
            int_start, int_end = get_time_interval(record['start_time'],
                                                   record['end_time'])
            for i in xrange(int_start, int_end + 1):
                matrix[record['location']][i] += 1 / n
    return matrix


def get_time_interval(start_time, end_time):
    start_hour = int(start_time[8:10])
    start_minute = int(start_time[10:12])
    end_hour = int(end_time[8:10])
    end_minute = int(end_time[10:12])

    interval_start = start_hour * 2
    if start_minute >= 15:
        interval_start += 1
    if start_minute >= 45:
        interval_start += 1
    interval_end = end_hour * 2
    if end_minute < 15:
        interval_end -= 1
    if end_minute >= 45:
        interval_end += 1

    return interval_start, interval_end


if __name__ == '__main__':
    import json
    data = json.load(open('53008957.json'))
    result = generate_matrix(data)
    def print_result(result):
        for location, row in result.items():
            print location
            print ' '.join(map(lambda x: "%.3f" % x, row))
    print json.dumps(result)
