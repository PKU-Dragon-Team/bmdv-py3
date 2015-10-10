#!/usr/bin/env python
# encoding: utf-8

from db import MySQL as DB
from app import get_speed_by_day
from batch_common import fetch_user_location_logs
from batch_common import dbconfig
from batch_common import fetch_users
import sys


def run():
    output = open(sys.argv[1], 'w')
    db = DB(dbconfig)

    for uid in fetch_users(db):
        data = fetch_user_location_logs(uid, db)
        for day in range(1, 32):
            day = '201312%02d' % day
            rows_by_day = filter(lambda x: x['day'] == day, data)
            if not rows_by_day:
                continue
            rows_by_day = map(lambda x: [x['start_time'], x['location']],
                              rows_by_day)
            speeds = map(lambda x: x['speed'],
                         get_speed_by_day(rows_by_day, day))
            output.write(','.join(map(str, [uid, day] + speeds)) + '\n')
    output.close()

if __name__ == '__main__':
    run()
