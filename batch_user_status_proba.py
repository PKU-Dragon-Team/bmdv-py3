#!/usr/bin/env python
# encoding: utf-8

from csv import DictWriter
import json
from db import MySQL as DB
from batch_common import dbconfig
from batch_common import fetch_users
from batch_common import fetch_user_location_logs

from merge_locations import merge_locations
from get_stop import get_stop, get_delta
from get_move import get_moves
from move_stop_probability_matrix import generate_status_matrix


def run(outputfile):
    cols = ['uid', 'data']
    f = open(outputfile, 'w')
    writer = DictWriter(f, cols)
    writer.writeheader()
    db = DB(dbconfig)

    for uid in fetch_users(db):
        logs = fetch_user_location_logs(uid, db)
        results = merge_locations(logs)
        get_delta(results)
        moves = get_moves(results)
        stops = get_stop(results)
        user_status = generate_status_matrix(moves, stops)
        writer.writerow({
            'uid': uid,
            'data': json.dumps(user_status)
        })


if __name__ == '__main__':
    import sys
    run(sys.argv[1])
