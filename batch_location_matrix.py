#!/usr/bin/env python
# encoding: utf-8

from db import MySQL as DB
from batch_common import dbconfig
from batch_common import fetch_users
from batch_common import fetch_user_location_logs
from merge_locations import merge_locations
from periodic_probability_matrix import generate_matrix
import json
from csv import DictWriter
import sys

reload(sys)
exec("sys.setdefaultencoding('utf-8')");


def run():
    output = open(sys.argv[1], 'w')
    writer = DictWriter(output, fieldnames=['uid', 'data'])
    writer.writeheader()
    db = DB(dbconfig)

    for uid in fetch_users(db):
        logs = fetch_user_location_logs(uid, db)
        locations = merge_locations(logs)
        matrix = generate_matrix(locations)
        writer.writerow({
            'uid': uid,
            'data': json.dumps(matrix)
        })
    output.close()


if __name__ == '__main__':
    run()
