#!/usr/bin/env python
# encoding: utf-8

from flask import Flask, make_response
from json import dumps
from flask.ext.cors import CORS
import MySQLdb
import MySQLdb.converters
from config import HOST, USER, PASSWD, DATABASE
from get_stop import get_stop, get_delta, get_stop_by_day, get_delta_by_day
from get_stop import str2date
from get_stop import date2str
from periodic_probability_matrix import generate_matrix
from get_most_proba_locations import get_most_proba_locations, pretty_print_most_proba_locations
from apriori import freq_seq_mining
from get_move import get_moves_by_day, get_moves
from get_transient_entropy import transient_entropy, entropy
import pandas as pd
import datetime
from merge_locations import merge_locations, merge_locations_by_date, raw_merge_locations_by_date, check_error_points
from move_stop_probability_matrix import generate_status_matrix
from move_stop_probability_matrix import get_status
from app_site_matrix import active_matrix
from tag_config import clean_tags

app = Flask(__name__)
cors = CORS(app)

conv = MySQLdb.converters.conversions.copy()
# convert decimals to int
conv[246] = int
db = MySQLdb.connect(HOST, USER, PASSWD, DATABASE, conv=conv)

holidays = ['01', '07', '08', '14', '15', '21', '22', '28', '29']


@app.route("/usercount")
def usercount():
    db.ping(True)
    cursor = db.cursor()
    prepare_sql = """
    select count(1) from users where high >= '8'"""
    cursor.execute(prepare_sql)
    row = cursor.fetchone()
    return make_response(dumps(row[0]))


@app.route('/users/<uid>')
def user(uid):
    cols = ['uid', 'gender', 'age', 'brand_chn', 'call_fee', 'gprs_fee', 'dept_name']
    db.ping(True)
    cursor = db.cursor()
    prepare_sql = """
    select uid, gender, age, brand_chn, call_fee, gprs_fee, dept_name
        from users where uid = %s"""
    cursor.execute(prepare_sql, (uid,))
    row = cursor.fetchone()
    result = dict(zip(cols, row))
    return make_response(dumps(result))


@app.route("/users/<int:offset>/<int:limit>")
def users(offset, limit):
    cols = ['uid', 'gender', 'age', 'brand_chn', 'call_fee', 'gprs_fee', 'dept_name']
    db.ping(True)
    cursor = db.cursor()
    prepare_sql = """
    select uid, gender, age, brand_chn, call_fee, gprs_fee, dept_name
        from users where high >= '7' limit %s offset %s"""
    cursor.execute(prepare_sql, (limit, offset))
    rows = cursor.fetchall()
    results = [dict(zip(cols, row)) for row in rows]
    return make_response(dumps(results))


@app.route("/gprs_count_by_hour/<uid>")
def gprs_count_by_hour(uid):
    cols = ['uid', 'day', 'hour', 'count']
    db.ping(True)
    cursor = db.cursor()
    prepare_sql = """select uid, day, substring(minute, 3, 2) as hour, count(distinct minute) as count
                        from app_domain_logs where uid = %s group by day, hour"""
    cursor.execute(prepare_sql, (uid,))
    rows = cursor.fetchall()
    results = [dict(zip(cols, row)) for row in rows]
    return make_response(dumps(results))


@app.route("/call_count_by_hour/<uid>")
def call_count_by_hour(uid):
    cols = ['uid', 'day', 'hour', 'count']
    db.ping(True)
    cursor = db.cursor()
    prepare_sql = """select uid,
                        day(start_time) as day,
                        hour(start_time) as hour,
                        count(1) as count
                        from calls where uid = %s group by day, hour"""
    cursor.execute(prepare_sql, (uid,))
    rows = cursor.fetchall()
    results = [dict(zip(cols, row)) for row in rows]
    return make_response(dumps(results))


@app.route("/gprs_count_by_day/<uid>")
def gprs_count_by_day(uid):
    cols = ['uid', 'day', 'count']
    db.ping(True)
    cursor = db.cursor()
    prepare_sql = """select uid, day, sum(count) as count from gprs_hour_counts
                        where uid = %s group by day"""
    cursor.execute(prepare_sql, (uid,))
    rows = cursor.fetchall()
    results = [dict(zip(cols, row)) for row in rows]
    return make_response(dumps(results))


