#!/usr/bin/env python
# encoding: utf-8

from csv import DictWriter
import json
from db import MySQL as DB
from batch_common import dbconfig
from batch_common import fetch_users
from app_site_matrix import active_matrix
import sys

reload(sys)
exec("sys.setdefaultencoding('utf-8')");


def fetch_uid_app_data(uid, db):
    cols = ['day', 'minute', 'entity']
    prepare_sql = """select day, concat('201312', minute) as start_time,
                        app_name
                        from app_domain_logs
                        where uid = %s and app_name != '其他' and
                              site_channel_name not like %s
                              and dirty is NULL
                        order by day, minute"""
    data = db.fetchall(prepare_sql, (uid, '被动%'))
    return [dict(zip(cols, row)) for row in data]


def run(outputfile):
    cols = ['uid', 'data']
    f = open(outputfile, 'w')
    writer = DictWriter(f, cols)
    writer.writeheader()
    db = DB(dbconfig)

    for uid in fetch_users(db):
        logs = fetch_uid_app_data(uid, db)
        writer.writerow({
            'uid': uid,
            'data': json.dumps(active_matrix(logs))
        })

if __name__ == '__main__':
    run(sys.argv[1])
