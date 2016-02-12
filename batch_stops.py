#!/usr/bin/env python
# encoding: utf-8

from db import MySQL as DB
from batch_common import fetch_user_location_logs
from batch_common import dbconfig
from batch_common import fetch_users
from merge_locations import merge_locations
import sys
import json
from csv import DictWriter


def run():
    output = open(sys.argv[1], 'w')
    writer = DictWriter(output, fieldnames=['uid', 'data'])
    writer.writeheader()
    db = DB(dbconfig)

    for uid in fetch_users(db):
        data = fetch_user_location_logs(uid, db)
        locations = merge_locations(data)
        writer.writerow({
            'uid': uid,
            'data': json.dumps(locations)
        })
    output.close()


if __name__ == '__main__':
    run()