@app.route("/call_count_by_day/<uid>")
def call_count_by_day(uid):
    cols = ['uid', 'day', 'count']
    db.ping(True)
    cursor = db.cursor()
    prepare_sql = """select uid, day(start_time) as day, count(1) as count from calls
                        where uid = %s group by day"""
    cursor.execute(prepare_sql, (uid,))
    rows = cursor.fetchall()
    results = [dict(zip(cols, row)) for row in rows]
    return make_response(dumps(results))


@app.route("/location/daycount/<uid>")
def location_daycount_by_uid(uid):
    db.ping(True)
    cursor = db.cursor()
    prepare_sql = """select distinct(log_date) as day
                        from location_logs_with_date
                        where uid = %s"""
    cursor.execute(prepare_sql, (uid,))
    rows = cursor.fetchall()
    results = [row[0] for row in rows]
    return make_response(dumps(results))


def fetch_uid_location_data(uid):
    cols = ['day', 'start_time', 'location']
    db.ping(True)
    cursor = db.cursor()
    prepare_sql = """select log_date as day, start_time, location
                        from location_logs_with_date
                        where uid = %s order by day, start_time"""
    cursor.execute(prepare_sql, (uid,))
    rows = cursor.fetchall()
    return [dict(zip(cols, row)) for row in rows]


def fetch_uid_semantic_data(uid):
    cols = ['day', 'start_time', 'location', 'district', 'business']
    db.ping(True)
    cursor = db.cursor()
    prepare_sql = """select a.log_date as day, a.start_time, a.location,
                        b.district, b.business
                        from location_logs_with_date a
                        left join semantic4 b
                        on a.location = b.location
                        where a.uid = %s
                        order by a.start_time"""
    cursor.execute(prepare_sql, (uid,))
    rows = cursor.fetchall()
    return [dict(zip(cols, row)) for row in rows]


def fetch_uid_business_data(uid):
    rows = fetch_uid_semantic_data(uid)
    for row in rows:
        row['location'] = row['business'] and row['business'] or row['district']
    return rows


def fetch_uid_district_data(uid):
    rows = fetch_uid_semantic_data(uid)
    for row in rows:
        row['location'] = row['district']
    return rows


@app.route("/location_by_uid/<uid>")
def location_by_uid(uid):
    results = fetch_uid_location_data(uid)
    return make_response(dumps(merge_locations(results)))


def _location_by_uid_stop(uid):
    results = fetch_uid_location_data(uid)
    locations = merge_locations(results)
    get_delta(locations)
    locations = get_stop(locations, 30)
    return locations


def area_by_uid_stop(uid, area_func=fetch_uid_business_data):
    results = area_func(uid)
    invalids = check_error_points(raw_merge_locations_by_date(results))
    results = filter(lambda x: (x['location'], x['start_time']) not in invalids, results)
    locations = merge_locations(results)
    get_delta(locations)
    locations = get_stop(locations, 30)
    return locations


def _location_by_uid_stop_holiday(uid):
    locations = _location_by_uid_stop(uid)
    return [data for data in locations if data['date'] in holidays]


def _location_by_uid_stop_workday(uid):
    locations = _location_by_uid_stop(uid)
    return [data for data in locations if data['date'] not in holidays]


@app.route("/location_by_uid_stop/<uid>")
def location_by_uid_stop(uid):
    return make_response(dumps(_location_by_uid_stop(uid)))


@app.route("/raw_location_by_uid_day/<uid>/<day>")
def raw_location_by_uid_day(uid, day):
    day = '201312' + day
    cols = ['start_time', 'location']
    db.ping(True)
    cursor = db.cursor()
    prepare_sql = """select start_time, location
                        from location_logs_with_date
                        where uid = %s and log_date = %s order by start_time"""
    cursor.execute(prepare_sql, (uid, day))
    rows = cursor.fetchall()
    results = [dict(zip(cols, row)) for row in rows]
    invalids = check_error_points(raw_merge_locations_by_date(results))
    results = filter(
        lambda x: (x['location'], x['start_time']) not in invalids, results)
    return make_response(dumps(results))


