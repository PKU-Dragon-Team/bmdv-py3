#!/usr/bin/env python
# encoding: utf-8

from db import MySQL as DB
from batch_common import dbconfig
from batch_common import fetch_users
from batch_common import fetch_semantic_logs
from batch_district import area_by_uid_stop
from merge_locations import merge_locations
from periodic_probability_matrix import generate_matrix
import json
from csv import DictWriter
import sys

reload(sys)
exec("sys.setdefaultencoding('utf-8')");


def get_business_logs(uid, db):
    rows = fetch_semantic_logs(uid, db)
    for row in rows:
        row['location'] = row['business'] and row['business'] or row['district']
    return rows


def run():
    output = open(sys.argv[1], 'w')
    writer = DictWriter(output, fieldnames=['uid', 'data'])
    writer.writeheader()
    db = DB(dbconfig)

    for uid in fetch_users(db):
        locations = area_by_uid_stop(uid, db, get_business_logs)
        writer.writerow({
            'uid': uid,
            'data': json.dumps(locations)
        })
    output.close()


if __name__ == '__main__':
    run()
