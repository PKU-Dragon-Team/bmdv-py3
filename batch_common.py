#!/usr/bin/env python
# encoding: utf-8

from config import HOST, USER, PASSWD, DATABASE

dbconfig = {
    'host': HOST,
    'user': USER,
    'passwd': PASSWD,
    'db': DATABASE,
    'charset': 'utf8'
}


def fetch_users(db, pagecnt=10000):
    offset = 0
    while True:
        users = db.fetchall("""
                            select uid from users where high >= '7'
                            limit %s offset %s""", (pagecnt, offset * pagecnt))
        if not users:
            break

        for uid in map(lambda x: x[0], users):
            yield uid

        offset += 1


def fetch_user_location_logs(uid, db):
    cols = ['start_time', 'location', 'day']
    prepare_sql = """select start_time, location, log_date
                        from location_logs_with_date
                        where uid = %s order by start_time"""
    data = db.fetchall(prepare_sql, (uid,))
    return [dict(zip(cols, row)) for row in data]


def fetch_semantic_logs(uid, db):
    cols = ['day', 'start_time', 'location', 'district', 'business']
    prepare_sql = """select a.log_date as day, a.start_time, a.location,
                        b.district, b.business
                        from location_logs_with_date a
                        left join location_desc b
                        on a.location = b.location
                        where a.uid = %s
                        order by a.start_time"""
    data = db.fetchall(prepare_sql, (uid,))
    return [dict(zip(cols, row)) for row in data]