# @app.route("/entropy_by_uid_day/<uid>/<day>")
# def entropy_by_uid_day(uid, day):
#     day = '201312' + day
#     cols = ['start_time', 'location']
#     db.ping(True)
#     cursor = db.cursor()
#     prepare_sql = """select start_time, location
#                         from location_logs_with_date
#                         where uid = %s and log_date = %s order by start_time"""
#     cursor.execute(prepare_sql, (uid, day))
#     rows = cursor.fetchall()
#     results = merge_locations_by_date([dict(zip(cols, row)) for row in rows])
#     get_delta_by_day(results)
#     print results
#     result = []
#     delta_t = 60
#     for location in results:
#         tm = str2date(location['start_time'])
#         start_time = tm - datetime.timedelta(minutes=delta_t / 2)
#         end_time = tm + datetime.timedelta(minutes=delta_t / 2)
#         result.append({
#             'entropy': entropy(move, delta_t, [start_time, end_time]),
#             'time': location['start_time']
#         })
# return make_response(dumps(result))


def get_speed_by_day(all_rows, day):
    timestamps = pd.date_range(start=day + '001500',
                               end=day + '235959',
                               freq='30Min')
    cols = ['start_time', 'location']
    speeds = []

    if len(all_rows) == 0:
        return speeds

    delta_t = 60
    for i in range(len(timestamps)):
        start_time = timestamps[i].to_datetime() - datetime.timedelta(minutes=delta_t / 2)
        end_time = timestamps[i].to_datetime() + datetime.timedelta(minutes=delta_t / 2)
        rows = filter(lambda x: date2str(start_time) <= x[0] <= date2str(end_time),
                      all_rows)
        if len(rows) == 0:
            speeds.append({
                'time': date2str(timestamps[i]),
                'speed': 0
            })
            continue
        rows = merge_locations_by_date([dict(zip(cols, row)) for row in rows])
        get_delta_by_day(rows)
        speed = entropy(rows, delta_t, [start_time, end_time])
        speeds.append({
            'time': date2str(timestamps[i]),
            'speed': speed
        })
    return speeds


def get_speed_by_day_at_change_point(all_rows, day):
    cols = ['start_time', 'location']
    speeds = []
    results = merge_locations_by_date([dict(zip(cols, row)) for row in all_rows])

    points = set()
    for location in results:
        points.add(location['start_time'])
        points.add(location['end_time'])
    points = map(lambda x: str2date(x), sorted(points))

    if len(all_rows) == 0:
        return speeds

    delta_t = 60
    for i in range(len(points)):
        start_time = points[i] - datetime.timedelta(minutes=delta_t / 2)
        end_time = points[i] + datetime.timedelta(minutes=delta_t / 2)
        rows = filter(lambda x: date2str(start_time) <= x[0] <= date2str(end_time),
                      all_rows)
        if len(rows) == 0:
            speeds.append({
                'time': date2str(points[i]),
                'speed': 0
            })
            continue
        rows = merge_locations_by_date([dict(zip(cols, row)) for row in rows])
        get_delta_by_day(rows)
        speed = entropy(rows, delta_t, [start_time, end_time])
        speeds.append({
            'time': date2str(points[i]),
            'speed': speed
        })
    return speeds


@app.route("/speed_by_uid_day/<uid>/<day>")
def speed_by_uid_day(uid, day):
    day = '201312' + day
    speeds = []

    db.ping(True)
    cursor = db.cursor()
    prepare_sql = """select start_time, location
                        from location_logs_with_date
                        where uid = %s and log_date = %s order by start_time"""
    cursor.execute(prepare_sql, (uid, day))
    all_rows = cursor.fetchall()
    speeds = get_speed_by_day(all_rows, day)
    return make_response(dumps(speeds))


@app.route("/speed_by_uid_day_at_change_point/<uid>/<day>")
def speed_by_uid_day_at_change_point(uid, day):
    day = '201312' + day
    speeds = []

    db.ping(True)
    cursor = db.cursor()
    prepare_sql = """select start_time, location
                        from location_logs_with_date
                        where uid = %s and log_date = %s order by start_time"""
    cursor.execute(prepare_sql, (uid, day))
    all_rows = cursor.fetchall()
    speeds = get_speed_by_day_at_change_point(all_rows, day)
    return make_response(dumps(speeds))


