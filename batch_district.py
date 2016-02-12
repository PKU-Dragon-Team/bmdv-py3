#!/usr/bin/env python
# encoding: utf-8

from db import MySQL as DB
from batch_common import dbconfig
from batch_common import fetch_users
from batch_common import fetch_semantic_logs
from merge_locations import merge_locations, raw_merge_locations_by_date, check_error_points
from periodic_probability_matrix import generate_matrix
from get_stop import get_stop, get_delta
import json
from csv import DictWriter
import sys

reload(sys)
exec("sys.setdefaultencoding('utf-8')");


def get_district_logs(uid, db):
    rows = fetch_semantic_logs(uid, db)
    for row in rows:
        row['location'] = row['district']
    return rows


def area_by_uid_stop(uid, db, area_func):
    results = area_func(uid, db)
    invalids = check_error_points(raw_merge_locations_by_date(results))
    results = filter(lambda x: (x['location'], x['start_time']) not in invalids, results)
    locations = merge_locations(results)
    get_delta(locations)
    locations = get_stop(locations, 30)
    return locations


def run():
    output = open(sys.argv[1], 'w')
    writer = DictWriter(output, fieldnames=['uid', 'data'])
    writer.writeheader()
    db = DB(dbconfig)

    for uid in fetch_users(db):
        locations = area_by_uid_stop(uid, db, get_district_logs)
        writer.writerow({
            'uid': uid,
            'data': json.dumps(locations)
        })
    output.close()


if __name__ == '__main__':
    run()