@app.route("/speed_by_uid/<uid>")
def speed_by_uid(uid):
    db.ping(True)
    cursor = db.cursor()
    prepare_sql = """select start_time, location, log_date
                        from location_logs_with_date
                        where uid = %s order by start_time"""
    cursor.execute(prepare_sql, (uid,))
    all_rows = cursor.fetchall()
    result = []

    for day in range(1, 32):
        day = '201312%02d' % day
        rows_by_day = filter(lambda x: x[2] == day, all_rows)
        rows_by_day = map(lambda x: x[:2], rows_by_day)
        speeds = get_speed_by_day(rows_by_day, day)
        result.append(speeds)

    return make_response(dumps(result))


@app.route("/location_by_uid_day/<uid>/<day>")
def location_by_uid_day(uid, day):
    day = '201312' + day
    cols = ['start_time', 'location']
    db.ping(True)
    cursor = db.cursor()
    prepare_sql = """select start_time, location
                        from location_logs_with_date
                        where uid = %s and log_date = %s order by start_time"""
    cursor.execute(prepare_sql, (uid, day))
    rows = cursor.fetchall()
    results = [dict(zip(cols, row)) for row in rows]
    return make_response(dumps(merge_locations_by_date(results)))


@app.route("/location_by_uid_day_stop/<uid>/<day>")
def location_by_uid_day_stop(uid, day):
    day = '201312' + day
    cols = ['start_time', 'location']
    db.ping(True)
    cursor = db.cursor()
    prepare_sql = """select start_time, location
                        from location_logs_with_date
                        where uid = %s and log_date = %s order by start_time"""
    cursor.execute(prepare_sql, (uid, day))
    rows = cursor.fetchall()
    results = merge_locations_by_date([dict(zip(cols, row)) for row in rows])
    get_delta_by_day(results)
    results = get_stop_by_day(results)
    return make_response(dumps(results))


@app.route("/app_log_by_uid_day/<uid>/<day>")
def app_log_by_uid_day(uid, day):
    cols = ['minute', 'busi_name', 'app_name',
            'site_name', 'site_channel_name', 'domain', 'count']
    db.ping(True)
    cursor = db.cursor()
    prepare_sql = """select minute, busi_name, app_name, site_name, site_channel_name, domain, count
                            from app_domain_logs
                            where uid = %s and day = %s order by minute"""
    cursor.execute(prepare_sql, (uid, day))
    rows = cursor.fetchall()
    results = [dict(zip(cols, row)) for row in rows]
    return make_response(dumps(results))


@app.route("/semantic_proba_matrix/<uid>")
def semantic_proba_matrix(uid):
    locations = area_by_uid_stop(uid, area_func=fetch_uid_business_data)
    return make_response(dumps(generate_matrix(locations)))


@app.route("/district_proba_matrix/<uid>")
def district_proba_matrix(uid):
    locations = area_by_uid_stop(uid, area_func=fetch_uid_district_data)
    return make_response(dumps(generate_matrix(locations)))


@app.route("/proba_matrix/<uid>")
def proba_matrix(uid):
    locations = _location_by_uid_stop(uid)
    return make_response(dumps(generate_matrix(locations)))


@app.route("/tag_proba_matrix/<uid>")
def tag_proba_matrix(uid):
    locations = _location_by_uid_stop(uid)
    matrix = generate_matrix(locations)
    semantic_data = fetch_semantic_data(matrix.keys())
    semantic_dict = {}
    for row in semantic_data:
        semantic_dict[row['location']] = clean_tags(row['tags'], 5)
    tag_matrix = {}
    for location, proba in matrix.items():
        tag_dict = semantic_dict[location]
        tag_weight = sum(v for v in tag_dict.values())
        if tag_weight == 0:
            continue
        for tag, cnt in tag_dict.items():
            tag_matrix.setdefault(tag, [0] * 48)
            for i in range(48):
                tag_matrix[tag][i] += (proba[i] * cnt + 0.001) / (tag_weight + 0.001)

    return make_response(dumps(tag_matrix))


@app.route("/proba_matrix_holiday/<uid>")
def proba_matrix_holiday(uid):
    locations = _location_by_uid_stop_holiday(uid)
    return make_response(dumps(generate_matrix(locations)))


@app.route("/proba_matrix_workday/<uid>")
def proba_matrix_workday(uid):
    locations = _location_by_uid_stop_workday(uid)
    return make_response(dumps(generate_matrix(locations)))


@app.route("/most_proba_locations/<uid>")
def most_proba_locations(uid):
    locations = _location_by_uid_stop(uid)
    matrix = generate_matrix(locations)
    most_proba_locations = pretty_print_most_proba_locations(get_most_proba_locations(matrix))
    return make_response(dumps(most_proba_locations))


@app.route("/most_proba_locations_workday/<uid>")
def most_proba_locations_workday(uid):
    locations = _location_by_uid_stop_workday(uid)
    matrix = generate_matrix(locations)
    most_proba_locations = pretty_print_most_proba_locations(get_most_proba_locations(matrix))
    return make_response(dumps(most_proba_locations))


@app.route("/most_proba_locations_holiday/<uid>")
def most_proba_locations_holiday(uid):
    locations = _location_by_uid_stop_holiday(uid)
    matrix = generate_matrix(locations)
    most_proba_locations = pretty_print_most_proba_locations(get_most_proba_locations(matrix))
    return make_response(dumps(most_proba_locations))


def _stop_to_seq(locations):
    seqs = []
    for day in locations:
        seq = [stop['location'] for stop in day['locations']]
        if len(seq) > 0:
            seqs.append(seq)
    return seqs


@app.route("/freq_seq/<uid>")
def freq_seq(uid):
    locations = _location_by_uid_stop(uid)
    dataset = _stop_to_seq(locations)
    L, supportData = freq_seq_mining(dataset, 4)
    flattenL = []
    for ck in L:
        flattenL += ck
    flattenL = [seq for seq in flattenL if len(seq) > 1]
    return make_response(dumps(flattenL))


@app.route("/web_req_histgram/<uid>")
def web_req_histgram(uid):
    cols = ['hour', 'count']
    db.ping(True)
    cursor = db.cursor()
    prepare_sql = """select cast(substring(minute, 3, 2) as SIGNED) as hour, count(distinct minute) as count
                        from app_domain_logs where uid = %s and dirty is NULL group by hour"""

    cursor.execute(prepare_sql, (uid,))
    rows = cursor.fetchall()
    results = [dict(zip(cols, row)) for row in rows]
    return make_response(dumps(results))


@app.route("/site_count/<uid>")
def site_count(uid):
    cols = ['site_name', 'count']
    db.ping(True)
    cursor = db.cursor()
    prepare_sql = """select site_name, count(1) as count from app_domain_logs
                        where uid = %s group by site_name
                        order by count desc limit 10"""

    cursor.execute(prepare_sql, (uid,))
    rows = cursor.fetchall()
    results = [dict(zip(cols, row)) for row in rows]
    return make_response(dumps(results))


@app.route("/app_count/<uid>")
def app_count(uid):
    cols = ['app_name', 'count']
    db.ping(True)
    cursor = db.cursor()
    prepare_sql = """select app_name, count(1) as count from app_domain_logs
                        where uid = %s group by app_name
                        order by count desc limit 10"""

    cursor.execute(prepare_sql, (uid,))
    rows = cursor.fetchall()
    results = [dict(zip(cols, row)) for row in rows]
    return make_response(dumps(results))


@app.route("/call_histgram/<uid>")
def call_histgram(uid):
    cols = ['hour', 'count']
    db.ping(True)
    cursor = db.cursor()
    prepare_sql = """select hour(start_time) as hour, count(1) as count
                        from calls where uid = %s group by hour"""

    cursor.execute(prepare_sql, (uid,))
    rows = cursor.fetchall()
    results = [dict(zip(cols, row)) for row in rows]
    return make_response(dumps(results))


def fetch_semantic_data(locations):
    cols = ['location', 'station_desc', 'tags', 'addr', 'business']
    cursor = db.cursor()
    prepare_sql = """select location, station_desc, tags, addr, business from semantic4 where location in (%s)""" % \
        ','.join(map(lambda x: "'" + x + "'", locations))
    cursor.execute(prepare_sql)
    rows = cursor.fetchall()
    return [dict(zip(cols, row)) for row in rows]


@app.route("/semantic_data/<uid>")
def semantic_data(uid):
    locations = _location_by_uid_stop(uid)
    locationlist = set()
    for day in locations:
        for item in day['locations']:
            locationlist.add(item['location'])
    results = fetch_semantic_data(locationlist)
    return make_response(dumps(list(results)))


@app.route("/user_status_proba/<uid>")
def user_status_proba(uid):
    logs = fetch_uid_location_data(uid)
    results = merge_locations(logs)
    get_delta(results)
    moves = get_moves(results)
    stops = get_stop(results)
    return make_response(dumps(generate_status_matrix(moves, stops)))


@app.route("/user_status/<uid>")
def user_status(uid):
    logs = fetch_uid_location_data(uid)
    results = merge_locations(logs)
    get_delta(results)
    moves = get_moves(results)
    stops = get_stop(results)
    return make_response(dumps(get_status(moves, stops)))


def fetch_uid_app_data(uid):
    cols = ['day', 'minute', 'entity']
    db.ping(True)
    cursor = db.cursor()
    prepare_sql = """select day, concat('201312', minute) as start_time,
                        app_name
                        from app_domain_logs
                        where uid = %s and app_name != '其他' and
                              site_channel_name not like %s
                              and dirty is NULL
                        order by day, minute"""
    cursor.execute(prepare_sql, (uid, '被动%'))
    rows = cursor.fetchall()
    return [dict(zip(cols, row)) for row in rows]


def fetch_uid_app_data_with_condition(uid, condition=''):
    cols = ['day', 'minute', 'entity']
    db.ping(True)
    cursor = db.cursor()
    prepare_sql = """select day, concat('201312', minute) as start_time,
                        app_name
                        from app_domain_logs
                        where uid = %s and app_name != '其他' and
                              site_channel_name not like %s and
                              app_name != '微信' and
                              app_name != '手机腾讯网' and
                              app_name != 'QQ' and
                              dirty is NULL
                        order by day, minute"""
    cursor.execute(prepare_sql, (uid, '被动%'))
    rows = cursor.fetchall()
    return [dict(zip(cols, row)) for row in rows]


def fetch_uid_app_type_data(uid):
    cols = ['day', 'minute', 'entity']
    db.ping(True)
    cursor = db.cursor()
    prepare_sql = """select day, concat('201312', minute) as start_time,
                        app_type_name
                        from app_domain_logs
                        where uid = %s and app_name != '其他' and
                              site_channel_name not like %s
                              and dirty is NULL
                              and app_type_name in ('旅游', '游戏', '电商购物', '社交沟通', '社区论坛', '网页浏览', '视频', '邮箱', '阅读', '音乐')
                        order by day, minute"""
    cursor.execute(prepare_sql, (uid, '被动%'))
    rows = cursor.fetchall()
    return [dict(zip(cols, row)) for row in rows]


def fetch_uid_app_type_data_with_condition(uid, condition=''):
    cols = ['day', 'minute', 'entity']
    db.ping(True)
    cursor = db.cursor()
    prepare_sql = """select day, concat('201312', minute) as start_time,
                        app_type_name
                        from app_domain_logs
                        where uid = %s and app_name != '其他' and
                              site_channel_name not like %s and
                              app_type_name in ('旅游', '游戏', '电商购物', '社区论坛', '网页浏览', '视频', '邮箱', '阅读', '音乐') and
                              dirty is NULL
                        order by day, minute"""
    cursor.execute(prepare_sql, (uid, '被动%'))
    rows = cursor.fetchall()
    return [dict(zip(cols, row)) for row in rows]


@app.route("/app_by_uid/<uid>")
def app_by_uid(uid):
    results = fetch_uid_app_data(uid)
    return make_response(dumps(active_matrix(results)))


@app.route("/app_type_by_uid/<uid>")
def app_type_by_uid(uid):
    results = fetch_uid_app_type_data(uid)
    return make_response(dumps(active_matrix(results)))


@app.route("/app_by_uid_with_condition/<uid>")
def app_by_uid_condition(uid):
    results = fetch_uid_app_data_with_condition(uid)
    return make_response(dumps(active_matrix(results)))


@app.route("/app_type_by_uid_with_condition/<uid>")
def app_type_by_uid_condition(uid):
    results = fetch_uid_app_type_data_with_condition(uid)
    return make_response(dumps(active_matrix(results)))

if __name__ == "__main__":
    app.run(debug=True)
